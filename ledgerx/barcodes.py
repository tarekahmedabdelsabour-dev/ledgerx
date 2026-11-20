"""Item barcodes for the shop: find the items that have none, give them an in-store EAN-13, and prepare label data."""
import frappe
from frappe import _
from frappe.utils import flt

from ledgerx import ean

MAX_PER_RUN = 1000


def _item_group_names(item_group):
	if not item_group:
		return None
	lft, rgt = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"]) or (None, None)
	if lft is None:
		frappe.throw(_("Item Group not found."))
	return frappe.get_all("Item Group", filters={"lft": [">=", lft], "rgt": ["<=", rgt]}, pluck="name")


def _missing(item_group=None, limit=None):
	groups = _item_group_names(item_group)
	cond, args = "", []
	if groups:
		cond = " and i.item_group in (" + ", ".join(["%s"] * len(groups)) + ")"
		args = list(groups)
	sql = (
		"select i.name from `tabItem` i where i.disabled = 0 and i.is_sales_item = 1 and ifnull(i.has_variants, 0) = 0"
		" and not exists (select 1 from `tabItem Barcode` b where b.parent = i.name and b.parenttype = 'Item' and ifnull(b.barcode, '') != '')"
		+ cond + " order by i.name" + (f" limit {int(limit)}" if limit else ""))
	return [r[0] for r in frappe.db.sql(sql, args)]


@frappe.whitelist()
def barcode_summary(item_group=None):
	frappe.has_permission("Item", "read", throw=True)
	groups = _item_group_names(item_group)
	flt_ = {"disabled": 0, "is_sales_item": 1, "has_variants": 0}
	if groups:
		flt_["item_group"] = ["in", groups]
	total = frappe.db.count("Item", flt_)
	missing = len(_missing(item_group))
	return {"total": total, "missing": missing}


@frappe.whitelist()
def generate_barcodes(item_group=None, limit=500, dry_run=1):
	"""Gives each sales item without a barcode a new in-store EAN-13. dry_run=1 only shows what would happen."""
	frappe.only_for(("Stock Manager", "System Manager"))
	limit = max(1, min(int(limit or MAX_PER_RUN), MAX_PER_RUN))
	names = _missing(item_group, limit)
	existing = [r[0] for r in frappe.db.sql("select barcode from `tabItem Barcode` where barcode like '2%%' and char_length(barcode) = 13")]
	seq = ean.next_sequence(existing)
	plan = []
	for n in names:
		plan.append((n, ean.make(seq)))
		seq += 1
	if int(dry_run):
		return {"dry_run": 1, "count": len(plan), "sample": [{"item": n, "barcode": c} for n, c in plan[:15]], "remaining": max(len(_missing(item_group)) - len(plan), 0)}
	done, failed = [], []
	for i, (n, code) in enumerate(plan, 1):
		try:
			if frappe.db.exists("Item Barcode", {"barcode": code}):
				failed.append({"item": n, "error": _("Barcode already exists")})
				continue
			doc = frappe.get_doc("Item", n)
			doc.append("barcodes", {"barcode": code, "barcode_type": "EAN"})
			doc.save()
			done.append({"item": n, "barcode": code})
		except Exception as e:
			frappe.db.rollback()
			failed.append({"item": n, "error": str(e)[:200]})
		if i % 50 == 0:
			frappe.db.commit()
	frappe.db.commit()
	return {"dry_run": 0, "count": len(done), "done": done[:50], "failed": failed[:50], "failed_count": len(failed), "remaining": len(_missing(item_group))}


def label_rows(names, price_list=None, copies=1):
	"""Label data: barcode (first Item Barcode, else the item code), name, code, price."""
	if not price_list:
		price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
	rows, no_barcode = [], 0
	for n in names:
		if not frappe.has_permission("Item", "read", n):
			continue
		d = frappe.db.get_value("Item", n, ["item_name", "stock_uom", "standard_rate"], as_dict=True)
		if not d:
			continue
		code = frappe.db.get_value("Item Barcode", {"parent": n, "parenttype": "Item"}, "barcode")
		if not code:
			no_barcode += 1
			code = n
		price = None
		if price_list:
			price = frappe.db.get_value("Item Price", {"item_code": n, "price_list": price_list, "selling": 1}, "price_list_rate", order_by="valid_from desc")
		if price is None:
			price = d.standard_rate
		for _i in range(max(1, min(int(copies or 1), 100))):
			rows.append({"code": code, "title": d.item_name or n, "sub": n, "price": flt(price) if price else None, "price_text": f"{flt(price):,.2f}" if price else "", "uom": d.stock_uom})
	return rows, no_barcode, price_list
