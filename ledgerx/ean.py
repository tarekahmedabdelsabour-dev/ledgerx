"""EAN-13 helpers for in-store item barcodes. No database access, so it is unit-tested.

Codes starting with 2 belong to the range GS1 reserves for numbers a shop prints itself, so they never clash with a
manufacturer's barcode. Layout: "2" + 11-digit running number + check digit.
"""
PREFIX = "2"
MAX_SEQ = 10 ** 11 - 1


def check_digit(first12):
	"""EAN-13 check digit of the first 12 digits (weights 1, 3, 1, 3, ...)."""
	if len(first12) != 12 or not first12.isdigit():
		raise ValueError("12 digits expected")
	total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(first12))
	return str((10 - total % 10) % 10)


def is_valid(code):
	code = str(code or "")
	return len(code) == 13 and code.isdigit() and code[-1] == check_digit(code[:12])


def make(seq):
	"""The internal EAN-13 for running number `seq` (1 ... 99,999,999,999)."""
	if not 0 < int(seq) <= MAX_SEQ:
		raise ValueError("sequence out of range")
	body = PREFIX + str(int(seq)).zfill(11)
	return body + check_digit(body)


def sequence_of(code):
	"""Running number of an internal code, or None when the code is not one of ours."""
	code = str(code or "")
	if is_valid(code) and code.startswith(PREFIX):
		return int(code[1:12])
	return None


def next_sequence(existing_codes):
	"""One above the highest internal running number already used (1 when there is none)."""
	used = [s for s in (sequence_of(c) for c in existing_codes) if s is not None]
	return (max(used) + 1) if used else 1
