import os

import openai

from .lead_scoring import score_lead_metadata


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def _openai_chat(prompt: str, max_tokens: int = 250) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for AI features")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly Indian digital growth expert helping local businesses with business websites, SEO, WhatsApp, SMS, and email outreach."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_lead_score(lead: dict) -> dict:
    basic = score_lead_metadata(lead.get("rating"), lead.get("review_count"), lead.get("website"))

    if not OPENAI_API_KEY:
        return basic

    try:
        prompt = (
            "Evaluate this local business lead for website and digital growth readiness. "
            f"Business name: {lead.get('business_name')}\n"
            f"Category: {lead.get('category')}\n"
            f"City: {lead.get('city')}\n"
            f"Rating: {lead.get('rating') or 'unknown'}\n"
            f"Review count: {lead.get('review_count') or 'unknown'}\n"
            f"Website: {lead.get('website') or 'none'}\n"
            "Respond in JSON with keys: score, website_need_score, business_potential, digital_gaps, priority, pitch_angle. "
            "Keep values short and numeric where applicable."
        )
        ai_text = _openai_chat(prompt)
        import json

        payload = json.loads(ai_text)
        for key in ["score", "website_need_score", "business_potential"]:
            if key in payload:
                payload[key] = int(payload[key])
        payload.setdefault("priority", basic["priority"])
        payload.setdefault("digital_gaps", basic["digital_gaps"])
        payload.setdefault("pitch_angle", basic["pitch_angle"])
        return payload
    except Exception:
        return basic


def generate_outreach_message(lead: dict) -> str:
    if not OPENAI_API_KEY:
        return (
            f"Hi {lead.get('business_name')}, I saw your {lead.get('category')} in {lead.get('city')}. "
            "I can build a modern website and WhatsApp booking system for your business to convert more customers. "
            "Would you like a quick proposal?"
        )

    prompt = (
        "Compose a short, friendly, natural outreach message in Hindi or Hinglish for a local business. "
        f"Business: {lead.get('business_name')}\n"
        f"Category: {lead.get('category')}\n"
        f"City: {lead.get('city')}\n"
        f"Website: {lead.get('website') or 'no website'}\n"
        "Mention missing website or online growth opportunity, keep the tone professional, and include a clear call to action. "
        "Return only the message text."
    )
    return _openai_chat(prompt, max_tokens=120)


def generate_support_reply(question: str, lead: dict | None = None) -> str:
    if not OPENAI_API_KEY:
        return (
            "Thanks for your message. We help restaurants, salons, gyms, clinics, and local stores with websites, SEO, Google Business, "
            "WhatsApp integration, and booking systems. Please share your business details and budget so we can help."
        )

    context = "" if not lead else f"Lead business: {lead.get('business_name')} in {lead.get('city')}.\n"
    prompt = (
        "You are a friendly Indian business consultant. Answer the customer query in Hindi/Hinglish when appropriate, "
        "keep it professional and helpful, explain digital growth services, and suggest booking a call. "
        f"Context:\n{context}\nQuestion: {question}"
    )
    return _openai_chat(prompt, max_tokens=180)
