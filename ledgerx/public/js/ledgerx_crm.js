/* LedgerX identity inside Frappe CRM (/crm): replaces visible product names and keeps the tab title.
   Text nodes are changed in place (never replaced), so Vue's own updates are not disturbed.
   The copyright line (©, "Technologies") is deliberately left untouched. */
(function () {
	var BRAND = "LedgerX";
	var RULES = [
		[/Frappe\s+CRM/g, BRAND + " CRM"],
		[/Frappe\s+HR/g, BRAND + " HR"],
		[/ERPNext/g, BRAND],
		[/Frappe/g, BRAND],
	];

	// Exact visible texts that do not go through the translation files (labels from shared UI code).
	var DICT = {
		"Getting started": "البدء",
		"Start now": "ابدأ الآن",
		"Skip all": "تخطي الكل",
		"Help centre": "مركز المساعدة",
		"Call Logs": "سجل المكالمات",
		"LedgerX HR": "الموارد البشرية",
		"Deals": "الصفقات",
		"Organizations": "المنظمات",
		"Welcome to LedgerX CRM": "مرحبًا بك في LedgerX CRM",
		"Add your first lead": "أضف أول عميل محتمل",
		"Connect your email": "اربط بريدك الإلكتروني",
		"Invite your team": "ادعُ فريقك",
		"Convert lead to deal": "حوّل العميل المحتمل إلى صفقة",
		"Schedule a follow-up task": "جدولة مهمة متابعة",
		"No leads yet": "لا يوجد عملاء محتملون بعد",
		"Import": "استيراد",
		"Documentation": "الوثائق",
	};
	var RTL = false;

	// Frappe CRM never flips its layout by itself, so the sidebar stays on the left for Arabic users.
	// Find the user's language (own setting, then the site default) and switch the page direction.
	function setRtl() {
		RTL = true;
		var h = document.documentElement;
		h.setAttribute("dir", "rtl");
		h.setAttribute("lang", "ar");
		schedule();
	}
	function isArabic(l) { return typeof l === "string" && l.toLowerCase().indexOf("ar") === 0; }
	function getJSON(url) {
		return fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } })
			.then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; });
	}
	function detectLanguage() {
		var m = document.cookie.match(/(?:^|;\s*)user_id=([^;]*)/);
		var user = m ? decodeURIComponent(m[1]) : "";
		var q = "/api/method/frappe.client.get_value?doctype=User&fieldname=language&filters=" +
			encodeURIComponent(JSON.stringify({ name: user }));
		getJSON(q).then(function (j) {
			var l = j.message && j.message.language;
			if (l) return isArabic(l) && setRtl();
			return getJSON("/api/method/frappe.client.get_single_value?doctype=System%20Settings&field=language")
				.then(function (j2) {
					if (isArabic(j2.message)) return setRtl();
					// last resort: the page already shows Arabic text
					var txt = (document.body && document.body.innerText) || "";
					if ((txt.match(/[\u0600-\u06FF]/g) || []).length > 25) setRtl();
				});
		});
	}

	function arabic(text) {
		var t = text.trim();
		if (!t) return text;
		var m = /^(\d+)\/(\d+) steps completed$/.exec(t);
		if (m) return text.replace(t, "تم إنجاز " + m[1] + " من " + m[2] + " خطوات");
		m = /^(\d+)% completed$/.exec(t);
		if (m) return text.replace(t, "اكتمل " + m[1] + "%");
		if (Object.prototype.hasOwnProperty.call(DICT, t)) return text.replace(t, DICT[t]);
		return text;
	}

	function fix(text) {
		if (!text) return text;
		var out = text;
		if (out.indexOf("©") === -1 && !/Technologies|contributors/.test(out)) {
			for (var i = 0; i < RULES.length; i++) out = out.replace(RULES[i][0], RULES[i][1]);
			if (RTL && /[A-Za-z]/.test(out)) out = arabic(out);
		}
		return out;
	}

	function walk(root) {
		var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
		var n;
		while ((n = w.nextNode())) {
			var p = n.parentNode && n.parentNode.nodeName;
			if (p === "SCRIPT" || p === "STYLE") continue;
			var t = fix(n.nodeValue);
			if (t !== n.nodeValue) n.nodeValue = t;
		}
		if (root.querySelectorAll) {
			root.querySelectorAll("[placeholder],[title],[aria-label]").forEach(function (el) {
				["placeholder", "title", "aria-label"].forEach(function (a) {
					var v = el.getAttribute(a);
					if (v) {
						var f = fix(v);
						if (f !== v) el.setAttribute(a, f);
					}
				});
			});
		}
	}

	function fixHead() {
		if (/Frappe/.test(document.title)) document.title = fix(document.title);
		document.querySelectorAll('link[rel*="icon"]').forEach(function (l) {
			if (l.getAttribute("href") !== "/assets/ledgerx/images/ledgerx-favicon.svg")
				l.setAttribute("href", "/assets/ledgerx/images/ledgerx-favicon.svg");
		});
	}

	var queued = false;
	function run() {
		queued = false;
		fixHead();
		if (document.body) walk(document.body);
	}
	function schedule() {
		if (!queued) {
			queued = true;
			setTimeout(run, 60);
		}
	}

	new MutationObserver(schedule).observe(document.documentElement, {
		childList: true, subtree: true, characterData: true,
	});
	run();
	detectLanguage();
})();
