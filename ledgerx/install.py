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
}


PRINT_STYLE = "LedgerX"
BASE_PRINT_STYLE = "Redesign"  # Frappe's default; LedgerX = a copy of it + the watermark


def after_install():
	apply_branding()
	apply_print_style()


def after_migrate():
	apply_branding()
	apply_print_style()


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
