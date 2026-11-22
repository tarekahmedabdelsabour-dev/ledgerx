"""The tools the model may call. Every one runs as the asking user: the framework's own permission checks apply
(roles, user permissions, field levels), and anything outside them is refused, never described."""
import collections

import frappe

from ledgerx.ai import knowledge, safety
from ledgerx.ai.safety import Refused

STANDARD = {"name", "creation", "modified", "owner", "docstatus"}
NO_VALUE = frozenset({"Section Break", "Column Break", "Tab Break", "Attachment Gallery", "HTML", "Table", "Table MultiSelect", "Button", "Image", "Fold", "Heading"})
NUMERIC = {"Currency", "Float", "Int", "Percent", "Long Int"}
DATE_TYPES = {"Date", "Datetime"}
MAX_GROUPS = 2000
MAX_SERIES_ROWS = 20000


def _spec(name, description, props, required=()):
	return {"name": name, "description": description, "input_schema": {"type": "object", "properties": props, "required": list(required)}}


_S, _I = {"type": "string"}, {"type": "integer"}
_FILTERS = {"type": "array", "description": 'Filters as [[field, operator, value], ...], e.g. [["status","=","Paid"],["posting_date","between",["2026-01-01","2026-01-31"]]]. Operators: = != > < >= <= like, not like, in, not in, between, is', "items": {"type": "array"}}

SPECS = [
	_spec("search_guide", "Search the LedgerX user guide for how a page, screen, feature or workflow works. Use for any how-to or explain question.", {"query": _S}, ["query"]),
	_spec("read_guide", "Read a whole guide page by its id (ids are listed in the system prompt).", {"page": _S}, ["page"]),
	_spec("list_modules", "List the modules the user can open.", {}),
	_spec("list_doctypes", "List the document types (records) the user can read, optionally in one module or matching a word.", {"module": _S, "search": _S}),
	_spec("describe_doctype", "Show the fields the user can read in a document type (name, label, type, options). Call before querying a type you are unsure about.", {"doctype": _S}, ["doctype"]),
	_spec("query_records", "List records of one document type with chosen fields. Returns up to 40 rows to you and the full list (up to the limit) to the user's screen.", {"doctype": _S, "fields": {"type": "array", "items": _S}, "filters": _FILTERS, "order_by": {"type": "string", "description": "e.g. 'posting_date desc'"}, "limit": _I}, ["doctype"]),
	_spec("aggregate", "Compute SUM/AVG/COUNT/MIN/MAX of a field, optionally grouped by one or two fields (e.g. sales by customer). Always use this for totals instead of adding rows yourself.", {"doctype": _S, "function": {"type": "string", "enum": sorted(safety.FUNCS)}, "field": {"type": "string", "description": "not needed for COUNT"}, "group_by": {"type": "array", "items": _S}, "filters": _FILTERS, "limit": _I}, ["doctype", "function"]),
	_spec("time_series", "A value per day/week/month/year (e.g. monthly sales) for charts and trends.", {"doctype": _S, "date_field": _S, "value_field": {"type": "string", "description": "not needed for COUNT"}, "function": {"type": "string", "enum": sorted(safety.FUNCS)}, "period": {"type": "string", "enum": ["day", "week", "month", "year"]}, "filters": _FILTERS}, ["doctype", "date_field", "function"]),
	_spec("get_document", "Read one record in full (with its child tables).", {"doctype": _S, "name": _S}, ["doctype", "name"]),
	_spec("list_reports", "List the standard reports the user may run, optionally matching a word.", {"search": _S}),
	_spec("run_report", "Run a standard report with its filters (most need company, from_date, to_date).", {"report_name": _S, "filters": {"type": "object"}}, ["report_name"]),
	_spec("show_table", "Show a dataset (from an earlier tool result) to the user as a table, with an Excel download and an optional simple chart. Use it whenever the answer is a list of rows.", {"dataset": _S, "title": _S, "chart": {"type": "object", "properties": {"type": {"type": "string", "enum": ["bar", "line", "pie"]}, "label": _S, "values": _S}}}, ["dataset", "title"]),
]


