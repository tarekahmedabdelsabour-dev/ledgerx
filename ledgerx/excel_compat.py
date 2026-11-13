"""Let every CSV reader in the system also read an Excel (.xlsx) file.

ERPNext and Frappe have a handful of places that only understand CSV (Rename Tool, serial / batch
import, BOM import, ...). They all call `frappe.utils.csvutils.read_csv_content`. That function is
wrapped here: if the bytes it receives are an .xlsx workbook, the first sheet is read instead.
CSV input goes through the original function untouched.
"""
import sys

from ledgerx import excel_core

_MARK = "_ledgerx_excel_aware"


def _wrap(original):
	def read_csv_content(fcontent, *args, **kwargs):
		if excel_core.is_xlsx(fcontent):
			try:
				from frappe.utils import formatdate

				return excel_core.xlsx_to_rows(fcontent, fmt_date=formatdate)
			except Exception:
				pass  # fall through: let the original report the problem
		return original(fcontent, *args, **kwargs)

	setattr(read_csv_content, _MARK, True)
	read_csv_content.__wrapped__ = original
	return read_csv_content


def patch():
	"""Idempotent. Also re-points modules that already imported the function by name."""
	try:
		from frappe.utils import csvutils
	except Exception:
		return
	current = getattr(csvutils, "read_csv_content", None)
	if current is None:
		return
	if not getattr(current, _MARK, False):
		wrapped = _wrap(current)
		original = current
		csvutils.read_csv_content = wrapped
	else:
		wrapped, original = current, current.__wrapped__
	for mod in list(sys.modules.values()):
		try:
			if getattr(mod, "read_csv_content", None) is original and mod is not csvutils:
				mod.read_csv_content = wrapped
		except Exception:
			continue
