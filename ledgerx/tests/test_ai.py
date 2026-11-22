"""Tests for the assistant: the loop, the guide search, the safety rules and the tools under a stubbed framework."""
import json
import os
import sys
import types
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, ROOT)

from ledgerx.ai import client, engine, knowledge, prompt, render, safety  # noqa: E402

DOCS = os.path.join(ROOT, "ledgerx", "public", "docs")


def read(n):
	with open(os.path.join(DOCS, n), encoding="utf-8") as f:
		return f.read()


GUIDE = knowledge.Guide.from_files(read("structure.js"), read("content_ar.js"), read("content_en.js"))


class FakeTools:
	specs = []

	def __init__(self, replies=None, denied=0, data_ok=0):
		self.denied, self.data_ok, self.calls = denied, data_ok, []
		self.replies = replies or {}

	def call(self, name, args):
		self.calls.append((name, args))
		return self.replies.get(name, ({"ok": 1}, False))


def script(*responses):
	it = iter(responses)
	sent = []

	def post(payload):
		sent.append(json.loads(json.dumps(payload)))
		return next(it)

	post.sent = sent
	return post


def text(t, **u):
	return {"content": [{"type": "text", "text": t}], "stop_reason": "end_turn", "usage": {"input_tokens": 10, "output_tokens": 5, **u}}


def use(name, args, i="t1"):
	return {"content": [{"type": "text", "text": "x"}, {"type": "tool_use", "id": i, "name": name, "input": args}], "stop_reason": "tool_use", "usage": {"input_tokens": 20, "output_tokens": 7}}


class Engine(unittest.TestCase):
	def test_tool_loop_and_usage(self):
		tools = FakeTools()
		post = script(use("aggregate", {"a": 1}), text("done", cache_read_input_tokens=4))
		r = engine.run(post, tools, "sys", [], "q", "m", 100)
		self.assertEqual(r["answer"], "done")
		self.assertEqual(r["usage"], {"input": 30, "output": 12, "cache_read": 4})
		self.assertEqual(tools.calls, [("aggregate", {"a": 1})])
		second = post.sent[1]["messages"]
		self.assertEqual(second[-1]["content"][0]["type"], "tool_result")
		self.assertEqual(second[-1]["content"][0]["tool_use_id"], "t1")
		self.assertEqual(post.sent[0]["system"][0]["cache_control"], {"type": "ephemeral"})

	def test_error_flag_and_cut(self):
		tools = FakeTools({"q": ({"e": "x" * 20000}, True)})
		post = script(use("q", {}), text("ok"))
		engine.run(post, tools, "s", [], "q", "m", 10)
		res = post.sent[1]["messages"][-1]["content"][0]
		self.assertTrue(res["is_error"])
		self.assertLessEqual(len(res["content"]), engine.MAX_TOOL_RESULT + 20)

	def test_denial_overrides_the_model_text(self):
		tools = FakeTools({"query_records": ({"error": "NOT_PERMITTED"}, True)})
		tools.denied = 1
		post = script(use("query_records", {}), text("The salary of Ahmed is probably 5000"))
		r = engine.run(post, tools, "s", [], "مرتب أحمد كام؟", "m", 10, lang="ar")
		self.assertEqual(r["answer"], safety.DENIED["ar"])
		r = engine.run(script(text("x")), types.SimpleNamespace(denied=1, data_ok=0, specs=[], call=None), "s", [], "q", "m", 10, lang="en")
		self.assertEqual(r["answer"], safety.DENIED["en"])

	def test_denial_with_data_keeps_answer(self):
		t = types.SimpleNamespace(denied=1, data_ok=1, specs=[], call=None)
		self.assertEqual(engine.run(script(text("fine")), t, "s", [], "q", "m", 10)["answer"], "fine")

	def test_max_steps(self):
		post = script(*[use("a", {}, "t%d" % i) for i in range(10)])
		r = engine.run(post, FakeTools(), "s", [], "q", "m", 10, lang="en", max_steps=3)
		self.assertEqual(r["steps"], 3)
		self.assertEqual(len(post.sent), 3)

	def test_history_cleaning(self):
		h = [{"role": "assistant", "content": "a"}, {"role": "user", "content": "u1"}, {"role": "user", "content": "u2"},
			{"role": "assistant", "content": "r"}, {"role": "system", "content": "bad"}, {"role": "user", "content": ""}, "junk", {"role": "user", "content": "last"}]
		out = engine.clean_history(h)
		self.assertEqual(out[0]["role"], "user")
		self.assertEqual([m["role"] for m in out], ["user", "assistant"])
		self.assertEqual(out[0]["content"], "u1\nu2")

	def test_messages_are_localised(self):
		self.assertIn("المفتاح", engine.message("auth", "ar").replace("مفتاح", "المفتاح"))
		self.assertEqual(engine.message("nope", "en"), engine.MSG["en"]["bad"])


