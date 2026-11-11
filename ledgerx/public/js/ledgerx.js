// LedgerX - desk behaviour.
// Visual theming lives in ledgerx.css; this file only fixes text that CSS cannot reach.

(function () {
	"use strict";

	var BRAND = "LedgerX";
	var LEGACY_NAMES = /\b(ERPNext|Frappe)\b/g;

	// Browser tab title: Frappe/ERPNext sometimes append their own name.
	function rebrandTitle() {
		var title = document.title;
		if (title && LEGACY_NAMES.test(title)) {
			LEGACY_NAMES.lastIndex = 0;
			document.title = title.replace(LEGACY_NAMES, BRAND);
		}
		LEGACY_NAMES.lastIndex = 0;
	}

	function watchTitle() {
		var el = document.querySelector("title");
		if (!el || !window.MutationObserver) return;
		new MutationObserver(rebrandTitle).observe(el, {
			childList: true,
			characterData: true,
			subtree: true,
		});
		rebrandTitle();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", watchTitle);
	} else {
		watchTitle();
	}

	// ---- No videos: the "Watch Video" help on list views and the YouTube player.
	// Apps register help videos with `frappe.help.youtube_id["User"] = "..."` when a list view loads.
	// Turning `youtube_id` into a store that forgets everything makes those assignments harmless.
	function disableHelpVideos() {
		if (!window.frappe || !frappe.help) return false;
		try {
			Object.defineProperty(frappe.help, "youtube_id", {
				configurable: true,
				get: function () {
					return {};
				},
				set: function () {},
			});
		} catch (e) {
			frappe.help.youtube_id = {};
		}
		frappe.help.show_video = function () {};
		return true;
	}

	if (!disableHelpVideos()) {
		var tries = 0;
		var timer = setInterval(function () {
			if (disableHelpVideos() || ++tries > 40) clearInterval(timer);
		}, 250);
	}
})();

// ---- The product name "ERPNext" never shows on screen.
// Apps (ERPNext, HRMS, Frappe) write their own name into labels, help texts, messages, tooltips and
// onboarding. Text is rewritten as it is drawn: visible text nodes and the title / placeholder /
// aria-label / tooltip attributes only. Form values, editors, code blocks and scripts are never
// touched, and neither are route or doctype names (those live in data, not in the text on screen).
(function () {
	"use strict";

	var BRAND = "LedgerX";
	var NAME = /\bERP ?Next\b/g;
	var TEST = /ERP ?Next/;
	var ATTRS = ["title", "placeholder", "aria-label", "data-original-title", "alt"];
	var SKIP = /^(SCRIPT|STYLE|TEXTAREA|INPUT|PRE|CODE|NOSCRIPT)$/;
	var SKIP_SELECTOR = ".ql-editor, .CodeMirror, .ace_editor, [contenteditable='true'], .frappe-control[data-fieldtype='Code']";

	function skipped(el) {
		if (!el) return false;
		if (el.nodeType === 1 && (SKIP.test(el.tagName) || (el.closest && el.closest(SKIP_SELECTOR)))) return true;
		return false;
	}

	function fixAttrs(el) {
		for (var i = 0; i < ATTRS.length; i++) {
			var v = el.getAttribute(ATTRS[i]);
			if (v && TEST.test(v)) el.setAttribute(ATTRS[i], v.replace(NAME, BRAND));
		}
	}

	function sweep(root) {
		if (!root) return;
		if (root.nodeType === 3) {
			var p = root.parentNode;
			if (TEST.test(root.nodeValue) && !skipped(p)) root.nodeValue = root.nodeValue.replace(NAME, BRAND);
			return;
		}
		if (root.nodeType !== 1 || skipped(root)) return;
		fixAttrs(root);
		var walker = document.createTreeWalker(root, 1 | 4, {
			acceptNode: function (n) {
				if (n.nodeType === 1) return SKIP.test(n.tagName) ? 2 : 1; // reject subtree of script/input/...
				return 1;
			},
		});
		var n;
		while ((n = walker.nextNode())) {
			if (n.nodeType === 3) {
				if (TEST.test(n.nodeValue) && !skipped(n.parentNode)) n.nodeValue = n.nodeValue.replace(NAME, BRAND);
			} else {
				fixAttrs(n);
			}
		}
	}

	var queue = [], timer = null;
	function schedule(node) {
		queue.push(node);
		if (timer) return;
		timer = setTimeout(function () {
			var items = queue;
			queue = [];
			timer = null;
			for (var i = 0; i < items.length; i++) sweep(items[i]);
		}, 40);
	}

	function start() {
		if (!document.body || !window.MutationObserver) return;
		sweep(document.body);
		new MutationObserver(function (muts) {
			for (var i = 0; i < muts.length; i++) {
				var m = muts[i];
				if (m.type === "childList") {
					for (var j = 0; j < m.addedNodes.length; j++) schedule(m.addedNodes[j]);
				} else if (m.type === "characterData") {
					schedule(m.target);
				} else if (m.type === "attributes") {
					schedule(m.target);
				}
			}
		}).observe(document.body, {
			childList: true,
			subtree: true,
			characterData: true,
			attributes: true,
			attributeFilter: ATTRS,
		});
	}

	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