class Toolbox:
	def __init__(self, user, lang, guide, max_rows=200, model_rows=40):
		self.user, self.lang, self.guide = user, lang, guide
		self.max_rows, self.model_rows = max(10, int(max_rows or 200)), model_rows
		self.specs = SPECS
		self.denied = 0
		self.data_ok = 0
		self.datasets = collections.OrderedDict()
		self.shown = []
		self.used = []
		self._allowed = False  # cache; None means "everything" so False marks "not computed"

	# ---- dispatch ---------------------------------------------------------------------------------------------

	def call(self, name, args):
		fn = getattr(self, "t_" + str(name), None) if name in {s["name"] for s in SPECS} else None
		if not fn:
			return {"error": "unknown tool"}, True
		import inspect

		params = inspect.signature(fn).parameters
		kwargs = {k: v for k, v in (args or {}).items() if k in params}
		self.used.append(name)
		try:
			out = fn(**kwargs)
		except (Refused, frappe.PermissionError):
			self.denied += 1
			return {"error": safety.NOT_PERMITTED, "note": "Outside the user's permissions. Say so in one sentence; do not describe or guess the data."}, True
		except (ValueError, TypeError) as e:
			return {"error": str(e)}, True
		except Exception:
			frappe.log_error(title="LedgerX AI tool " + str(name))
			return {"error": "The tool failed."}, True
		if name in ("query_records", "aggregate", "time_series", "get_document", "run_report", "search_guide", "read_guide"):
			self.data_ok += 1
		return out, False

	# ---- permission helpers -----------------------------------------------------------------------------------

	def _is_admin(self):
		return "System Manager" in frappe.get_roles(self.user)

	def _doctype(self, dt):
		if not isinstance(dt, str) or not dt or not frappe.db.exists("DocType", dt):
			raise ValueError(f"unknown document type: {dt!r}")
		if safety.is_blocked_doctype(dt) or not frappe.has_permission(dt, "read"):
			raise Refused(dt)
		return frappe.get_meta(dt)

	def _readable(self, meta):
		"""{fieldname: docfield or None} the user may read, without secrets or table fields."""
		out = {f: None for f in STANDARD}
		allowed = set(meta.get_permitted_fieldnames())
		for df in meta.fields:
			if df.fieldname in allowed and df.fieldtype not in NO_VALUE and not safety.is_sensitive_field(df.fieldname, df.fieldtype) and df.fieldtype != "Password":
				out[df.fieldname] = df
		return out

	def _check_fields(self, meta, fields, readable):
		for f in fields:
			if not safety.valid_ident(f):
				raise ValueError(f"bad field name: {f!r}")
			if f in readable:
				continue
			if meta.has_field(f) or safety.is_sensitive_field(f):
				raise Refused(f)
			raise ValueError(f"{meta.name} has no field {f!r}")

	def _filters(self, meta, readable, filters):
		flt = safety.norm_filters(filters)
		self._check_fields(meta, [f[0] for f in flt], readable)
		return flt

	def _pages(self):
		"""None = every guide page; otherwise the ids of pages for modules the user has (plus general pages)."""
		if self._allowed is not False:
			return self._allowed
		if self._is_admin():
			self._allowed = None
			return None
		mine = set(frappe.get_user().allow_modules or [])
		allowed = set()
		for pid in self.guide.titles:
			mods = [m for m in knowledge.PAGE_MODULES.get(pid, []) if frappe.db.exists("Module Def", m)]
			if not mods or mine.intersection(mods):
				allowed.add(pid)
		self._allowed = allowed
		return allowed

	def allowed_pages(self):
		return self._pages()

	def _register(self, title, columns, rows, truncated, source):
		cleaned, cut = safety.clean_rows(rows, columns, self.max_rows)
		did = "d%d" % (len(self.datasets) + 1)
		self.datasets[did] = {"title": title, "columns": columns, "rows": cleaned, "truncated": bool(truncated or cut), "source": source}
		return did, cleaned

	def _for_model(self, did, columns, cleaned, total=None, **extra):
		out = {"dataset": did, "columns": columns, "rows": cleaned[: self.model_rows], "rows_returned": len(cleaned)}
		if len(cleaned) > self.model_rows:
			out["note"] = "Only the first %d rows are shown to you; the user sees all %d. Use aggregate for totals." % (self.model_rows, len(cleaned))
		if total is not None:
			out["total_matching"] = total
		out.update(extra)
		return out

	# ---- guide ------------------------------------------------------------------------------------------------

	def t_search_guide(self, query):
		allowed = self._pages()
		hits = self.guide.search(query, self.lang, allowed)
		if not hits and allowed is not None:
			top = self.guide.search(query, self.lang, None, limit=1)
			if top and top[0]["page"] not in allowed:
				raise Refused(top[0]["page"])
		return {"results": hits}

	def t_read_guide(self, page):
		allowed = self._pages()
		if page not in self.guide.titles:
			raise ValueError("unknown guide page")
		if allowed is not None and page not in allowed:
			raise Refused(page)
		return self.guide.page(page, self.lang)

	# ---- structure --------------------------------------------------------------------------------------------

	def t_list_modules(self):
		if self._is_admin():
			mods = frappe.get_all("Module Def", pluck="name", order_by="name")
		else:
			mods = sorted(frappe.get_user().allow_modules or [])
		return {"modules": mods}

	def t_list_doctypes(self, module=None, search=None):
		readable = set(frappe.permissions.get_doctypes_with_read())
		filters = {"istable": 0, "issingle": 0}
		if module:
			filters["module"] = str(module)
		rows = frappe.get_all("DocType", filters=filters, fields=["name", "module"], order_by="name", limit_page_length=3000)
		q = safety_norm(search)
		out = [{"doctype": r.name, "module": r.module} for r in rows if r.name in readable and not safety.is_blocked_doctype(r.name) and (not q or q in safety_norm(r.name))]
		return {"doctypes": out[:80], "more": len(out) > 80}

	def t_describe_doctype(self, doctype):
		meta = self._doctype(doctype)
		readable = self._readable(meta)
		fields = []
		for fn, df in readable.items():
			if df is None:
				continue
			item = {"field": fn, "label": df.label, "type": df.fieldtype}
			if df.fieldtype in ("Link", "Select", "Dynamic Link") and df.options:
				item["options"] = df.options if df.fieldtype != "Select" else df.options.split("\n")[:25]
			fields.append(item)
		return {"doctype": doctype, "title_field": meta.title_field, "submittable": bool(meta.is_submittable), "standard_fields": sorted(STANDARD), "fields": fields,
			"child_tables": [{"field": d.fieldname, "doctype": d.options} for d in meta.get_table_fields()]}

	# ---- data -------------------------------------------------------------------------------------------------

	def t_query_records(self, doctype, fields=None, filters=None, order_by=None, limit=20):
		meta = self._doctype(doctype)
		readable = self._readable(meta)
		fields = list(fields or [])
		if not fields:
			fields = ["name"] + ([meta.title_field] if meta.title_field and meta.title_field in readable else []) + [f for f in ("status", "posting_date", "transaction_date", "grand_total") if f in readable and f not in fields][:3]
		fields = list(dict.fromkeys(fields))[:20]
		self._check_fields(meta, fields, readable)
		flt = self._filters(meta, readable, filters)
		field, desc = safety.norm_order(order_by, readable)
		try:
			limit = max(1, min(int(limit or 20), self.max_rows))
		except (TypeError, ValueError):
			raise ValueError("limit must be a number")
		rows = frappe.get_list(doctype, fields=fields, filters=flt, order_by=("%s %s" % (field, "desc" if desc else "asc")) if field else None, limit_page_length=limit + 1)
		total = self._count(doctype, flt)
		cleaned_cut = len(rows) > limit
		did, cleaned = self._register(f"{doctype}", fields, rows[:limit], cleaned_cut, {"doctype": doctype})
		return self._for_model(did, fields, cleaned, total, truncated=cleaned_cut)

	def _count(self, doctype, flt):
		r = frappe.get_list(doctype, fields=[{"COUNT": "*", "as": "n"}], filters=flt)
		return int(r[0].n) if r else 0

	def t_aggregate(self, doctype, function, field=None, group_by=None, filters=None, limit=20):
		meta = self._doctype(doctype)
		readable = self._readable(meta)
		function = str(function).upper()
		if function not in safety.FUNCS:
			raise ValueError("function must be one of " + ", ".join(sorted(safety.FUNCS)))
		group_by = list(group_by or [])[:2]
		if function == "COUNT":
			agg = {"COUNT": "*", "as": "value"}
		else:
			if not field:
				raise ValueError("field is required")
			self._check_fields(meta, [field], readable)
			df = readable.get(field)
			if function in ("SUM", "AVG") and not (df is not None and df.fieldtype in NUMERIC):
				raise ValueError(f"{field} is not a numeric field")
			agg = {function: field, "as": "value"}
		self._check_fields(meta, group_by, readable)
		flt = self._filters(meta, readable, filters)
		rows = frappe.get_list(doctype, fields=group_by + [agg], filters=flt, group_by=", ".join(group_by) or None, limit_page_length=MAX_GROUPS)
		rows = sorted(rows, key=lambda r: (r.get("value") is None, -(float(r.get("value") or 0))))
		try:
			limit = max(1, min(int(limit or 20), self.max_rows))
		except (TypeError, ValueError):
			raise ValueError("limit must be a number")
		cols = group_by + ["value"]
		did, cleaned = self._register(f"{function} {field or doctype}" + (" / " + ", ".join(group_by) if group_by else ""), cols, rows[:limit], len(rows) > limit, {"doctype": doctype})
		return self._for_model(did, cols, cleaned, groups=len(rows))

	def t_time_series(self, doctype, date_field, function, value_field=None, period="month", filters=None):
		meta = self._doctype(doctype)
		readable = self._readable(meta)
		function = str(function).upper()
		if function not in safety.FUNCS:
			raise ValueError("function must be one of " + ", ".join(sorted(safety.FUNCS)))
		if period not in ("day", "week", "month", "year"):
			raise ValueError("period must be day, week, month or year")
		self._check_fields(meta, [date_field] + ([value_field] if value_field else []), readable)
		df = readable.get(date_field)
		if date_field not in ("creation", "modified") and not (df is not None and df.fieldtype in DATE_TYPES):
			raise ValueError(f"{date_field} is not a date field")
		if function != "COUNT" and not value_field:
			raise ValueError("value_field is required")
		flt = self._filters(meta, readable, filters)
		fields = [date_field] + ([value_field] if value_field else [])
		rows = frappe.get_list(doctype, fields=list(dict.fromkeys(fields)), filters=flt + [[date_field, "is", "set"]], order_by=f"{date_field} asc", limit_page_length=MAX_SERIES_ROWS + 1)
		partial = len(rows) > MAX_SERIES_ROWS
		buckets = collections.OrderedDict()
		for r in rows[:MAX_SERIES_ROWS]:
			d = frappe.utils.getdate(r.get(date_field))
			key = {"day": d.isoformat(), "month": d.strftime("%Y-%m"), "year": str(d.year), "week": "%d-W%02d" % d.isocalendar()[:2]}[period]
			buckets.setdefault(key, []).append(float(r.get(value_field) or 0) if value_field else 1.0)
		agg = {"SUM": sum, "COUNT": len, "AVG": lambda v: sum(v) / len(v), "MIN": min, "MAX": max}[function]
		data = [{"period": k, "value": round(agg(v), 2)} for k, v in buckets.items()]
		did, cleaned = self._register(f"{function} {value_field or doctype} / {period}", ["period", "value"], data[-self.max_rows:], partial or len(data) > self.max_rows, {"doctype": doctype})
		return self._for_model(did, ["period", "value"], cleaned, partial=partial)

	def t_get_document(self, doctype, name):
		meta = self._doctype(doctype)
		doc = frappe.get_doc(doctype, name)
		doc.check_permission("read")
		doc.apply_fieldlevel_read_permissions()
		out = {"doctype": doctype, "name": doc.name}
		for df in meta.fields:
			if df.fieldtype in NO_VALUE or df.fieldtype == "Password" or safety.is_sensitive_field(df.fieldname, df.fieldtype):
				continue
			v = doc.get(df.fieldname)
			if v not in (None, "", 0) or df.fieldtype in ("Check",):
				out[df.fieldname] = safety.clean_value(v)
		for t in meta.get_table_fields():
			child = frappe.get_meta(t.options)
			rows = doc.get(t.fieldname) or []
			if not rows:
				continue
			names = [c.fieldname for c in child.fields if c.fieldtype not in NO_VALUE and c.fieldtype != "Password" and not safety.is_sensitive_field(c.fieldname, c.fieldtype) and c.permlevel == 0][:12]
			out[t.fieldname] = [{n: safety.clean_value(r.get(n)) for n in names if r.get(n) not in (None, "")} for r in rows[:30]]
		out["docstatus"] = doc.docstatus
		return out

	# ---- reports ----------------------------------------------------------------------------------------------

	def t_list_reports(self, search=None):
		q = safety_norm(search)
		rows = frappe.get_all("Report", filters={"disabled": 0}, fields=["name", "ref_doctype", "module"], order_by="name", limit_page_length=1000)
		out = []
		for r in rows:
			if q and q not in safety_norm(r.name):
				continue
			if safety.is_blocked_doctype(r.ref_doctype or ""):
				continue
			try:
				if frappe.get_doc("Report", r.name).is_permitted():
					out.append({"report": r.name, "module": r.module, "based_on": r.ref_doctype})
			except Exception:
				continue
			if len(out) >= 40:
				break
		return {"reports": out}

	def t_run_report(self, report_name, filters=None):
		if not isinstance(report_name, str) or not frappe.db.exists("Report", report_name):
			raise ValueError("unknown report")
		ref = frappe.db.get_value("Report", report_name, "ref_doctype")
		if safety.is_blocked_doctype(ref or ""):
			raise Refused(report_name)
		if filters is not None and not isinstance(filters, dict):
			raise ValueError("filters must be an object")
		from frappe.desk.query_report import run

		res = run(report_name, filters=filters or {}, ignore_prepared_report=True)
		cols = []
		for c in res.get("columns") or []:
			if isinstance(c, dict):
				cols.append((c.get("fieldname") or c.get("label"), c.get("label") or c.get("fieldname")))
			else:
				label = str(c).split(":")[0]
				cols.append((label, label))
		rows = []
		for r in res.get("result") or []:
			if isinstance(r, dict):
				rows.append([r.get(k) for k, _ in cols])
			elif isinstance(r, (list, tuple)):
				rows.append(list(r)[: len(cols)])
		keep = [i for i, (k, _) in enumerate(cols) if not safety.is_sensitive_field(str(k))]
		names = [cols[i][1] for i in keep]
		rows = [[r[i] if i < len(r) else None for i in keep] for r in rows]
		did, cleaned = self._register(report_name, names, rows, False, {"report": report_name})
		return self._for_model(did, names, cleaned, total=len(rows))

	# ---- display ----------------------------------------------------------------------------------------------

	def t_show_table(self, dataset, title, chart=None):
		ds = self.datasets.get(dataset)
		if not ds:
			raise ValueError("unknown dataset; use an id from an earlier result")
		ds["title"] = str(title)[:120]
		spec = None
		if isinstance(chart, dict) and chart.get("type") in ("bar", "line", "pie"):
			lab, val = chart.get("label"), chart.get("values")
			if lab in ds["columns"] and val in ds["columns"]:
				spec = {"type": chart["type"], "label": ds["columns"].index(lab), "values": ds["columns"].index(val)}
		self.shown = [s for s in self.shown if s["dataset"] != dataset] + [{"dataset": dataset, "chart": spec}]
		return {"ok": True}

	def blocks(self):
		"""What the screen draws: the tables the model chose to show, in order."""
		out = []
		for s in self.shown:
			ds = self.datasets[s["dataset"]]
			out.append({"id": s["dataset"], "title": ds["title"], "columns": ds["columns"], "rows": ds["rows"], "truncated": ds["truncated"], "chart": s["chart"]})
		return out


def safety_norm(text):
	return knowledge.norm(text or "")
