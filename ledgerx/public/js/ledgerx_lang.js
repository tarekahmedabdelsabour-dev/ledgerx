/* LedgerX language switch (Arabic <-> English), one small tab on every desk, website, CRM and HR page.
   Draws its own style so the same file works everywhere. Drag it anywhere; it remembers the place. */
(function () {
	"use strict";
	if (window.__lxLang) return;
	window.__lxLang = true;

	var POS_KEY = "lx-lang-pos";

	function css() {
		if (document.getElementById("lx-lang-style")) return;
		var s = document.createElement("style");
		s.id = "lx-lang-style";
		s.textContent =
			"#lx-lang-switch{all:unset;box-sizing:border-box;position:fixed;top:0;inset-inline-end:132px;z-index:100000;" +
			"display:inline-flex;align-items:center;gap:5px;height:20px;padding:0 10px 1px;cursor:pointer;user-select:none;" +
			"font:700 11px/1 'InterVariable','Inter','Cairo','Tajawal','Segoe UI',system-ui,sans-serif;letter-spacing:.03em;" +
			"color:#fff;background:linear-gradient(135deg,#0b2a5b 0%,#0b5e78 60%,#14b8a6 100%);" +
			"border-radius:0 0 9px 9px;box-shadow:0 2px 6px rgba(7,26,58,.28);opacity:.92;transition:opacity .15s,height .15s,box-shadow .15s}" +
			"#lx-lang-switch:hover{opacity:1;height:24px;box-shadow:0 4px 10px rgba(7,26,58,.35)}" +
			"#lx-lang-switch:focus-visible{outline:2px solid #ffd166;outline-offset:1px}" +
			"#lx-lang-switch svg{width:12px;height:12px;stroke:#ffd166;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}" +
			"#lx-lang-switch.lx-dragging{cursor:grabbing;opacity:1}" +
			"@media print{#lx-lang-switch{display:none}}";
		(document.head || document.documentElement).appendChild(s);
	}

	function current() {
		var f = window.frappe || {};
		var l = document.documentElement.getAttribute("lang") || (f.boot && f.boot.lang) || f.lang || "en";
		return String(l).toLowerCase().indexOf("ar") === 0 ? "ar" : "en";
	}

	function csrf() {
		var f = window.frappe || {};
		return window.csrf_token || f.csrf_token || (f.boot && f.boot.csrf_token) || "";
	}

	function isGuest() {
		var f = window.frappe || {};
		var u = (f.session && f.session.user) || "";
		if (!u) { var m = document.cookie.match(/(?:^|;\s*)user_id=([^;]*)/); u = m ? decodeURIComponent(m[1]) : "Guest"; }
		return u === "Guest";
	}

	// Same effect as Ctrl+Shift+R: drop the browser's cached copies, re-fetch this page uncached, then reload.
	function done(lang) {
		document.cookie = "preferred_language=" + lang + "; path=/; max-age=31536000; SameSite=Lax";
		var jobs = [];
		try { if (window.caches) jobs.push(caches.keys().then(function (k) { return Promise.all(k.map(function (n) { return caches.delete(n); })); })); } catch (e) {}
		try {
			if (navigator.serviceWorker) jobs.push(navigator.serviceWorker.getRegistrations().then(function (r) { return Promise.all(r.map(function (x) { return x.unregister(); })); }));
		} catch (e) {}
		try {
			if (window.indexedDB && indexedDB.databases) jobs.push(indexedDB.databases().then(function (d) { d.forEach(function (x) { if (x.name) indexedDB.deleteDatabase(x.name); }); }));
		} catch (e) {}
		// The desk keeps doctype and page definitions (with their translated texts) in localStorage and only
		// drops them on a version change or a quick double reload: drop them now, the way a hard reload does.
		try {
			["_last_load", "_version_number", "metadata_version", "page_info", "last_visited"].forEach(function (k) { localStorage.removeItem(k); });
			Object.keys(localStorage).forEach(function (k) {
				if (/^_page:|^_doctype:|^_report:|translat|messages|boot/i.test(k)) localStorage.removeItem(k);
			});
		} catch (e) {}
		try { sessionStorage.clear(); } catch (e) {}
		// API answers the browser kept (translated labels, sidebar, counts): fetch each again, bypassing its cache.
		try {
			var seen = {};
			performance.getEntriesByType("resource").forEach(function (r) {
				var u = r.name;
				if (u.indexOf(location.origin) === 0 && u.indexOf("/api/") > -1 && !seen[u] && Object.keys(seen).length < 80) {
					seen[u] = 1;
					jobs.push(fetch(u, { cache: "reload", credentials: "same-origin" }));
				}
			});
		} catch (e) {}
		try { jobs.push(fetch(location.href, { cache: "reload", credentials: "same-origin" })); } catch (e) {}
		var fired = false, go = function () { if (fired) return; fired = true; window.location.reload(); };
		Promise.all(jobs.map(function (p) { return p.catch(function () {}); })).then(go, go);
		setTimeout(go, 2500);
	}

	function post(lang, token) {
		return fetch("/api/method/ledgerx.api.lang.set_language", {
			method: "POST", credentials: "same-origin",
			headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": token, Accept: "application/json" },
			body: JSON.stringify({ lang: lang }),
		});
	}

	function switchTo(lang) {
		if (isGuest()) return done(lang);
		var token = csrf();
		var go = function (t) { post(lang, t).then(function () { done(lang); }, function () { done(lang); }); };
		if (token && token !== "{{ csrf_token }}") return go(token);
		fetch("/api/method/ledgerx.api.lang.csrf", { credentials: "same-origin" })
			.then(function (r) { return r.json(); })
			.then(function (j) { go((j && j.message) || ""); }, function () { done(lang); });
	}

	function place(el) {
		try {
			var p = JSON.parse(localStorage.getItem(POS_KEY) || "null");
			if (p && typeof p.x === "number") {
				el.style.insetInlineEnd = "auto";
				el.style.left = Math.min(Math.max(0, p.x), window.innerWidth - 40) + "px";
				el.style.top = Math.min(Math.max(0, p.y), window.innerHeight - 24) + "px";
			}
		} catch (e) {}
	}

	function drag(el) {
		var sx, sy, ox, oy, moved = false, active = false;
		el.addEventListener("pointerdown", function (e) {
			if (e.button) return;
			var r = el.getBoundingClientRect();
			sx = e.clientX; sy = e.clientY; ox = r.left; oy = r.top; moved = false; active = true;
		});
		window.addEventListener("pointermove", function (e) {
			if (!active) return;
			var dx = e.clientX - sx, dy = e.clientY - sy;
			if (!moved && Math.abs(dx) + Math.abs(dy) < 6) return;
			moved = true; el.classList.add("lx-dragging");
			el.style.insetInlineEnd = "auto";
			el.style.left = Math.min(Math.max(0, ox + dx), window.innerWidth - 40) + "px";
			el.style.top = Math.min(Math.max(0, oy + dy), window.innerHeight - 24) + "px";
		});
		window.addEventListener("pointerup", function () {
			if (!active) return;
			active = false; el.classList.remove("lx-dragging");
			if (moved) {
				var r = el.getBoundingClientRect();
				try { localStorage.setItem(POS_KEY, JSON.stringify({ x: r.left, y: r.top })); } catch (e) {}
				el.setAttribute("data-moved", "1");
				setTimeout(function () { el.removeAttribute("data-moved"); }, 50);
			}
		});
	}

	function label(el) {
		var target = current() === "ar" ? "en" : "ar";
		if (el.getAttribute("data-target") === target) return;
		el.setAttribute("data-target", target);
		var text = target === "en" ? "EN" : "عربي";
		el.title = target === "en" ? "Switch to English" : "التبديل إلى العربية";
		el.setAttribute("aria-label", el.title);
		el.innerHTML = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 2.6 15.3 0 18M12 3c-2.6 2.7-2.6 15.3 0 18"/></svg><span></span>';
		el.lastChild.textContent = text;
	}

	function mount() {
		if (!document.body) return;
		css();
		var el = document.getElementById("lx-lang-switch");
		if (!el) {
			el = document.createElement("button");
			el.id = "lx-lang-switch";
			el.type = "button";
			el.addEventListener("click", function () {
				if (el.getAttribute("data-moved")) return;
				switchTo(el.getAttribute("data-target"));
			});
			place(el);
			drag(el);
			document.body.appendChild(el);
		}
		label(el);
	}

	function start() {
		mount();
		setInterval(mount, 1200); // the desk redraws its page; also picks up the language once the app knows it
	}

	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
