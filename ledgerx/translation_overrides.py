"""Corrected Arabic for apps whose own translation files are partial or wrong.

Every app ships its own ar.po / ar.csv, and the app installed last wins over the ones before it. So a
correction written in *this* app's translations/ar.csv would lose to the Lending app's own file (that
is how "Haircut %" stayed "حلاقة شعر"). Frappe applies the Translation records stored in the database
after every app file, so the corrected texts are synced there on each migrate.

Source files: translations_data/*.json  ({"English": "العربية"}). Edit a file and run migrate: changed
texts are updated, new ones added, nothing else in the Translation list is touched.
"""
import glob
import hashlib
import json
import os

import frappe

LANG = "ar"
SETTING = "ledgerx_translation_overrides_hash"


def _load():
	merged = {}
	folder = os.path.join(os.path.dirname(__file__), "translations_data")
	for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
		with open(path, encoding="utf-8") as f:
			merged.update(json.load(f))
	return merged


def apply():
	data = _load()
	if not data:
		return
	digest = hashlib.sha1(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
	if frappe.db.get_default(SETTING) == digest:
		return

	existing = {
		r.source_text: r
		for r in frappe.get_all(
			"Translation", filters={"language": LANG}, fields=["name", "source_text", "translated_text", "context"]
		)
		if not r.context
	}
	added = changed = 0
	for source, text in data.items():
		row = existing.get(source)
		if row is None:
			frappe.get_doc(
				{"doctype": "Translation", "language": LANG, "source_text": source, "translated_text": text}
			).insert(ignore_permissions=True)
			added += 1
		elif row.translated_text != text:
			frappe.db.set_value("Translation", row.name, "translated_text", text)
			changed += 1

	frappe.db.set_default(SETTING, digest)
	frappe.db.commit()
	from frappe.translate import clear_cache

	clear_cache()
	print(f"LedgerX translations: {added} added, {changed} updated")
