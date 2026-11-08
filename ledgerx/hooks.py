app_name = "ledgerx"
app_title = "LedgerX"
app_publisher = "LedgerX"
app_description = "LedgerX - custom branding and interface layer for ERPNext"
app_email = "hello@ledgerx.local"
app_license = "mit"
app_icon = "fa fa-book"
app_color = "#0F766E"

# LedgerX sits on top of ERPNext: install erpnext first, then this app.
required_apps = ["erpnext"]

# Logo used by the desk (apps screen, sidebar header) and as the fallback brand logo.
app_logo_url = "/assets/ledgerx/images/ledgerx-logo.svg"

add_to_apps_screen = [
	{
		"name": app_name,
		"logo": "/assets/ledgerx/images/ledgerx-mark.svg",
		"title": app_title,
		"route": "/desk/home",
		"sequence_id": 0,
	}
]

# Desk (the logged-in interface). Plain files from public/ are served from /assets/ledgerx/,
# so no `bench build` is needed for CSS/JS edits - just hard-refresh the browser.
# These load after Frappe's and ERPNext's own bundles, so they win on equal specificity.
app_include_css = "/assets/ledgerx/css/ledgerx.css"
app_include_js = "/assets/ledgerx/js/ledgerx.js"

# Website, login page, web forms and portal.
web_include_css = "/assets/ledgerx/css/ledgerx_web.css"

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
