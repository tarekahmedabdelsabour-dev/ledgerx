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
	var RTL = (document.documentElement.getAttribute("dir") || "").toLowerCase() === "rtl" ||
		(document.documentElement.lang || "").indexOf("ar") === 0;

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
})();
