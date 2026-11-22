"""LedgerX Assistant endpoints. The assistant reads and explains only, always as the asking user."""
import base64
import os

import frappe
from frappe.utils import add_to_date, nowdate, now_datetime

from ledgerx.ai import client, engine, knowledge, prompt, render, safety
from ledgerx.ai.tools import Toolbox

SETTINGS = "LedgerX AI Settings"
MAX_QUESTION = 2000
PER_MINUTE = 20
DOCS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "docs")
_guide = {"mtimes": None, "obj": None}


def _lang():
	return "ar" if (frappe.local.lang or "ar").lower().startswith("ar") else "en"


def guide():
	"""The user guide shipped with the app, re-read only when its files change."""
	names = ("structure.js", "content_ar.js", "content_en.js")
	paths = [os.path.join(DOCS, n) for n in names]
	mt = tuple(os.path.getmtime(p) for p in paths)
	if _guide["mtimes"] != mt:
		texts = []
		for p in paths:
			with open(p, encoding="utf-8") as f:
				texts.append(f.read())
		_guide["obj"] = knowledge.Guide.from_files(*texts)
		_guide["mtimes"] = mt
	return _guide["obj"]


def _settings():
	return frappe.get_single(SETTINGS)


def _role_ok(s):
	return not s.allowed_role or s.allowed_role in frappe.get_roles()


def _used_today():
	return frappe.db.count("LedgerX AI Log", {"user": frappe.session.user, "creation": [">=", nowdate()]})


def _used_last_minute():
	return frappe.db.count("LedgerX AI Log", {"user": frappe.session.user, "creation": [">=", add_to_date(now_datetime(), minutes=-1)]})


@frappe.whitelist()
def status():
	"""Whether to show the assistant icon, and the user's quota."""
	if frappe.session.user in ("Guest", None):
		return {"enabled": False}
	s = _settings()
	key = s.get_password("api_key", raise_exception=False)
	ok = bool(s.enabled and key and _role_ok(s))
	limit = int(s.daily_limit or 0)
	out = {"enabled": ok, "lang": _lang()}
	if ok and limit:
		out["remaining"] = max(0, limit - _used_today())
	return out



def _log(question, answer, tools, usage, error=""):
	try:
		frappe.get_doc({
			"doctype": "LedgerX AI Log", "user": frappe.session.user, "question": (question or "")[:1000], "answer": answer or "",
			"tools_used": ", ".join(tools or [])[:140], "input_tokens": (usage or {}).get("input", 0), "output_tokens": (usage or {}).get("output", 0),
			"error": (error or "")[:500],
		}).insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="LedgerX AI log")


@frappe.whitelist(methods=["POST"])
def chat(message, history=None, context=None):
	lang = safety.has_arabic(message) and "ar" or _lang()
	s = _settings()
	key = s.get_password("api_key", raise_exception=False)
	if not (s.enabled and key) or not _role_ok(s):
		frappe.throw(engine.message("bad", lang), frappe.PermissionError)
	message = (message or "").strip()[:MAX_QUESTION]
	if not message:
		return {"answer": "", "blocks": []}
	limit = int(s.daily_limit or 0)
	if limit and _used_today() >= limit:
		return {"answer": "وصلت للحد اليومي من الأسئلة. جرّب بكرة." if lang == "ar" else "You have reached the daily question limit. Try again tomorrow.", "blocks": [], "limited": True}
	if _used_last_minute() >= PER_MINUTE:
		return {"answer": engine.message("busy", lang), "blocks": []}

	history = frappe.parse_json(history) if isinstance(history, str) else history
	context = frappe.parse_json(context) if isinstance(context, str) else (context or {})
	g = guide()
	tb = Toolbox(frappe.session.user, lang, g, max_rows=s.max_rows or 200)
	allowed = tb.allowed_pages()
	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
	currency = frappe.db.get_value("Company", company, "default_currency") if company else None
	system = prompt.build(nowdate(), frappe.session.user, frappe.utils.get_fullname(frappe.session.user), company, currency,
		(context or {}).get("route") if isinstance(context, dict) else None, g.toc(lang, allowed), s.instructions or "", lang)
	post = client.make_post(key)
	try:
		res = engine.run(post, tb, system, history, message, s.model or "claude-sonnet-5-5", int(s.max_tokens or 1500), lang)
	except engine.AIError as e:
		_log(message, "", tb.used, None, "%s %s" % (e.kind, e.detail))
		frappe.local.message_log = []
		return {"answer": engine.message(e.kind, lang), "blocks": [], "error": e.kind}
	except Exception:
		frappe.log_error(title="LedgerX AI chat")
		_log(message, "", tb.used, None, "unexpected")
		frappe.local.message_log = []
		return {"answer": engine.message("bad", lang), "blocks": [], "error": "bad"}
	blocks = tb.blocks()
	if tb.denied and not tb.data_ok:
		blocks = []
	frappe.cache.set_value("ledgerx_ai_datasets", {b["id"]: {"title": b["title"], "columns": b["columns"], "rows": b["rows"]} for b in blocks}, user=frappe.session.user, expires_in_sec=3600)
	_log(message, res["answer"], tb.used, res["usage"])
	frappe.local.message_log = []  # tool code may msgprint; it must not leak into this reply
	return {"answer": res["answer"], "blocks": blocks}


@frappe.whitelist()
def download(dataset):
	"""Excel file for a table shown in the last answer (kept for an hour, only for the user who asked)."""
	sets = frappe.cache.get_value("ledgerx_ai_datasets", user=frappe.session.user) or {}
	ds = sets.get(dataset)
	if not ds:
		frappe.throw(engine.message("bad", _lang()))
	data = render.xlsx_bytes(ds["columns"], ds["rows"], ds["title"])
	name = "".join(c if c.isalnum() or c in " -_" else "_" for c in ds["title"]).strip()[:60] or "report"
	return {"filename": name + ".xlsx", "data": base64.b64encode(data).decode()}
