import sys
import types

from ledgerx import shared


def test_pct_ok():
	assert shared.pct_ok(0) and shared.pct_ok(100) and shared.pct_ok("12.5") and shared.pct_ok(None)
	assert not shared.pct_ok(-0.1) and not shared.pct_ok(100.01) and not shared.pct_ok("x")


def test_doctype_clashes():
	got = shared.doctype_clashes({"a": ["X", "Y"], "b": ["Y", "Z"], "c": ["Y"]})
	assert got == {"Y": ["a", "b", "c"]}
	assert shared.doctype_clashes({"a": ["X"], "b": ["Z"]}) == {}


def test_run_each_isolates_failures(monkeypatch):
	events = []
	fake = types.SimpleNamespace(
		db=types.SimpleNamespace(commit=lambda: events.append("commit"), rollback=lambda: events.append("rollback")),
		log_error=lambda title: events.append(("log", title)),
	)
	monkeypatch.setitem(sys.modules, "frappe", fake)

	def fn(i):
		if i == 2:
			raise ValueError("bad row")

	done, failed = shared.run_each([1, 2, 3], fn, "Job")
	assert done == [1, 3] and failed == [2]
	assert events == ["commit", "rollback", ("log", "Job: 2"), "commit"]
