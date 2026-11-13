import datetime
import unittest

from ledgerx import excel_core as X


class TestExcelCore(unittest.TestCase):
	def test_roundtrip(self):
		rows = [["Title"], [], ["name", "qty", "rate", "date"], ["A", 2, 10.5, datetime.date(2026, 3, 5)], ["ب", 3.0, None, "=x"]]
		blob = X.rows_to_xlsx(rows, "Bulk: Edit/Items?")
		self.assertTrue(X.is_xlsx(blob))
		back = X.xlsx_to_rows(blob, fmt_date=lambda d: d.strftime("%d-%m-%Y"))
		self.assertEqual(back[0], ["Title"])
		self.assertEqual(back[3], ["A", "2", "10.5", "05-03-2026"])
		self.assertEqual(back[4][0], "ب")
		self.assertEqual(back[4][1], "3")
		self.assertEqual(back[4][3], "=x")

	def test_csv_and_magic(self):
		self.assertFalse(X.is_xlsx(b"a,b\n1,2"))
		self.assertFalse(X.is_xlsx("PK\x03\x04"))
		self.assertEqual(X.rows_to_csv([["a", "b,c"], ["1", "2"]]), 'a,"b,c"\r\n1,2\r\n')
