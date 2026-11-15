/* Small Arabic / English switch on every desk and website page.
   Signed-in users: saves the language on their user and reloads. Guests: sets the language cookie. */
(function () {
	"use strict";
	if (window.__lxLang) return;
	window.__lxLang = true;

	function current() {
		var f = window.frappe || {};
		var l = (f.boot && f.boot.lang) || f.lang || document.documentElement.lang || "en";
		return String(l).toLowerCase().indexOf("ar") === 0 ? "ar" : "en";
	}

	function isGuest() {
		var f = window.frappe || {};
		var u = (f.session && f.session.user) || (f.boot && f.boot.user && f.boot.user.name) || "Guest";
		return u === "Guest";
	}

	function switchTo(lang) {
		var f = window.frappe;
		if (!isGuest() && f && f.call) {
			f.call({
				method: "frappe.client.set_value",
				args: { doctype: "User", name: f.session.user, fieldname: "language", value: lang },
				callback: function () { window.location.reload(); },
				error: function () { if (f.msgprint) f.msgprint(lang === "ar" ? "تعذر تغيير اللغة" : "Could not change the language"); },
			});
			return;
		}
		document.cookie = "preferred_language=" + lang + "; path=/; max-age=31536000; SameSite=Lax";
		window.location.reload();
	}

	function build() {
		var cur = current();
		var target = cur === "ar" ? "en" : "ar";
		var el = document.createElement("button");
		el.type = "button";
		el.id = "lx-lang-switch";
		el.textContent = target === "en" ? "EN" : "عربي";
		el.title = target === "en" ? "Switch to English" : "التبديل إلى العربية";
		el.setAttribute("aria-label", el.title);
		el.addEventListener("click", function () { switchTo(target); });
		return el;
	}

	function mount() {
		if (!document.body || document.getElementById("lx-lang-switch")) return;
		var btn = build();
		btn.className = "lx-lang-floating";
		document.body.appendChild(btn);
	}

	function start() {
		mount();
		// keep it alive: the desk re-renders its page, so put the button back if it ever disappears
		setInterval(mount, 1500);
	}

	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
