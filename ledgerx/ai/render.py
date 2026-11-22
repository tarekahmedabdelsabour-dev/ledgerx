"""Excel file for a table the assistant showed. Pure apart from openpyxl."""
import io

import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

MAX_SHEET_NAME = 31


def safe_cell(v):
	"""A text cell that starts like a formula is stored as text, so a value can never run in Excel."""
	if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
		return "'" + v
	return v


def xlsx_bytes(columns, rows, title="Report"):
	wb = openpyxl.Workbook()
	ws = wb.active
	bad = set('[]:*?/\\')
	ws.title = ("".join(c for c in (title or "Report") if c not in bad).strip() or "Report")[:MAX_SHEET_NAME]
	ws.append([safe_cell(str(c)) for c in columns])
	for c in ws[1]:
		c.font = Font(bold=True)
	for r in rows:
		ws.append([safe_cell(v) for v in r])
	for i, col in enumerate(columns, 1):
		width = max([len(str(col))] + [len(str(r[i - 1])) for r in rows[:200] if i - 1 < len(r) and r[i - 1] is not None])
		ws.column_dimensions[get_column_letter(i)].width = min(max(10, width + 2), 50)
	ws.freeze_panes = "A2"
	ws.sheet_view.rightToLeft = False
	buf = io.BytesIO()
	wb.save(buf)
	return buf.getvalue()
