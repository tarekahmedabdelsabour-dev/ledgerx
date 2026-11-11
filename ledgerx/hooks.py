from ledgerx import __version__ as app_version

app_name = "ledgerx"
app_title = "LedgerX"
app_publisher = "LedgerX"
app_description = "LedgerX - branding and interface layer"
app_email = "hello@ledgerx.local"
app_license = "mit"
app_icon = "fa fa-book"
app_color = "#0F766E"

# LedgerX sits on top of ERPNext: install erpnext first, then this app.
required_apps = ["erpnext"]

# Logo used by the desk (apps screen, sidebar header) and as the fallback brand logo.
app_logo_url = "/assets/ledgerx/images/ledgerx-logo.svg"

# LedgerX has no apps-screen tile of its own on purpose: ERPNext's tile is shown as LedgerX
# instead (name + logo), see ledgerx/boot.py. A second tile would open the same screen.
boot_session = "ledgerx.boot.extend_bootinfo"

# Desk (the logged-in interface). Plain files from public/ are served from /assets/ledgerx/,
# so no `bench build` is needed for CSS/JS edits - just hard-refresh the browser.
# These load after Frappe's and ERPNext's own bundles, so they win on equal specificity.
#
# Frappe links plain (non-bundle) files without a version, so a browser may keep serving an old
# copy after an update. The ?v= suffix is the app version: bump it in ledgerx/__init__.py with
# every release and every browser fetches the new file on its own.
app_include_css = f"/assets/ledgerx/css/ledgerx.css?v={app_version}"
app_include_js = f"/assets/ledgerx/js/ledgerx.js?v={app_version}"

# Website, login page, web forms and portal.
web_include_css = f"/assets/ledgerx/css/ledgerx_web.css?v={app_version}"

# Branding on the login page / website. Later apps override earlier ones for the same key,
# so these replace the values ERPNext declares in its own hooks.
website_context = {
	"favicon": "/assets/ledgerx/images/ledgerx-favicon.svg",
	"splash_image": "/assets/ledgerx/images/ledgerx-logo.svg",
}

# Apply the branding records (Website Settings, Navbar Settings, System Settings)
# once on install and again after every migrate, so the settings can never drift back.
after_install = "ledgerx.install.after_install"
after_migrate = "ledgerx.install.after_migrate"

# No explanation videos anywhere: ERPNext's own Video doctypes are closed for every user.
# (Onboarding video links are emptied in install.remove_videos; the player is switched off in ledgerx.js.)
has_permission = {
	"Video": "ledgerx.permissions.deny",
	"Video Settings": "ledgerx.permissions.deny",
}

# The CRM app (/crm) is a separate single-page app, so its branding is injected into its HTML response.
after_request = [
	"ledgerx.crm_branding.after_request",
	"ledgerx.html_branding.after_request",
]
