"""What the assistant may read and how values are cleaned before the model or the screen sees them. No framework imports."""
import datetime
import decimal
import re

NOT_PERMITTED = "NOT_PERMITTED"

# Credentials and secrets: never sent to the model, whatever the user's rights.
SENSITIVE_FIELD = re.compile(r"(pass(word|wd|phrase)|secret|token|api_?key|private_?key|hmac|credential|^otp|_otp$|csid)", re.I)

# Settings and logs that hold connections, keys or other people's questions.
BLOCKED_DOCTYPES = {
	"LedgerX AI Settings", "LedgerX AI Log", "Email Account", "Email Domain", "Social Login Key", "OAuth Client",
	"OAuth Bearer Token", "OAuth Authorization Code", "Token Cache", "Integration Request", "Webhook",
	"Webhook Request Log", "Document Share Key", "Access Log", "E-Invoice Connection", "Store Settings",
	"Paymob Settings", "Payment Gateway", "Connected App", "Google Settings", "Dropbox Settings", "S3 Backup Settings",
}

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
TAGS = re.compile(r"<[^>]+>")
OPS = {"=", "!=", ">", "<", ">=", "<=", "like", "not like", "in", "not in", "between", "is"}
FUNCS = {"SUM", "AVG", "COUNT", "MIN", "MAX"}
MAX_IN = 100


class Refused(Exception):
	"""The question is outside what this user may see (or what the assistant may touch)."""


def is_sensitive_field(fieldname, fieldtype=None):
	return fieldtype == "Password" or bool(SENSITIVE_FIELD.search(fieldname or ""))


def is_blocked_doctype(name):
	return name in BLOCKED_DOCTYPES or (name or "").startswith(("__", "OAuth "))


def valid_ident(name):
	return isinstance(name, str) and bool(IDENT.match(name))


def clean_value(value, max_len=300):
	"""One cell as plain JSON-safe data."""
	if value is None:
		return None
	if isinstance(value, bool):
		return int(value)
	if isinstance(value, decimal.Decimal):
		value = float(value)
	if isinstance(value, float):
		return round(value, 6)
	if isinstance(value, int):
		return value
	if isinstance(value, datetime.datetime):
		return value.strftime("%Y-%m-%d %H:%M:%S")
	if isinstance(value, (datetime.date, datetime.time)):
		return value.isoformat()
	if isinstance(value, datetime.timedelta):
		return str(value)
	if isinstance(value, (bytes, bytearray)):
		return ""
	text = TAGS.sub(" ", str(value))
	text = " ".join(text.split())
	return text if len(text) <= max_len else text[: max_len - 1] + "…"


def clean_rows(rows, columns, max_rows):
	"""(rows as lists in column order, truncated?)"""
	out = []
	for r in rows[:max_rows]:
		out.append([clean_value(r.get(c) if isinstance(r, dict) else r[i]) for i, c in enumerate(columns)])
	return out, len(rows) > max_rows


def norm_filters(filters):
	"""Filters from the model as [[field, op, value], ...]; anything else is refused instead of passed on."""
	if filters in (None, "", [], {}):
		return []
	if isinstance(filters, dict):
		filters = [[k, "=", v] for k, v in filters.items()]
	if not isinstance(filters, list):
		raise ValueError("filters must be a list of [field, operator, value]")
	out = []
	for f in filters:
		if not (isinstance(f, (list, tuple)) and len(f) == 3):
			raise ValueError("each filter must be [field, operator, value]")
		field, op, val = f
		op = str(op).strip().lower()
		if not valid_ident(field):
			raise ValueError(f"bad field name in filter: {field!r}")
		if op not in OPS:
			raise ValueError(f"operator not allowed: {op}")
		if op in ("in", "not in"):
			if not isinstance(val, list) or len(val) > MAX_IN:
				raise ValueError("'in' needs a list of at most %d values" % MAX_IN)
		elif op == "between":
			if not (isinstance(val, list) and len(val) == 2):
				raise ValueError("'between' needs [from, to]")
		elif op == "is":
			if val not in ("set", "not set"):
				raise ValueError("'is' needs 'set' or 'not set'")
		elif isinstance(val, (list, dict)):
			raise ValueError("value must be a single value")
		out.append([field, op, val])
	return out


def norm_order(order_by, allowed):
	"""'field desc' with the field taken from `allowed`; returns (field, descending)."""
	if not order_by:
		return None, False
	parts = str(order_by).split()
	field = parts[0]
	desc = len(parts) > 1 and parts[1].lower() == "desc"
	if len(parts) > 2 or (len(parts) == 2 and parts[1].lower() not in ("asc", "desc")) or field not in allowed:
		raise ValueError(f"cannot order by {order_by!r}")
	return field, desc


def has_arabic(text):
	return bool(re.search(r"[؀-ۿ]", text or ""))


DENIED = {
	"ar": "ده مش من صلاحياتك.",
	"en": "This is outside your permissions.",
}


def denied_text(lang):
	return DENIED["ar" if (lang or "ar").lower().startswith("ar") else "en"]
