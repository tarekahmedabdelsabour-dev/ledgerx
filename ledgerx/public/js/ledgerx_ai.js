/* LedgerX Assistant: a floating icon and chat panel. Reads and explains only; the server answers as the signed-in user.
 * Works on the desk, the CRM and the HR screens. Everything the model wrote is escaped before it is drawn. */
(function () {
	"use strict";
	if (window.__lxAI) return;
	window.__lxAI = true;

	var API = "/api/method/ledgerx.api.ai.";
	var KEY = "lx_ai_chat";
	var state = { enabled: false, open: false, busy: false, history: [], token: "", lang: "ar" };

	function isAr() { return state.lang !== "en"; }
	function T(ar, en) { return isAr() ? ar : en; }
	function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
	function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

	function csrf() {
		var f = window.frappe || {};
		var t = window.csrf_token || f.csrf_token || (f.boot && f.boot.csrf_token) || "";
		if (t && t !== "{{ csrf_token }}") return Promise.resolve(t);
		if (state.token) return Promise.resolve(state.token);
		return fetch("/api/method/ledgerx.api.lang.csrf", { credentials: "same-origin" }).then(function (r) { return r.json(); }).then(function (j) { state.token = (j && j.message) || ""; return state.token; });
	}

	function call(method, body, post) {
		var go = function (token) {
			var opt = { credentials: "same-origin", headers: { "Accept": "application/json" } };
			var url = API + method;
			if (post) {
				opt.method = "POST";
				opt.headers["Content-Type"] = "application/json";
				opt.headers["X-Frappe-CSRF-Token"] = token;
				opt.body = JSON.stringify(body || {});
			} else if (body) {
				url += "?" + Object.keys(body).map(function (k) { return k + "=" + encodeURIComponent(body[k]); }).join("&");
			}
			return fetch(url, opt).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); });
		};
		return (post ? csrf() : Promise.resolve("")).then(go);
	}

	// ---- styles ---------------------------------------------------------------------------------------------
	var CSS = [
		"#lx-ai-fab{position:fixed;bottom:16px;inset-inline-end:16px;z-index:10000;width:52px;height:52px;border-radius:50%;border:0;cursor:pointer;padding:0;",
		"background:linear-gradient(135deg,#0B2A5B,#0F766E);box-shadow:0 6px 18px rgba(7,26,58,.35);display:flex;align-items:center;justify-content:center}",
		"#lx-ai-fab:focus-visible{outline:3px solid #14B8A6;outline-offset:2px}",
		"#lx-ai-fab.lx-up{bottom:64px}",
		"#lx-ai{--bg:#fff;--fg:#0f172a;--mut:#64748b;--line:#e2e8f0;--soft:#f1f5f9;--me:#0F766E;--mefg:#fff;position:fixed;bottom:80px;inset-inline-end:16px;z-index:10001;width:min(440px,calc(100vw - 24px));height:min(640px,calc(100vh - 110px));",
		"background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.28);display:none;flex-direction:column;overflow:hidden;font:14px/1.55 system-ui,Tahoma,sans-serif}",
		"#lx-ai.lx-up{bottom:128px;height:min(640px,calc(100vh - 150px))}",
		"#lx-ai.on{display:flex}",
		"@media (prefers-color-scheme:dark){#lx-ai{--bg:#0f1b33;--fg:#e5edf8;--mut:#94a3b8;--line:#1e3358;--soft:#16264a}}",
		"[data-theme=dark] #lx-ai{--bg:#0f1b33;--fg:#e5edf8;--mut:#94a3b8;--line:#1e3358;--soft:#16264a}",
		".lx-ai-h{display:flex;align-items:center;gap:8px;padding:10px 14px;background:linear-gradient(135deg,#0B2A5B,#0F766E);color:#fff;font-weight:600}",
		".lx-ai-h span{flex:1}.lx-ai-h button{background:transparent;border:0;color:#fff;cursor:pointer;font-size:13px;opacity:.85;padding:4px 6px;border-radius:6px}",
		".lx-ai-h button:hover{opacity:1;background:rgba(255,255,255,.15)}",
		".lx-ai-b{flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:10px}",
		".lx-m{max-width:92%;padding:8px 12px;border-radius:12px;word-wrap:break-word;overflow-wrap:anywhere}",
		".lx-m.u{align-self:flex-start;background:var(--me);color:var(--mefg)}.lx-m.a{align-self:flex-start;background:var(--soft)}",
		".lx-m p{margin:0 0 6px}.lx-m p:last-child{margin:0}.lx-m ul{margin:4px 0;padding-inline-start:20px}.lx-m code{background:rgba(100,116,139,.2);padding:0 4px;border-radius:4px}",
		".lx-t{width:100%;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--bg)}",
		".lx-t h4{margin:0;padding:6px 10px;font-size:13px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--line)}.lx-t h4 span{flex:1}",
		".lx-t h4 button{border:1px solid var(--line);background:var(--soft);color:var(--fg);border-radius:6px;font-size:12px;cursor:pointer;padding:2px 8px}",
		".lx-tw{max-height:280px;overflow:auto}.lx-t table{border-collapse:collapse;width:100%;font-size:12.5px}",
		".lx-t th,.lx-t td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:start;white-space:nowrap}.lx-t th{position:sticky;top:0;background:var(--soft)}",
		".lx-t td.n{text-align:end;font-variant-numeric:tabular-nums}.lx-t .cut{padding:4px 10px;color:var(--mut);font-size:12px}",
		".lx-ch{padding:8px 10px;border-bottom:1px solid var(--line)}.lx-ch svg{width:100%;height:auto;display:block}",
		".lx-s{display:flex;flex-wrap:wrap;gap:6px}.lx-s button{border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:999px;padding:5px 11px;font-size:12.5px;cursor:pointer}",
		".lx-s button:hover{border-color:#14B8A6}",
		".lx-ai-f{display:flex;gap:8px;padding:10px;border-top:1px solid var(--line);align-items:flex-end}",
		".lx-ai-f textarea{flex:1;resize:none;border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:var(--bg);color:var(--fg);font:inherit;max-height:110px;min-height:38px}",
		".lx-ai-f textarea:focus{outline:2px solid #14B8A6;border-color:transparent}",
		".lx-ai-f button{background:var(--me);color:#fff;border:0;border-radius:10px;padding:0 14px;height:38px;cursor:pointer;font-weight:600}.lx-ai-f button:disabled{opacity:.5;cursor:default}",
		".lx-dots{display:inline-flex;gap:4px}.lx-dots i{width:6px;height:6px;border-radius:50%;background:var(--mut);animation:lxd 1s infinite}.lx-dots i:nth-child(2){animation-delay:.15s}.lx-dots i:nth-child(3){animation-delay:.3s}",
		"@keyframes lxd{0%,80%,100%{opacity:.25}40%{opacity:1}}@media (prefers-reduced-motion:reduce){.lx-dots i{animation:none}}",
		"@media print{#lx-ai,#lx-ai-fab{display:none}}"
	].join("");

	var ICON = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2l1.9 5.6L19.5 9.5l-5.6 1.9L12 17l-1.9-5.6L4.5 9.5l5.6-1.9L12 2z" fill="#fff"/><path d="M19 15l.9 2.6 2.6.9-2.6.9L19 22l-.9-2.6-2.6-.9 2.6-.9L19 15z" fill="#99f6e4"/></svg>';

	// ---- text -----------------------------------------------------------------------------------------------
	function inline(s) { return esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>"); }
	function md(text) {
		var out = [], list = false;
		String(text || "").split(/\r?\n/).forEach(function (line) {
			var m = /^\s*(?:[-*]|\d+[.)])\s+(.*)$/.exec(line);
			if (m) { if (!list) { out.push("<ul>"); list = true; } out.push("<li>" + inline(m[1]) + "</li>"); return; }
			if (list) { out.push("</ul>"); list = false; }
			var h = /^#{1,4}\s+(.*)$/.exec(line);
			if (h) out.push("<p><strong>" + inline(h[1]) + "</strong></p>");
			else if (line.trim()) out.push("<p>" + inline(line) + "</p>");
		});
		if (list) out.push("</ul>");
		return out.join("");
	}

	// ---- chart ----------------------------------------------------------------------------------------------
	var COLORS = ["#0F766E", "#0B2A5B", "#14B8A6", "#6366F1", "#F59E0B", "#E11D48", "#64748B", "#84CC16"];
	function chart(block) {
		var c = block.chart; if (!c) return null;
		var rows = block.rows.slice(0, c.type === "pie" ? 8 : 24), labels = rows.map(function (r) { return String(r[c.label]); }), vals = rows.map(function (r) { return Number(r[c.values]) || 0; });
		if (!vals.length) return null;
		var W = 400, H = 170, ns = "http://www.w3.org/2000/svg", s = document.createElementNS(ns, "svg");
		s.setAttribute("viewBox", "0 0 " + W + " " + H); s.setAttribute("role", "img"); s.setAttribute("aria-label", block.title);
		function node(n, a, txt) { var e = document.createElementNS(ns, n); Object.keys(a).forEach(function (k) { e.setAttribute(k, a[k]); }); if (txt != null) e.textContent = txt; s.appendChild(e); return e; }
		var max = Math.max.apply(null, vals.concat([0])), min = Math.min.apply(null, vals.concat([0])), span = (max - min) || 1;
		if (c.type === "pie") {
			var tot = vals.reduce(function (a, b) { return a + Math.abs(b); }, 0) || 1, ang = -Math.PI / 2, cx = 80, cy = 85, r = 70;
			vals.forEach(function (v, i) {
				var a2 = ang + Math.abs(v) / tot * Math.PI * 2, big = a2 - ang > Math.PI ? 1 : 0;
				if (vals.length === 1) node("circle", { cx: cx, cy: cy, r: r, fill: COLORS[0] });
				else node("path", { d: "M" + cx + "," + cy + " L" + (cx + r * Math.cos(ang)) + "," + (cy + r * Math.sin(ang)) + " A" + r + "," + r + " 0 " + big + " 1 " + (cx + r * Math.cos(a2)) + "," + (cy + r * Math.sin(a2)) + " Z", fill: COLORS[i % COLORS.length] });
				node("rect", { x: 175, y: 12 + i * 19, width: 10, height: 10, rx: 2, fill: COLORS[i % COLORS.length] });
				node("text", { x: 191, y: 21 + i * 19, "font-size": 11, fill: "currentColor" }, labels[i].slice(0, 22) + " (" + Math.round(Math.abs(v) / tot * 100) + "%)");
				ang = a2;
			});
		} else {
			var L = 6, B = 28, pw = W - L * 2, ph = H - B - 8, y0 = 8 + ph * (max / span), n = vals.length, step = pw / n;
			node("line", { x1: L, x2: W - L, y1: y0, y2: y0, stroke: "currentColor", "stroke-opacity": .3 });
			if (c.type === "line") {
				var pts = vals.map(function (v, i) { return (L + step * (i + .5)) + "," + (8 + ph * (max - v) / span); });
				node("polyline", { points: pts.join(" "), fill: "none", stroke: COLORS[0], "stroke-width": 2.5 });
				vals.forEach(function (v, i) { node("circle", { cx: L + step * (i + .5), cy: 8 + ph * (max - v) / span, r: 3, fill: COLORS[0] }); });
			} else {
				vals.forEach(function (v, i) {
					var h = Math.abs(v) / span * ph, y = v >= 0 ? y0 - h : y0, bw = Math.min(step * .7, 36);
					node("rect", { x: L + step * i + (step - bw) / 2, y: y, width: bw, height: Math.max(h, 1), rx: 2, fill: COLORS[0] });
				});
			}
			var every = Math.ceil(n / 8);
			labels.forEach(function (l, i) { if (i % every === 0) node("text", { x: L + step * (i + .5), y: H - 10, "font-size": 10, "text-anchor": "middle", fill: "currentColor" }, l.slice(0, 10)); });
			node("text", { x: W - L, y: 10, "font-size": 10, "text-anchor": "end", fill: "currentColor" }, fmt(max));
		}
		var d = el("div", "lx-ch"); d.appendChild(s); return d;
	}
	function fmt(v) { return typeof v === "number" ? v.toLocaleString("en-US", { maximumFractionDigits: 2 }) : v; }

	// ---- table ----------------------------------------------------------------------------------------------
	function table(block) {
		var box = el("div", "lx-t"), h = el("h4"), t = el("span", null, block.title || ""); h.appendChild(t);
		var x = el("button", null, T("تنزيل Excel", "Excel")); x.type = "button"; x.addEventListener("click", function () { download(block, x); }); h.appendChild(x);
		box.appendChild(h);
		var ch = chart(block); if (ch) box.appendChild(ch);
		var w = el("div", "lx-tw"), tb = el("table"), th = el("tr");
		block.columns.forEach(function (c) { th.appendChild(el("th", null, c)); });
		var head = el("thead"); head.appendChild(th); tb.appendChild(head);
		var body = el("tbody");
		block.rows.forEach(function (r) {
			var tr = el("tr");
			r.forEach(function (v) { var td = el("td", typeof v === "number" ? "n" : null, v == null ? "" : fmt(v)); tr.appendChild(td); });
			body.appendChild(tr);
		});
		tb.appendChild(body); w.appendChild(tb); box.appendChild(w);
		if (block.truncated) box.appendChild(el("div", "cut", T("اتعرض جزء من النتائج بس. ضيّق الفلتر لنتيجة أدق.", "Only part of the results is shown. Narrow the filter for more.")));
		return box;
	}
	function download(block, btn) {
		btn.disabled = true;
		call("download", { dataset: block.id }, false).then(function (r) {
			btn.disabled = false;
			var m = r.j && r.j.message; if (!m) return;
			var bin = atob(m.data), a = new Uint8Array(bin.length);
			for (var i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i);
			var url = URL.createObjectURL(new Blob([a], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" })), l = document.createElement("a");
			l.href = url; l.download = m.filename; document.body.appendChild(l); l.click(); l.remove(); setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
		}, function () { btn.disabled = false; });
	}

	// ---- panel ----------------------------------------------------------------------------------------------
	var fab, panel, body, input, send;

	function scroll() { body.scrollTop = body.scrollHeight; }
	function addMsg(role, text) { var m = el("div", "lx-m " + (role === "user" ? "u" : "a")); if (role === "user") m.textContent = text; else m.innerHTML = md(text); body.appendChild(m); scroll(); return m; }
	function save() { try { sessionStorage.setItem(KEY, JSON.stringify(state.history.slice(-16))); } catch (e) {} }
	function load() { try { state.history = JSON.parse(sessionStorage.getItem(KEY) || "[]") || []; } catch (e) { state.history = []; } }

	function suggestions() {
		var s = isAr() ? ["إزاي أعمل فاتورة مبيعات؟", "إيه إجمالي المبيعات الشهر ده؟", "أعلى 10 عملاء مبيعًا", "اشرحلي الصفحة اللي أنا فيها"] : ["How do I create a sales invoice?", "Total sales this month", "Top 10 customers by sales", "Explain the page I am on"];
		var d = el("div", "lx-s");
		s.forEach(function (q) { var b = el("button", null, q); b.type = "button"; b.addEventListener("click", function () { ask(q); }); d.appendChild(b); });
		return d;
	}

	function welcome() {
		body.textContent = "";
		var m = addMsg("assistant", T("أهلًا، أنا مساعد LedgerX. أشرح لك أي صفحة وأطلّعلك تقارير من بياناتك، في حدود صلاحياتك. أقدر أقرأ وأشرح بس، مش بعدّل حاجة.", "Hi, I am the LedgerX Assistant. I explain any page and build reports from your data, within your permissions. I can read and explain only; I never change anything."));
		m.appendChild(suggestions());
	}

	function build() {
		var st = el("style"); st.textContent = CSS; document.head.appendChild(st);
		fab = el("button"); fab.id = "lx-ai-fab"; fab.type = "button"; fab.innerHTML = ICON; fab.setAttribute("aria-label", T("مساعد LedgerX", "LedgerX Assistant")); fab.title = fab.getAttribute("aria-label");
		fab.addEventListener("click", toggle);
		panel = el("div"); panel.id = "lx-ai"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", fab.title);
		panel.dir = isAr() ? "rtl" : "ltr";
		var h = el("div", "lx-ai-h"), tt = el("span", null, T("مساعد LedgerX", "LedgerX Assistant"));
		var clr = el("button", null, T("محادثة جديدة", "New chat")); clr.type = "button"; clr.addEventListener("click", function () { state.history = []; save(); welcome(); });
		var cl = el("button", null, "✕"); cl.type = "button"; cl.setAttribute("aria-label", T("إغلاق", "Close")); cl.addEventListener("click", toggle);
		h.appendChild(tt); h.appendChild(clr); h.appendChild(cl);
		body = el("div", "lx-ai-b"); body.setAttribute("aria-live", "polite");
		var f = el("form", "lx-ai-f"); input = el("textarea"); input.rows = 1; input.maxLength = 2000; input.placeholder = T("اسأل عن أي حاجة في التطبيق…", "Ask about anything in the app…");
		send = el("button", null, T("إرسال", "Send")); send.type = "submit";
		f.appendChild(input); f.appendChild(send);
		f.addEventListener("submit", function (e) { e.preventDefault(); var q = input.value.trim(); if (q) ask(q); });
		input.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); f.requestSubmit(); } });
		panel.addEventListener("keydown", function (e) { if (e.key === "Escape") toggle(); });
		panel.appendChild(h); panel.appendChild(body); panel.appendChild(f);
		document.body.appendChild(panel); document.body.appendChild(fab);
		var shell = /^\/(crm|hr|hrms)(\/|$)/.test(location.pathname);
		if (shell) { fab.classList.add("lx-up"); panel.classList.add("lx-up"); }
		load();
		if (state.history.length) state.history.forEach(function (h2) { addMsg(h2.role, h2.content); }); else welcome();
	}

	function toggle() {
		state.open = !state.open; panel.classList.toggle("on", state.open);
		if (state.open) { setTimeout(function () { input.focus(); scroll(); }, 30); } else fab.focus();
	}

	function ask(q) {
		if (state.busy) return;
		state.busy = true; send.disabled = true; input.value = "";
		var sug = body.querySelector(".lx-s"); if (sug) sug.remove();
		addMsg("user", q);
		var wait = el("div", "lx-m a"); wait.innerHTML = '<span class="lx-dots"><i></i><i></i><i></i></span>'; body.appendChild(wait); scroll();
		var hist = state.history.slice(-8);
		call("chat", { message: q, history: hist, context: { route: location.pathname + location.hash } }, true).then(function (r) {
			wait.remove();
			var m = r.j && r.j.message, txt;
			if (!r.ok || !m) { txt = T("تعذّر تنفيذ الطلب.", "The request could not be completed."); addMsg("assistant", txt); return; }
			addMsg("assistant", m.answer);
			(m.blocks || []).forEach(function (b) { body.appendChild(table(b)); });
			scroll();
			if (!m.error) { state.history.push({ role: "user", content: q }, { role: "assistant", content: m.answer }); save(); }
		}, function () {
			wait.remove(); addMsg("assistant", T("تعذّر الاتصال بالسيرفر.", "Could not reach the server."));
		}).then(function () { state.busy = false; send.disabled = false; input.focus(); });
	}

	// Administrator, assistant not switched on yet: the panel points to the settings instead of chatting.
	function setupMode() {
		body.textContent = "";
		addMsg("assistant", T("المساعد لسه مش متفعّل. افتح الإعدادات، الصق مفتاح Claude API، علّم «Enabled» واحفظ. الأيقونة دي بتظهر لك إنت بس (كمدير) لحد ما يتفعّل.", "The assistant is not switched on yet. Open the settings, paste your Claude API key, tick Enabled and save. Only administrators see this icon until it is on."));
		var a = el("a", null, T("فتح إعدادات المساعد", "Open assistant settings")); a.href = "/desk/ledgerx-ai-settings";
		a.style.cssText = "align-self:flex-start;background:#0F766E;color:#fff;padding:8px 14px;border-radius:10px;text-decoration:none;font-weight:600";
		body.appendChild(a);
		input.disabled = true; send.disabled = true;
		input.placeholder = T("فعّل المساعد الأول", "Switch the assistant on first");
	}

	function boot() {
		if (/^\/(login|docs|store|shop)/.test(location.pathname)) return;
		call("status", null, false).then(function (r) {
			var m = r.j && r.j.message;
			if (!r.ok || !m || !(m.enabled || m.setup)) return;
			state.enabled = !!m.enabled; state.lang = m.lang || "ar";
			if (!document.getElementById("lx-ai-fab")) build();
			if (!m.enabled) setupMode();
		}, function () {});
	}
	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
