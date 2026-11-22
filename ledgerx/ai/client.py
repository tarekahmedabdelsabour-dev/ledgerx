"""The one place that talks to the network. Returns the parsed reply or raises AIError with a safe kind."""
import requests

from ledgerx.ai.engine import AIError

URL = "https://api.anthropic.com/v1/messages"
VERSION = "2023-06-01"


def kind_for_status(code):
	if code in (401, 403):
		return "auth"
	if code == 429:
		return "busy"
	if code >= 500:
		return "down"
	return "bad"


def make_post(api_key, timeout=90, session=None):
	http = session or requests
	headers = {"x-api-key": api_key, "anthropic-version": VERSION, "content-type": "application/json"}

	def post(payload):
		try:
			r = http.post(URL, json=payload, headers=headers, timeout=timeout)
		except requests.Timeout:
			raise AIError("slow")
		except requests.ConnectionError:
			raise AIError("net")
		except requests.RequestException:
			raise AIError("bad", "request failed")
		if r.status_code != 200:
			# the body of an error reply never holds our key, but keep only a short tail for the log
			raise AIError(kind_for_status(r.status_code), "HTTP %s %s" % (r.status_code, (r.text or "")[:300]))
		try:
			return r.json()
		except ValueError:
			raise AIError("bad", "not json")

	return post
