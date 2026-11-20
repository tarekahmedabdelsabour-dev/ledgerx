import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import importlib.util

spec = importlib.util.spec_from_file_location("ean", os.path.join(os.path.dirname(__file__), "..", "ean.py"))
ean = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ean)


class Ean(unittest.TestCase):
	def test_known_valid_codes(self):
		for c in ("4006381333931", "5901234123457", "9780201379624", "0012345678905"):
			self.assertTrue(ean.is_valid(c), c)
			self.assertEqual(ean.check_digit(c[:12]), c[-1])

	def test_invalid_codes(self):
		for c in ("4006381333932", "123", "abcdefghijklm", "", None, "40063813339311"):
			self.assertFalse(ean.is_valid(c))

	def test_make_is_valid_prefixed_and_unique(self):
		codes = [ean.make(i) for i in range(1, 2001)]
		self.assertEqual(len(set(codes)), 2000)
		for c in codes:
			self.assertTrue(ean.is_valid(c))
			self.assertTrue(c.startswith("2"))
			self.assertEqual(len(c), 13)

	def test_sequence_round_trip(self):
		for s in (1, 42, 99999, ean.MAX_SEQ):
			self.assertEqual(ean.sequence_of(ean.make(s)), s)
		self.assertIsNone(ean.sequence_of("4006381333931"))  # valid but not ours
		self.assertIsNone(ean.sequence_of("2000000000001"))  # wrong check digit

	def test_next_sequence_ignores_foreign_codes(self):
		self.assertEqual(ean.next_sequence([]), 1)
		self.assertEqual(ean.next_sequence(["4006381333931", ean.make(7), ean.make(3), "junk"]), 8)

	def test_bounds(self):
		for bad in (0, -1, ean.MAX_SEQ + 1):
			with self.assertRaises(ValueError):
				ean.make(bad)

	def test_single_digit_error_always_detected(self):
		code = ean.make(123456)
		for i in range(13):
			for d in "0123456789":
				if d != code[i]:
					self.assertFalse(ean.is_valid(code[:i] + d + code[i + 1:]))


if __name__ == "__main__":
	unittest.main()
