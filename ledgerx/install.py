"""Apply LedgerX branding to the single-doctype settings that control the visible identity.

Runs after install and after every migrate. It is idempotent and only writes fields that
actually exist on the installed Frappe version, so it is safe across minor Frappe changes.
"""

import frappe

LOGO = "/assets/ledgerx/images/ledgerx-logo.svg"
MARK = "/assets/ledgerx/images/ledgerx-mark.svg"
FAVICON = "/assets/ledgerx/images/ledgerx-favicon.svg"

BRANDING = {
	"Website Settings": {
		"app_name": "LedgerX",
		"app_logo": LOGO,
		"splash_image": LOGO,
		"favicon": FAVICON,
		"title_prefix": "LedgerX",
		"footer_powered": "",
		"copyright": "LedgerX",
		"show_language_picker": 1,  # Arabic / English switch on the login page
	},
	"Navbar Settings": {
		"app_logo": MARK,
	},
	# ERPNext writes its own name here on install ("Login to ERPNext", e-mail subjects...) and ships a
	# "Sent via ERPNext" footer for every outgoing e-mail.
	"System Settings": {
		"app_name": "LedgerX",
		"disable_standard_email_footer": 1,
	},
}


PRINT_STYLE = "LedgerX"
BASE_PRINT_STYLE = "Redesign"  # Frappe's default; LedgerX = a copy of it + the watermark


def after_install():
	apply_branding()
	ensure_help_menu()
	ensure_employee_documents()
	apply_print_style()
	remove_videos()


def after_migrate():
	apply_translation_overrides()
	apply_branding()
	ensure_help_menu()
	ensure_employee_documents()
	apply_print_style()
	remove_videos()


EMPLOYEE_DOC_TYPES = [
	# (name, required, has_expiry)
	("شهادة الميلاد", 1, 0),
	("بطاقة الرقم القومي", 1, 1),
	("المؤهل الدراسي", 1, 0),
	("موقف الخدمة العسكرية", 0, 0),
	("صحيفة الحالة الجنائية", 0, 1),
	("عقد العمل", 1, 0),
	("شهادة الخبرة", 0, 0),
	("الشهادة الصحية", 0, 1),
	("جواز السفر", 0, 1),
	("رخصة القيادة", 0, 1),
	("التأمينات الاجتماعية", 0, 0),
	("صور شخصية", 0, 0),
	("مستند آخر", 0, 0),
]


def ensure_employee_documents():
	"""Employee file: a Documents tab (birth certificate, qualification, military status...) on Employee.

	The employee photo is Employee's own image field (click the picture at the top of the form).
	"""
	try:
		if not frappe.db.exists("DocType", "Employee File"):
			return
		for name, required, has_expiry in EMPLOYEE_DOC_TYPES:
			if not frappe.db.exists("Employee Document Type", name):
				frappe.get_doc(
					{"doctype": "Employee Document Type", "type_name": name, "required": required, "has_expiry": has_expiry}
				).insert(ignore_permissions=True)

		meta = frappe.get_meta("Employee")
		if meta.has_field("lx_documents"):
			return
		last = [d.fieldname for d in meta.fields if d.fieldname][-1]
		for i, field in enumerate(
			[
				{"fieldname": "lx_documents_tab", "fieldtype": "Tab Break", "label": "Employee Documents"},
				{"fieldname": "lx_documents", "fieldtype": "Table", "label": "Documents", "options": "Employee File"},
			]
		):
			frappe.get_doc(
				{"doctype": "Custom Field", "dt": "Employee", "insert_after": last, **field}
			).insert(ignore_permissions=True)
			last = field["fieldname"]
		frappe.clear_cache(doctype="Employee")
	except Exception:
		frappe.log_error(title="LedgerX: employee documents")


DOCS_ITEM = "LedgerX Docs"


def ensure_help_menu():
	"""Help menu: LedgerX documentation first, the external standard links hidden."""
	try:
		ns = frappe.get_doc("Navbar Settings")
		changed = False
		found = None
		for row in ns.help_dropdown or []:
			if row.item_label == DOCS_ITEM:
				found = row
			elif not row.hidden and (row.route or "").startswith("http"):
				row.hidden = 1
				changed = True
		if not found:
			ns.append(
				"help_dropdown",
				{"item_label": DOCS_ITEM, "item_type": "Route", "route": "/docs", "is_standard": 0, "hidden": 0},
			)
			changed = True
		elif found.route != "/docs" or found.hidden:
			found.route, found.hidden = "/docs", 0
			changed = True
		if changed:
			ns.flags.ignore_permissions = True
			ns.save()
	except Exception:
		frappe.log_error(title="LedgerX: help menu")


def apply_translation_overrides():
	try:
		from ledgerx.translation_overrides import apply

		apply()
	except Exception:
		frappe.log_error(title="LedgerX: translation overrides")


def apply_branding():
	for doctype, values in BRANDING.items():
		try:
			meta = frappe.get_meta(doctype)
			for fieldname, value in values.items():
				if meta.has_field(fieldname):
					frappe.db.set_single_value(doctype, fieldname, value)
		except Exception:
			# Branding must never block an install or a migrate.
			frappe.log_error(title=f"LedgerX: could not apply branding to {doctype}")

	frappe.clear_cache()


def apply_print_style():
	"""Create/refresh the "LedgerX" Print Style: Frappe's default style plus the watermark.

	The record is rebuilt from public/css/ledgerx_print.css on every migrate, so editing that
	file and migrating is enough. It becomes the active style only if the site is still on the
	default one - a style the user picked on purpose is never overwritten.
	"""
	try:
		path = frappe.get_app_path("ledgerx", "public", "css", "ledgerx_print.css")
		with open(path, encoding="utf-8") as f:
			watermark_css = f.read()

		base_css = frappe.db.get_value("Print Style", BASE_PRINT_STYLE, "css") or ""
		css = f"{base_css}\n\n{watermark_css}"

		if frappe.db.exists("Print Style", PRINT_STYLE):
			doc = frappe.get_doc("Print Style", PRINT_STYLE)
			doc.css = css
			doc.disabled = 0
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc(
				{
					"doctype": "Print Style",
					"print_style_name": PRINT_STYLE,
					"css": css,
					"standard": 0,
					"disabled": 0,
				}
			).insert(ignore_permissions=True)

		current = frappe.db.get_single_value("Print Settings", "print_style")
		if current in (None, "", BASE_PRINT_STYLE):
			frappe.db.set_single_value("Print Settings", "print_style", PRINT_STYLE)
	except Exception:
		# Never block an install or a migrate because of a cosmetic feature.
		frappe.log_error(title="LedgerX: could not apply the print watermark style")

	frappe.clear_cache()


VIDEO_COLUMNS = {"Onboarding Step": ("video_url", "intro_video_url")}


def remove_videos():
	"""No explanation videos anywhere: empty the video links that apps ship on their onboarding steps.

	Standard onboarding steps come back from the app's files whenever an app update touches them, so
	this runs on every migrate, not just once. The player itself, the list-view "Watch Video"
	help and the Video doctype are switched off separately (ledgerx.js, ledgerx.permissions).
	"""
	try:
		for doctype, fields in VIDEO_COLUMNS.items():
			meta = frappe.get_meta(doctype)
			for fieldname in fields:
				if meta.has_field(fieldname):
					frappe.db.sql(
						f"update `tab{doctype}` set `{fieldname}` = '' where ifnull(`{fieldname}`, '') != ''"
					)
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="LedgerX: could not remove onboarding videos")

	frappe.clear_cache()
