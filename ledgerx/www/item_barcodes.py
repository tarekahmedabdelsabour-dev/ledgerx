import frappe
from frappe import _

no_cache = 1
sitemap = 0


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/item-barcodes"
		raise frappe.Redirect
	frappe.has_permission("Item", "read", throw=True)
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.can_generate = 1 if set(frappe.get_roles()) & {"Stock Manager", "System Manager"} else 0
	context.groups = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name", order_by="name", limit_page_length=500)
	context.price_lists = frappe.get_all("Price List", filters={"selling": 1, "enabled": 1}, pluck="name")
	context.no_header = 1
	context.show_sidebar = 0
	context.title = _("Item Barcodes")
