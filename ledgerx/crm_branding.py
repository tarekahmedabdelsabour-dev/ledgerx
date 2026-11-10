"""LedgerX identity inside the CRM app (served at /crm).

Frappe CRM is a standalone single-page app: it does not load the desk bundles, so the desk branding
(ledgerx.js / ledgerx.css) never reaches it. Instead, every HTML response for /crm gets three things
injected into <head>, without touching the CRM app's own files (its updates keep working):

  * a tiny inline script that switches the PWA service worker off (it would otherwise keep serving a
    cached copy of the page, without our additions),
  * ledgerx_crm.css  - logos (CSS only, so Vue never notices) and hidden Frappe links,
  * ledgerx_crm.js   - names ("Frappe CRM" -> "LedgerX CRM", "ERPNext" -> "LedgerX"), title and favicon.

Legal notices (the copyright line in the About dialog) are left as they are on purpose.
"""

from ledgerx import __version__

SW_OFF = (
	b"<script>try{if('serviceWorker' in navigator){navigator.serviceWorker.getRegistrations()"
	b".then(function(r){r.forEach(function(x){x.unregister()})});"
	b"navigator.serviceWorker.register=function(){return Promise.resolve()};"
	b"if(window.caches){caches.keys().then(function(k){k.forEach(function(n){caches.delete(n)})})}}}"
	b"catch(e){}</script>"
)


def is_crm_path(path):
	path = (path or "").rstrip("/")
	return path == "/crm" or path.startswith("/crm/")


def inject(html):
	"""Return `html` (bytes) with the LedgerX tags added, or unchanged when it is not the CRM shell."""
	if b"</head>" not in html or b"<head" not in html:
		return html
	v = __version__.encode()
	tail = (
		b'<link rel="icon" href="/assets/ledgerx/images/ledgerx-favicon.svg">'
		b'<link rel="stylesheet" href="/assets/ledgerx/css/ledgerx_crm.css?v=' + v + b'">'
		b'<script src="/assets/ledgerx/js/ledgerx_crm.js?v=' + v + b'" defer></script>'
	)
	html = html.replace(b"<title>Frappe CRM</title>", b"<title>LedgerX CRM</title>")
	head_at = html.find(b"<head")
	end_of_open = html.find(b">", head_at) + 1
	html = html[:end_of_open] + SW_OFF + html[end_of_open:]
	return html.replace(b"</head>", tail + b"</head>", 1)


def after_request(response=None, request=None):
	"""Frappe `after_request` hook. Must never break a response."""
	try:
		if response is None or request is None or not is_crm_path(request.path):
			return
		if "text/html" not in (response.headers.get("Content-Type") or ""):
			return
		if getattr(response, "direct_passthrough", False):
			return
		data = response.get_data()
		new = inject(data)
		if new != data:
			response.set_data(new)
	except Exception:
		pass
