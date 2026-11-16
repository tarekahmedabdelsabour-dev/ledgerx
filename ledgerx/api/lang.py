"""Language switch used by the CRM screen (the desk uses frappe.client.set_value directly)."""
import frappe


@frappe.whitelist(methods=["POST"])
def set_language(lang):
	if lang not in ("ar", "en"):
		frappe.throw("Unsupported language")
	if frappe.session.user == "Guest":
		return lang
	# a normal save (not db.set_value): it clears the user's cached boot data, which holds the translated texts
	user = frappe.get_doc("User", frappe.session.user)
	user.language = lang
	user.flags.ignore_permissions = True
	user.save()
	frappe.clear_cache(user=frappe.session.user)
	frappe.db.commit()
	frappe.local.cookie_manager.set_cookie("preferred_language", lang)
	return lang


@frappe.whitelist()
def csrf():
	"""CSRF token for the standalone screens (CRM / HR) that do not expose it to our script."""
	return frappe.sessions.get_csrf_token()
