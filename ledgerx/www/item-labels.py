import frappe
from frappe import _

from ledgerx.barcodes import _item_group_names, label_rows

no_cache = 1
sitemap = 0

SIZES = {"62x38": (62, 38), "50x30": (50, 30), "40x25": (40, 25), "a4": (70, 37)}


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/item-labels"
		raise frappe.Redirect
	form = frappe.form_dict
	names = [n for n in (form.get("items") or "").split(",") if n]
	group = form.get("item_group")
	if group and not names:
		groups = _item_group_names(group)
		names = frappe.get_all("Item", filters={"disabled": 0, "is_sales_item": 1, "has_variants": 0, "item_group": ["in", groups]}, pluck="name", limit_page_length=500, order_by="name")
	names = names[:500]
	size = form.get("size") if form.get("size") in SIZES else "62x38"
	copies = int(form.get("copies") or 1)
	rows, no_barcode, price_list = label_rows(names, form.get("price_list"), copies)
	context.labels = rows[:2000]
	context.no_barcode = no_barcode
	context.price_list = price_list or ""
	context.show_price = 0 if form.get("price") == "0" else 1
	context.size = size
	context.w, context.h = SIZES[size]
	context.a4 = size == "a4"
	context.truncated = len(rows) > 2000
	context.currency = frappe.db.get_default("currency") or ""
	context.no_header = 1
	context.show_sidebar = 0
	context.title = _("Item Barcode Labels")
