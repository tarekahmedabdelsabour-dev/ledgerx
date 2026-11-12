"""Put the LedgerX identity on every app shown in the desk - installed now or added later.

Frappe v16 draws the sidebar header logo, the sidebar subtitle and the tiles on the home screen
from `frappe.boot.app_data`, one entry per installed app, each with the title and logo that app
declares for itself (ERPNext's "E", HRMS's own mark, ...). This hook runs after `app_data` is built
(frappe/boot.py: load_desktop_data runs before the boot_session hooks) and rewrites what is
*displayed*. Routes, permissions and each app's dock are untouched, so app updates keep working.

Nothing here lists apps one by one: any app installed later gets the LedgerX logo automatically.
"""

BRAND = "LedgerX"
MARK = "/assets/ledgerx/images/ledgerx-mark.svg"

# Apps whose displayed *name* is replaced. ERPNext is the product the customer sees as LedgerX; HRMS
# becomes "LedgerX HR" (shown as "الموارد البشرية" in Arabic) and Lending "LedgerX Lending" ("الإقراض والتمويل"), see translations/ar.csv. Other apps
# (Framework, CRM, ...) keep their own names so the tiles stay distinguishable.
RENAMED_APPS = {"erpnext": BRAND, "hrms": f"{BRAND} HR", "lending": f"{BRAND} Lending"}

# Apps that keep their own logo. Empty = every app gets the LedgerX mark.
# Example: KEEP_LOGO_APPS = ("frappe",) leaves the Framework tile with its generic icon.
KEEP_LOGO_APPS = ()


def extend_bootinfo(bootinfo):
	for app in bootinfo.get("app_data") or []:
		name = app.get("app_name")

		if name in RENAMED_APPS:
			app["app_title"] = RENAMED_APPS[name]

		if name not in KEEP_LOGO_APPS:
			app["app_logo_url"] = MARK
