"""Server side of LedgerX's Excel support (see public/js/ledgerx_excel.js and excel_compat.py)."""
import base64
import re

import frappe
from frappe import _
from frappe.utils import formatdate

from ledgerx import excel_core

MAX_BYTES = 15 * 1024 * 1024
MAX_ROWS = 100000
DATA_URL = re.compile(r"^data:[^;,]*(?:;[^;,]*)*;base64,(.+)$", re.S)


@frappe.whitelist()
def xlsx_to_csv_dataurl(dataurl):
	"""A chosen .xlsx workbook, returned as the CSV data URL the existing CSV import code expects."""
	m = DATA_URL.match(dataurl or "")
	if not m:
		frappe.throw(_("Invalid file"))
	content = base64.b64decode(m.group(1))
	if len(content) > MAX_BYTES:
		frappe.throw(_("The file is too large"))
	if not excel_core.is_xlsx(content):
		frappe.throw(_("Please choose an Excel (.xlsx) file"))
	rows = excel_core.xlsx_to_rows(content, fmt_date=formatdate)
	if len(rows) > MAX_ROWS:
		frappe.throw(_("Too many rows"))
	csv_text = excel_core.rows_to_csv(rows)
	return "data:text/csv;base64," + base64.b64encode(csv_text.encode("utf-8")).decode("ascii")


@frappe.whitelist(methods=["POST"])
def rows_to_xlsx(rows, sheet_name="Sheet1"):
	"""Rows of a table as a base64 .xlsx workbook."""
	rows = frappe.parse_json(rows)
	if not isinstance(rows, list) or len(rows) > MAX_ROWS:
		frappe.throw(_("Invalid data"))
	blob = excel_core.rows_to_xlsx([r if isinstance(r, list) else [r] for r in rows], sheet_name)
	return base64.b64encode(blob).decode("ascii")
