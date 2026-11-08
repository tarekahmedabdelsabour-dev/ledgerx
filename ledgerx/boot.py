"""Rebrand ERPNext's entry in the desk's app list as LedgerX.

Frappe v16 draws the sidebar header logo, the sidebar subtitle and the tiles on the home screen
from `frappe.boot.app_data`. ERPNext declares its own title and logo for that list, so without
this hook the ERPNext "E" icon and name stay visible even though LedgerX is installed.

The hook runs after `app_data` is built (see frappe/boot.py: load_desktop_data runs before the
boot_session hooks), and only changes what is displayed - routes, permissions and the dock of the
app are left exactly as ERPNext defines them, so ERPNext updates keep working.
"""

BRAND = "LedgerX"
MARK = "/assets/ledgerx/images/ledgerx-mark.svg"

# Apps whose displayed name/logo are replaced by LedgerX's.
REBRANDED_APPS = ("erpnext",)


def extend_bootinfo(bootinfo):
	for app in bootinfo.get("app_data") or []:
		if app.get("app_name") in REBRANDED_APPS:
			app["app_title"] = BRAND
			app["app_logo_url"] = MARK
