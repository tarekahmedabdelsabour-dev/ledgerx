"""No "ERPNext" anywhere the customer can read it.

Three layers cover everything without touching ERPNext's own files (its updates keep working):

  1. Desk (the logged-in interface): ledgerx.js rewrites text, tooltips and placeholders as they
     appear on screen.
  2. Server-rendered pages (login, website, portal, web forms, error pages, setup wizard shell):
     this module rewrites the HTML of every response on its way out.
  3. Stored settings and templates (System Settings app name, e-mail footer, website footer): see
     install.py and templates/.

The rewrite below is deliberately conservative: only *visible text* and the visible attributes
(title, alt, placeholder, aria-label, meta content) are touched. <script>, <style> and comments are
never changed, because the desk page carries its boot data (doctype and route names such as
"ERPNext Settings") inside a script and renaming those would break navigation. Paths that carry
real documents or data (API, files, print views) are skipped as well.
"""

import re

BRAND = "LedgerX"

# "ERPNext", "ERP Next" - exact capitalisation of the product name only, never "erpnext" (module and
# route identifiers) so nothing technical is renamed by accident.
NAME = re.compile(r"\bERP ?Next\b")

TOKEN = re.compile(r"(<script\b.*?</script\s*>|<style\b.*?</style\s*>|<!--.*?-->|<[^>]*>)", re.S | re.I)
ATTR = re.compile(r'(\b(?:title|alt|placeholder|aria-label|data-original-title|content)\s*=\s*")([^"]*)(")', re.I)

SKIP_PREFIXES = ("/api/", "/files/", "/private/", "/assets/", "/printview", "/crm", "/app/print", "/backups")
MAX_BYTES = 3 * 1024 * 1024


def rebrand_text(text):
	return NAME.sub(BRAND, text)


def rebrand_html(html):
	"""Return `html` (str) with the product name replaced in visible text only."""
	if "ERP" not in html:
		return html
	out = []
	for tok in TOKEN.split(html):
		if not tok:
			continue
		if tok.startswith("<"):
			low = tok[:8].lower()
			if low.startswith(("<script", "<style", "<!--")):
				out.append(tok)
			elif "ERP" in tok:
				out.append(ATTR.sub(lambda m: m.group(1) + rebrand_text(m.group(2)) + m.group(3), tok))
			else:
				out.append(tok)
		else:
			out.append(rebrand_text(tok))
	return "".join(out)


def should_skip(path):
	path = path or ""
	return path.startswith(SKIP_PREFIXES)


def after_request(response=None, request=None):
	"""Frappe `after_request` hook. Must never break a response."""
	try:
		if response is None or request is None or should_skip(request.path):
			return
		if "text/html" not in (response.headers.get("Content-Type") or ""):
			return
		if getattr(response, "direct_passthrough", False) or response.status_code != 200:
			return
		data = response.get_data()
		if len(data) > MAX_BYTES or b"ERP" not in data:
			return
		new = rebrand_html(data.decode("utf-8")).encode("utf-8")
		if new != data:
			response.set_data(new)
	except Exception:
		pass