class Client(unittest.TestCase):
	def test_status_mapping(self):
		for code, kind in ((401, "auth"), (403, "auth"), (429, "busy"), (500, "down"), (529, "down"), (400, "bad")):
			self.assertEqual(client.kind_for_status(code), kind)

	def test_post_errors_never_hold_the_key(self):
		class R:
			status_code = 401
			text = "invalid"

		class S:
			def post(self, *a, **k):
				return R()

		try:
			client.make_post("sk-secret", session=S())({})
		except engine.AIError as e:
			self.assertEqual(e.kind, "auth")
			self.assertNotIn("sk-secret", e.detail + str(e))


class Safety(unittest.TestCase):
	def test_fields_and_doctypes(self):
		for f in ("password", "api_key", "secret_key", "access_token", "private_key", "hmac_secret", "otp_secret"):
			self.assertTrue(safety.is_sensitive_field(f), f)
		for f in ("grand_total", "customer", "posting_date", "status"):
			self.assertFalse(safety.is_sensitive_field(f), f)
		self.assertTrue(safety.is_blocked_doctype("LedgerX AI Log"))
		self.assertFalse(safety.is_blocked_doctype("Sales Invoice"))

	def test_filters(self):
		self.assertEqual(safety.norm_filters({"status": "Paid"}), [["status", "=", "Paid"]])
		for bad in ([["a; drop", "=", 1]], [["a", "union", 1]], [["a", "in", "x"]], [["a", "=", [1]]], "x", [["a", "="]], [["a", "is", "zzz"]]):
			with self.assertRaises(ValueError):
				safety.norm_filters(bad)

	def test_order(self):
		self.assertEqual(safety.norm_order("a desc", {"a"}), ("a", True))
		self.assertEqual(safety.norm_order(None, {"a"}), (None, False))
		for bad in ("b", "a; x", "a sideways", "a desc x"):
			with self.assertRaises(ValueError):
				safety.norm_order(bad, {"a"})

	def test_clean_value(self):
		self.assertEqual(safety.clean_value("<b>hi</b>  there"), "hi there")
		self.assertEqual(len(safety.clean_value("x" * 1000)), 300)
		rows, cut = safety.clean_rows([{"a": 1}, {"a": 2}, {"a": 3}], ["a"], 2)
		self.assertEqual((rows, cut), ([[1], [2]], True))


class Render(unittest.TestCase):
	def test_formula_cells_are_text(self):
		import io

		import openpyxl

		wb = openpyxl.load_workbook(io.BytesIO(render.xlsx_bytes(["a"], [["=SUM(A1)"], [5]], "x/y")))
		ws = wb.active
		self.assertEqual(ws["A2"].value, "'=SUM(A1)")
		self.assertEqual(ws["A3"].value, 5)
		self.assertEqual(ws.title, "xy")


class GuideSearch(unittest.TestCase):
	def test_structure_and_pages(self):
		self.assertIn("ai", GUIDE.titles)
		self.assertIn("store", GUIDE.titles)
		self.assertGreater(len(GUIDE.chunks("ar")), 100)

	def test_arabic_and_english_search(self):
		hits = GUIDE.search("إزاي أضيف منتج في المتجر", "ar")
		self.assertTrue(hits)
		self.assertTrue(GUIDE.search("how does the online store take payment", "en"))
		self.assertEqual(GUIDE.search("paymob", "en")[0]["page"], "store")

	def test_allowed_filter(self):
		hits = GUIDE.search("paymob", "en", allowed={"fleet"})
		self.assertFalse([h for h in hits if h["page"] == "store"])

	def test_toc_respects_allowed(self):
		toc = " ".join(GUIDE.toc("en", {"ai"}))
		self.assertIn("ai=", toc)
		self.assertNotIn("store=", toc)

	def test_page(self):
		p = GUIDE.page("ai", "en")
		self.assertIn("permissions", p["text"].lower())


class Prompt(unittest.TestCase):
	def test_build(self):
		s = prompt.build("2026-11-22", "a@b.c", "Ali", "ACME", "EGP", "/desk/sales-invoice", ["Sales: selling=Selling"], "Be short", "ar")
		for w in ("read-only", "NOT_PERMITTED", "ACME", "/desk/sales-invoice", "selling=Selling", "Be short"):
			self.assertIn(w, s)
		self.assertNotRegex(s.replace("Never use the words ERPNext or Frappe.", ""), r"ERPNext|Frappe")


# ---- tools under a stubbed framework ---------------------------------------------------------------------------


