"""The LedgerX guide as the assistant sees it: the same pages as /docs, searchable. No framework imports."""
import json
import re

SECTION = re.compile(r'\{id:"([\w-]+)",t:\{ar:"([^"]*)",en:"([^"]*)"\},p:\[')
PAGE = re.compile(r'\{id:"([\w-]+)",t:\{ar:"([^"]*)",en:"([^"]*)"\}\}')
HEADING = re.compile(r"^#{1,4}\s+(.*)$", re.M)
WORD = re.compile(r"[\w]+", re.U)
STOP = {"the", "a", "an", "of", "to", "in", "is", "and", "or", "for", "on", "how", "what", "do", "i", "my", "can", "من", "في", "على", "الى", "إلى", "عن", "ما", "هو", "هي", "ازاي", "إزاي", "كيف", "هل", "ده", "دي"}

# Which module(s) a guide page belongs to. A page with no entry (or whose modules are not installed) is general.
PAGE_MODULES = {
	"fleet": ["Fleet Management", "Fleet", "Fleet Maintenance", "Fleet Operations", "Fleet Tracking", "Fleet Reports"],
	"fieldsales": ["Field Sales"], "payments": ["Payment Network"], "hotels": ["Hotels"], "showroom": ["Showroom"],
	"education": ["Education"], "realestate": ["Real Estate"], "factory": ["Factory", "Manufacturing"],
	"research": ["Operations Research"], "pharmacy": ["Pharmacy"], "malls": ["Malls"], "einvoicing": ["E-Invoicing"],
	"store": ["Store"], "invoices": ["Accounts"], "journal": ["Accounts"], "acc-reports": ["Accounts"], "coa": ["Accounts"],
	"selling": ["Selling"], "buying": ["Buying"], "stock": ["Stock"], "pos": ["Selling", "Accounts"], "crm": ["CRM", "FCRM"],
	"hr": ["HR", "Payroll"], "projects": ["Projects"], "lending": ["Loan Management", "Lending"],
}


def norm(text):
	"""Lower case; Arabic letter variants and marks folded so a spelling difference does not hide a match."""
	t = (text or "").lower()
	t = re.sub(r"[\u064B-\u0652\u0640]", "", t)
	return t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")


def tokens(text):
	return [w for w in WORD.findall(norm(text)) if len(w) > 1 and w not in STOP]


def parse_body(js_text):
	"""`window.LXD.body.xx={...};` as a dict of page id -> markdown."""
	start = js_text.index("=", js_text.index("window.LXD.body")) + 1
	return json.loads(js_text[start:].strip().rstrip(";"))


def parse_structure(js_text):
	"""[{id, title:{ar,en}, pages:[{id, title:{ar,en}}]}] in reading order."""
	marks = [(m.start(), "s", m) for m in SECTION.finditer(js_text)] + [(m.start(), "p", m) for m in PAGE.finditer(js_text)]
	sections = []
	for _pos, kind, m in sorted(marks, key=lambda x: x[0]):
		entry = {"id": m.group(1), "title": {"ar": m.group(2), "en": m.group(3)}}
		if kind == "s":
			sections.append({**entry, "pages": []})
		elif sections:
			sections[-1]["pages"].append(entry)
	return sections


class Guide:
	def __init__(self, structure, bodies):
		self.structure = structure
		self.bodies = bodies  # {"ar": {id: md}, "en": {id: md}}
		self.titles = {p["id"]: p["title"] for s in structure for p in s["pages"]}
		self._chunks = {}

	@classmethod
	def from_files(cls, structure_js, ar_js, en_js):
		return cls(parse_structure(structure_js), {"ar": parse_body(ar_js), "en": parse_body(en_js)})

	def title(self, page, lang):
		t = self.titles.get(page) or {}
		return t.get(lang) or t.get("en") or page

	def toc(self, lang, allowed=None):
		"""One line per page: `id: title` (limited to `allowed` ids when given)."""
		out = []
		for s in self.structure:
			ids = [p for p in s["pages"] if allowed is None or p["id"] in allowed]
			if ids:
				out.append("%s: %s" % (s["title"].get(lang) or s["title"]["en"], "; ".join("%s=%s" % (p["id"], p["title"].get(lang) or p["title"]["en"]) for p in ids)))
		return out

	def chunks(self, lang):
		"""[(page id, heading, text)] split at the headings of each page."""
		if lang in self._chunks:
			return self._chunks[lang]
		out = []
		for page, md in self.bodies.get(lang, {}).items():
			parts = HEADING.split(md)
			# split() with one group gives [intro, h1, body1, h2, body2, ...]
			if parts[0].strip():
				out.append((page, self.title(page, lang), parts[0].strip()))
			for i in range(1, len(parts) - 1, 2):
				out.append((page, parts[i].strip(), parts[i + 1].strip()))
		self._chunks[lang] = out
		return out

	def search(self, query, lang, allowed=None, limit=5, max_chars=1100):
		"""Best matching passages: [{page, title, heading, text}]. Tries the user's language, then the other."""
		q = tokens(query)
		if not q:
			return []
		results = []
		for lg in (lang, "en" if lang == "ar" else "ar"):
			scored = []
			for page, heading, text in self.chunks(lg):
				if allowed is not None and page not in allowed:
					continue
				h, t = norm(heading + " " + self.title(page, lg)), norm(text)
				score = sum(5 for w in q if w in h) + sum(min(t.count(w), 4) for w in q)
				if score:
					scored.append((score, page, heading, text))
			scored.sort(key=lambda x: -x[0])
			for _s, page, heading, text in scored[:limit]:
				results.append({"page": page, "title": self.title(page, lg), "heading": heading, "text": text[:max_chars]})
			if len(results) >= 2:
				break
		return results[:limit]

	def page(self, page, lang, max_chars=7000):
		for lg in (lang, "en" if lang == "ar" else "ar"):
			md = self.bodies.get(lg, {}).get(page)
			if md:
				return {"page": page, "title": self.title(page, lg), "text": md[:max_chars], "truncated": len(md) > max_chars}
		return None
