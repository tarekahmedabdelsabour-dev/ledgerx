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


def after_install():
	apply_branding()


def after_migrate():
	apply_branding()


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
