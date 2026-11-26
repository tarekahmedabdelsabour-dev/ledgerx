"""Small helpers shared by every LedgerX module app, so each app stops carrying its own copy.

Import from a module app as:  from ledgerx import shared

Nothing here changes what the apps do today: each helper is the same code the apps already repeat.
frappe is imported inside the functions that need it, so the pure helpers can be unit-tested without a site.
"""


def pct_ok(value, low=0.0, high=100.0):
	"""True when value is a number between low and high (inclusive)."""
	try:
		v = float(value or 0)
	except (TypeError, ValueError):
		return False
	return low <= v <= high


def require_pct(value, label, low=0.0, high=100.0):
	"""Throw unless the percentage is within range; returns it as a float."""
	import frappe
	from frappe import _

	if not pct_ok(value, low, high):
		frappe.throw(_("{0} must be between {1} and {2} percent").format(_(label), low, high))
	return float(value or 0)


def require_write(doc):
	"""The first line of every state-changing document action: the caller must be allowed to edit this document."""
	doc.check_permission("write")


def need_status(doc, *statuses, message=None):
	"""Read the stored status under a row lock and require it to be one of statuses.

	A second click, a retry or a forged client copy of the document cannot repeat a step that already happened.
	"""
	import frappe
	from frappe import _

	if not doc.is_new() and doc.name:
		stored = frappe.db.get_value(doc.doctype, doc.name, "status", for_update=True)
		if stored:
			doc.status = stored
	if doc.status not in statuses:
		frappe.throw((message or _("The document is {0}")).format(_(doc.status)))


def run_each(items, fn, title):
	"""Run fn(item) for every item, committing after each one.

	A failing item is rolled back and logged under `title` and does not stop the rest.
	Returns (done, failed) as two lists of items.
	"""
	import frappe

	done, failed = [], []
	for item in items:
		try:
			fn(item)
			frappe.db.commit()
			done.append(item)
		except Exception:
			frappe.db.rollback()
			frappe.log_error(title=f"{title}: {item}")
			failed.append(item)
	return done, failed


def doctype_clashes(names_by_app):
	"""{doctype: [apps]} for every DocType name declared by more than one app (DocType names are global)."""
	seen = {}
	for app, names in names_by_app.items():
		for n in names:
			seen.setdefault(n, []).append(app)
	return {n: sorted(a) for n, a in seen.items() if len(a) > 1}
