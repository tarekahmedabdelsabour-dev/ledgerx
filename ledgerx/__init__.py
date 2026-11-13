__version__ = "1.8.0"


def _enable_excel():
	# Every CSV reader in the system also reads .xlsx (see excel_compat.py). Must never block start-up.
	try:
		from ledgerx import excel_compat

		excel_compat.patch()
	except Exception:
		pass


_enable_excel()
