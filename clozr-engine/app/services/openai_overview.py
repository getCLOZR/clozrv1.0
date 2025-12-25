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


def generate_chat_response(
    product_id: str,
    shop_domain: str,
    initial_overview: str,
    question: str,
    raw_json: dict | None = None,
    attrs: dict | None = None,
) -> str:
    """
    Generate a product-aware chat response using LLM.
    Context includes the initial overview and product details.
    """
    raw_json = raw_json or {}
    attrs = attrs or {}

    title = raw_json.get("title", "") or ""
    vendor = raw_json.get("vendor", "") or ""
    product_type = raw_json.get("product_type", "") or ""
    tags = raw_json.get("tags", "") or ""
    body = (raw_json.get("body_html", "") or "")[:800]  # Shorter for chat context
    variants = raw_json.get("variants") or []

    v0 = variants[0] if variants else {}
    price = v0.get("price")
    variant_title = v0.get("title")

    # Build product context
    product_context = {
        "title": title,
        "vendor": vendor,
        "product_type": product_type,
        "tags": tags,
        "description": body[:600],  # Keep it concise
        "example_variant": {"title": variant_title, "price": price},
        "inferred_attributes": attrs,
    }

    system = (
        "You are CLOZR, a helpful product assistant for an ecommerce store. "
        "Answer the customer's question about the product based on the provided context. "
        "Be concise, helpful, and accurate. Use only the information provided. "
        "If you don't know something, say so. Keep responses to 2-3 sentences max. "
        "No emojis. Be professional and trustworthy."
    )

    user_message = (
        f"Product Context:\n{product_context}\n\n"
        f"Initial Product Overview:\n{initial_overview}\n\n"
        f"Customer Question: {question}\n\n"
        f"Answer the customer's question about this product."
    )

    try:
        # Use the same API pattern as generate_short_overview
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )

        text = (resp.output_text or "").strip()

        # Safety: keep it reasonable length
        if len(text) > 300:
            text = text[:300].rsplit(" ", 1)[0].strip() + "…"

        return text
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"Error in generate_chat_response: {str(e)}")
        print(traceback.format_exc())
        # Fallback response if LLM fails
        return f"I apologize, but I'm having trouble processing your question right now. Please try again in a moment."