def make_frappe(roles=("Accounts User",), allow_modules=("Accounts",)):
	f = types.ModuleType("frappe")

	class PermissionError_(Exception):
		pass

	class Row(dict):
		__getattr__ = dict.get

	f.PermissionError = PermissionError_
	f.log = []
	f.log_error = lambda **k: f.log.append(k)
	f.get_roles = lambda u=None: list(roles)
	f.utils = types.SimpleNamespace(getdate=lambda v: __import__("datetime").date.fromisoformat(str(v)[:10]))
	f.permissions = types.SimpleNamespace(get_doctypes_with_read=lambda: ["Sales Invoice", "Employee"])
	f.get_user = lambda: types.SimpleNamespace(allow_modules=list(allow_modules))
	installed = {"DocType": {"Sales Invoice", "Employee", "LedgerX AI Log"}, "Module Def": {"Accounts", "Fleet Management", "Selling", "Store"}}
	f.db = types.SimpleNamespace(exists=lambda dt, name=None: name in installed.get(dt, set()) if name else dt in installed["DocType"])
	f.db.exists = lambda dt, name=None: (name in installed.get(dt, set())) if name is not None else (dt in installed["DocType"])
	f.has_permission = lambda dt, ptype="read", **k: dt in ("Sales Invoice",)

	class Meta:
		def __init__(self, name):
			self.name, self.title_field, self.is_submittable = name, "customer", 1
			D = types.SimpleNamespace
			self.fields = [D(fieldname="customer", label="Customer", fieldtype="Link", options="Customer", permlevel=0),
				D(fieldname="grand_total", label="Total", fieldtype="Currency", options=None, permlevel=0),
				D(fieldname="posting_date", label="Date", fieldtype="Date", options=None, permlevel=0),
				D(fieldname="cost", label="Cost", fieldtype="Currency", options=None, permlevel=1),
				D(fieldname="api_key", label="Key", fieldtype="Data", options=None, permlevel=0)]

		def get_permitted_fieldnames(self):
			return ["customer", "grand_total", "posting_date", "api_key"]

		def has_field(self, n):
			return n in [x.fieldname for x in self.fields]

		def get_table_fields(self):
			return []

	f.get_meta = Meta
	f.calls = []

	def get_list(dt, fields=None, filters=None, order_by=None, limit_page_length=20, group_by=None):
		f.calls.append({"fields": fields, "filters": filters, "order_by": order_by, "group_by": group_by})
		if fields and isinstance(fields[0], dict) and "COUNT" in fields[0] and not group_by:
			return [Row(n=3)]
		if group_by:
			return [Row(customer="A", value=10), Row(customer="B", value=30), Row(customer="C", value=20)]
		if fields and fields[0] == "posting_date":
			return [Row(posting_date="2026-01-05", grand_total=10), Row(posting_date="2026-01-20", grand_total=5), Row(posting_date="2026-02-01", grand_total=7)]
		return [Row(name="X1", customer="A", grand_total=5), Row(name="X2", customer="B", grand_total=6)]

	f.get_list = get_list
	f.get_all = lambda *a, **k: [Row(name="Sales Invoice", module="Accounts"), Row(name="Employee", module="HR")]
	return f


def load_tools(**kw):
	sys.modules["frappe"] = make_frappe(**kw)
	sys.modules.pop("ledgerx.ai.tools", None)
	import importlib

	return importlib.import_module("ledgerx.ai.tools"), sys.modules["frappe"]


