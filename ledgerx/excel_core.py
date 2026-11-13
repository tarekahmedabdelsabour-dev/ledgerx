"""Spreadsheet helpers with no Frappe dependency (unit-tested on their own).

Excel and CSV are interchangeable everywhere in LedgerX: whatever accepts a CSV table also accepts an
.xlsx workbook, and whatever offers a CSV download also offers Excel.
"""
import csv
import datetime
import io

XLSX_MAGIC = b"PK\x03\x04"  # an .xlsx file is a zip archive


def is_xlsx(content):
	return isinstance(content, (bytes, bytearray)) and bytes(content[:4]) == XLSX_MAGIC


def _plain(value, fmt_date=None):
	"""One cell as the text a CSV would hold."""
	if value is None:
		return ""
	if isinstance(value, bool):
		return "1" if value else "0"
	if isinstance(value, datetime.datetime):
		if fmt_date and value.time() == datetime.time(0, 0):
			return fmt_date(value.date())
		return value.strftime("%Y-%m-%d %H:%M:%S") if value.time() != datetime.time(0, 0) else (
			fmt_date(value.date()) if fmt_date else value.strftime("%Y-%m-%d")
		)
	if isinstance(value, datetime.date):
		return fmt_date(value) if fmt_date else value.strftime("%Y-%m-%d")
	if isinstance(value, datetime.time):
		return value.strftime("%H:%M:%S")
	if isinstance(value, float) and value.is_integer():
		return str(int(value))
	return str(value)


def xlsx_to_rows(content, fmt_date=None):
	"""First worksheet of an .xlsx file as a list of rows of text (trailing empty cells trimmed)."""
	from openpyxl import load_workbook

	wb = load_workbook(io.BytesIO(bytes(content)), read_only=True, data_only=True)
	try:
		ws = wb.worksheets[0]
		rows = []
		for row in ws.iter_rows(values_only=True):
			cells = [_plain(v, fmt_date) for v in row]
			while cells and cells[-1] == "":
				cells.pop()
			rows.append(cells)
	finally:
		wb.close()
	while rows and not rows[-1]:
		rows.pop()
	return rows


def rows_to_xlsx(rows, sheet_name="Sheet1"):
	"""Rows (lists of values) as .xlsx bytes. Numbers stay numbers; everything else is text."""
	from openpyxl import Workbook

	wb = Workbook()
	ws = wb.active
	ws.title = (sheet_name or "Sheet1")[:31].translate({ord(c): " " for c in "[]:*?/\\"}) or "Sheet1"
	widths = {}
	for r_idx, row in enumerate(rows, start=1):
		for c_idx, value in enumerate(row, start=1):
			cell = ws.cell(row=r_idx, column=c_idx, value=value)
			if isinstance(value, str) and value[:1] == "=":
				cell.data_type = "s"  # text that looks like a formula stays text
			widths[c_idx] = min(max(widths.get(c_idx, 8), len(str(value)) + 2 if value is not None else 8), 50)
	for c_idx, w in widths.items():
		ws.column_dimensions[ws.cell(row=1, column=c_idx).column_letter].width = w
	out = io.BytesIO()
	wb.save(out)
	return out.getvalue()


def rows_to_csv(rows):
	out = io.StringIO()
	csv.writer(out, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n").writerows(rows)
	return out.getvalue()
