"""Language switch used by the CRM screen (the desk uses frappe.client.set_value directly)."""
import frappe


@frappe.whitelist(methods=["POST"])
def set_language(lang):
	if lang not in ("ar", "en"):
		frappe.throw("Unsupported language")
	if frappe.session.user == "Guest":
		return lang
	frappe.db.set_value("User", frappe.session.user, "language", lang)
	frappe.clear_document_cache("User", frappe.session.user)
	frappe.db.commit()
	frappe.local.cookie_manager.set_cookie("preferred_language", lang)
	return lang


@frappe.whitelist()
def csrf():
	"""CSRF token for the standalone screens (CRM / HR) that do not expose it to our script."""
	return frappe.sessions.get_csrf_token()
