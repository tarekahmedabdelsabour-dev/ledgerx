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
})();
