import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.getenv("OPENAI_OVERVIEW_MODEL", "gpt-4o-mini")


def generate_short_overview(raw_json: dict, attrs: dict | None) -> str:
    raw_json = raw_json or {}
    attrs = attrs or {}

    title = raw_json.get("title", "") or ""
    vendor = raw_json.get("vendor", "") or ""
    product_type = raw_json.get("product_type", "") or ""
    tags = raw_json.get("tags", "") or ""
    body = (raw_json.get("body_html", "") or "")[:1200]
    variants = raw_json.get("variants") or []

    v0 = variants[0] if variants else {}
    price = v0.get("price")
    variant_title = v0.get("title")

    # “facts” keeps the model grounded (don’t dump full JSON)
    facts = {
        "title": title,
        "vendor": vendor,
        "product_type": product_type,
        "tags": tags,
        "description": body,
        "example_variant": {"title": variant_title, "price": price},
        "inferred_attributes": attrs,
    }

    system = (
        "You are CLOZR. Write a customer-friendly overview paragraph for a product page. "
        "Use ONLY the provided facts. Do not guess. "
        "2–3 sentences max. No bullet points. No emojis. No tags list."
    )

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"FACTS:\n{facts}\n\nWrite the overview."},
        ],
        temperature=0.2,
    )

    text = (resp.output_text or "").strip()

    # Safety: keep it short
    if len(text) > 450:
        text = text[:450].rsplit(" ", 1)[0].strip() + "…"

    return text
