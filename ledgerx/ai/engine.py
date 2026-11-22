"""The conversation loop with the model. The network call and the tools are passed in, so it is tested without either."""
import json

MAX_TOOL_RESULT = 14000
MAX_HISTORY = 8

MSG = {
	"ar": {
		"auth": "مفتاح الذكاء الاصطناعي مرفوض. اطلب من مدير النظام مراجعته في إعدادات المساعد.",
		"busy": "الخدمة مشغولة الآن. جرّب بعد دقيقة.",
		"down": "خدمة الذكاء الاصطناعي غير متاحة حاليًا. جرّب لاحقًا.",
		"net": "تعذّر الوصول إلى خدمة الذكاء الاصطناعي. راجع اتصال السيرفر بالإنترنت.",
		"slow": "الرد تأخر أكتر من اللازم. جرّب سؤال أبسط.",
		"bad": "تعذّر تنفيذ الطلب.",
		"loop": "السؤال محتاج خطوات أكتر من المسموح. جرّب تقسّمه لأسئلة أصغر.",
	},
	"en": {
		"auth": "The AI key was rejected. Ask an administrator to check it in the assistant settings.",
		"busy": "The service is busy right now. Try again in a minute.",
		"down": "The AI service is unavailable at the moment. Try again later.",
		"net": "Could not reach the AI service. Check the server's internet connection.",
		"slow": "The reply took too long. Try a simpler question.",
		"bad": "The request could not be completed.",
		"loop": "The question needs more steps than allowed. Try splitting it.",
	},
}


class AIError(Exception):
	"""A failure whose message is safe to show to the user."""

	def __init__(self, kind, detail=""):
		super().__init__(kind)
		self.kind = kind
		self.detail = detail  # for the error log only; never shown, never holds the key


def message(kind, lang):
	return MSG["ar" if (lang or "ar").startswith("ar") else "en"].get(kind) or MSG["en"]["bad"]


def clean_history(history):
	"""Last turns as plain text, starting with a user turn and alternating, as the API requires."""
	out = []
	for h in history or []:
		role = h.get("role") if isinstance(h, dict) else None
		text = h.get("content") if isinstance(h, dict) else None
		if role not in ("user", "assistant") or not isinstance(text, str) or not text.strip():
			continue
		if out and out[-1]["role"] == role:
			out[-1]["content"] += "\n" + text.strip()
		else:
			out.append({"role": role, "content": text.strip()[:4000]})
	out = out[-MAX_HISTORY:]
	while out and out[0]["role"] != "user":
		out.pop(0)
	if out and out[-1]["role"] == "user":
		out.pop()  # the new question follows; two user turns in a row would be merged anyway
	return out


def run(post, tools, system, history, question, model, max_tokens, lang="ar", max_steps=6):
	"""Ask, let the model call tools until it answers. Returns {answer, usage, steps}."""
	messages = clean_history(history) + [{"role": "user", "content": question}]
	usage = {"input": 0, "output": 0, "cache_read": 0}
	text = ""
	for step in range(1, max_steps + 1):
		payload = {
			"model": model, "max_tokens": max_tokens,
			"system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
			"tools": tools.specs, "messages": messages,
		}
		resp = post(payload)
		u = resp.get("usage") or {}
		usage["input"] += u.get("input_tokens", 0) or 0
		usage["output"] += u.get("output_tokens", 0) or 0
		usage["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
		blocks = resp.get("content") or []
		text = "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
		calls = [b for b in blocks if b.get("type") == "tool_use"]
		if resp.get("stop_reason") != "tool_use" or not calls:
			return _finish(text, tools, usage, step, lang)
		messages.append({"role": "assistant", "content": blocks})
		results = []
		for c in calls:
			payload_out, is_error = tools.call(c.get("name"), c.get("input") or {})
			body = json.dumps(payload_out, ensure_ascii=False, default=str)
			if len(body) > MAX_TOOL_RESULT:
				body = body[:MAX_TOOL_RESULT] + ' ...[cut]'
			res = {"type": "tool_result", "tool_use_id": c.get("id"), "content": body}
			if is_error:
				res["is_error"] = True
			results.append(res)
		messages.append({"role": "user", "content": results})
	return _finish(text or message("loop", lang), tools, usage, max_steps, lang)


def _finish(text, tools, usage, steps, lang):
	from ledgerx.ai.safety import denied_text

	# Asked about something outside the user's rights and nothing readable came back: the reply is the fixed refusal,
	# whatever the model wrote, so a model slip can never turn it into a hint about the data.
	if getattr(tools, "denied", 0) and not getattr(tools, "data_ok", 0):
		text = denied_text(lang)
	return {"answer": text or message("bad", lang), "usage": usage, "steps": steps}