class ToolboxTests(unittest.TestCase):
	def tearDown(self):
		sys.modules.pop("frappe", None)
		sys.modules.pop("ledgerx.ai.tools", None)

	def box(self, **kw):
		tools, f = load_tools(**kw)
		return tools.Toolbox("u@x", "en", GUIDE, max_rows=50), f

	def test_query_returns_rows_and_registers_dataset(self):
		tb, f = self.box()
		out, err = tb.call("query_records", {"doctype": "Sales Invoice", "fields": ["name", "customer"], "filters": [["customer", "=", "A"]], "order_by": "grand_total desc"})
		self.assertFalse(err)
		self.assertEqual(out["total_matching"], 3)
		self.assertEqual(out["rows"][0], ["X1", "A"])
		self.assertEqual(tb.datasets["d1"]["columns"], ["name", "customer"])
		self.assertEqual(f.calls[-2]["order_by"], "grand_total desc")
		self.assertEqual(tb.data_ok, 1)

	def test_blocked_unreadable_and_restricted_are_denied(self):
		tb, _ = self.box()
		for args in ({"doctype": "Employee"}, {"doctype": "LedgerX AI Log"}, {"doctype": "Sales Invoice", "fields": ["cost"]},
			{"doctype": "Sales Invoice", "fields": ["api_key"]}, {"doctype": "Sales Invoice", "filters": [["cost", ">", 0]]}):
			out, err = tb.call("query_records", args)
			self.assertTrue(err)
			self.assertEqual(out["error"], "NOT_PERMITTED", args)
		self.assertEqual(tb.denied, 5)
		self.assertEqual(tb.data_ok, 0)

	def test_unknown_field_is_a_plain_error_not_a_denial(self):
		tb, _ = self.box()
		out, err = tb.call("query_records", {"doctype": "Sales Invoice", "fields": ["nonsense"]})
		self.assertTrue(err)
		self.assertNotEqual(out["error"], "NOT_PERMITTED")
		self.assertEqual(tb.denied, 0)

	def test_bad_filters_and_order(self):
		tb, _ = self.box()
		for args in ({"filters": [["customer", "union", 1]]}, {"order_by": "customer; drop"}, {"limit": "abc"}):
			out, err = tb.call("query_records", dict(doctype="Sales Invoice", **args))
			self.assertTrue(err, args)

	def test_aggregate_sorted_and_numeric_only(self):
		tb, f = self.box()
		out, err = tb.call("aggregate", {"doctype": "Sales Invoice", "function": "sum", "field": "grand_total", "group_by": ["customer"], "limit": 2})
		self.assertFalse(err)
		self.assertEqual(out["rows"], [["B", 30], ["C", 20]])
		self.assertEqual(f.calls[-1]["fields"][-1], {"SUM": "grand_total", "as": "value"})
		out, err = tb.call("aggregate", {"doctype": "Sales Invoice", "function": "SUM", "field": "customer"})
		self.assertTrue(err)
		out, err = tb.call("aggregate", {"doctype": "Sales Invoice", "function": "COUNT"})
		self.assertFalse(err)

	def test_time_series_by_month(self):
		tb, _ = self.box()
		out, err = tb.call("time_series", {"doctype": "Sales Invoice", "date_field": "posting_date", "value_field": "grand_total", "function": "SUM", "period": "month"})
		self.assertFalse(err)
		self.assertEqual(out["rows"], [["2026-01", 15], ["2026-02", 7]])
		out, err = tb.call("time_series", {"doctype": "Sales Invoice", "date_field": "grand_total", "function": "COUNT"})
		self.assertTrue(err)

	def test_show_table_and_blocks(self):
		tb, _ = self.box()
		tb.call("aggregate", {"doctype": "Sales Invoice", "function": "SUM", "field": "grand_total", "group_by": ["customer"]})
		out, err = tb.call("show_table", {"dataset": "d1", "title": "Sales", "chart": {"type": "bar", "label": "customer", "values": "value"}})
		self.assertFalse(err)
		b = tb.blocks()
		self.assertEqual(b[0]["chart"], {"type": "bar", "label": 0, "values": 1})
		self.assertEqual(tb.call("show_table", {"dataset": "zz", "title": "t"})[1], True)

	def test_guide_gating_for_a_normal_user(self):
		tb, _ = self.box(allow_modules=("Accounts",))
		allowed = tb.allowed_pages()
		self.assertIn("invoices", allowed)
		self.assertNotIn("store", allowed)
		self.assertIn("ai", allowed)  # general pages stay available
		out, err = tb.call("search_guide", {"query": "paymob"})
		self.assertTrue(err)
		self.assertEqual(out["error"], "NOT_PERMITTED")
		out, err = tb.call("read_guide", {"page": "store"})
		self.assertEqual(out["error"], "NOT_PERMITTED")
		out, err = tb.call("search_guide", {"query": "sales invoice"})
		self.assertFalse(err)

	def test_system_manager_sees_every_page(self):
		tb, _ = self.box(roles=("System Manager",))
		self.assertIsNone(tb.allowed_pages())
		self.assertFalse(tb.call("read_guide", {"page": "store"})[1])

	def test_unknown_tool_and_crash(self):
		tb, f = self.box()
		self.assertTrue(tb.call("rm_rf", {})[1])
		f.get_list = lambda *a, **k: 1 / 0
		out, err = tb.call("query_records", {"doctype": "Sales Invoice"})
		self.assertTrue(err)
		self.assertEqual(out["error"], "The tool failed.")
		self.assertEqual(len(f.log), 1)

	def test_list_doctypes_only_readable(self):
		tb, _ = self.box()
		out, _e = tb.call("list_doctypes", {})
		self.assertEqual([d["doctype"] for d in out["doctypes"]], ["Sales Invoice", "Employee"])

	def test_describe_hides_restricted_and_secret_fields(self):
		tb, _ = self.box()
		out, _e = tb.call("describe_doctype", {"doctype": "Sales Invoice"})
		names = [x["field"] for x in out["fields"]]
		self.assertIn("grand_total", names)
		self.assertNotIn("cost", names)
		self.assertNotIn("api_key", names)


if __name__ == "__main__":
	unittest.main()
