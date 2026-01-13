import os
from openai import OpenAI
from app.prompts.render_overview_prompt import render_overview_system_prompt
import json



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = os.getenv("OPENAI_OVERVIEW_MODEL", "gpt-4o-mini")



PROMPT_VERSION = "v1.0"



def generate_short_overview(raw_json: dict, attrs: dict | None) -> str:
    raw_json = raw_json or {}
    attrs = attrs or {}

    title = raw_json.get("title", "") or ""
    vendor = raw_json.get("vendor", "") or ""
    product_type = raw_json.get("product_type", "") or ""
    body = (raw_json.get("body_html", "") or "")[:1200]
    variants = raw_json.get("variants") or []

    v0 = variants[0] if variants else {}
    price = v0.get("price")
    variant_title = v0.get("title")

    facts = {
        "title": title,
        "vendor": vendor,
        "product_type": product_type,
        "description": body,
        "example_variant": {"title": variant_title, "price": price},
        "inferred_attributes": attrs,
    }

    # system = (
    #     "You are CLOZR. Write a customer-friendly overview paragraph for a product page. "
    #     "Use ONLY the provided facts. Do not guess. "
    #     "2–3 sentences max. No bullet points. No emojis. No tags list."
    # )

    system_prompt = render_overview_system_prompt()

    user_message = f"""FACTS:
{json.dumps(facts, indent=2)}

Select ONE concrete, product-specific fact from the above data.
Write a 1-sentence overview (15-25 words) that highlights this fact.
Use simple, neutral language. No marketing words."""

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    text = (resp.output_text or "").strip()

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
        "description": body,
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

        return text
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"Error in generate_chat_response: {str(e)}")
        print(traceback.format_exc())
        # Fallback response if LLM fails
        return f"I apologize, but I'm having trouble processing your question right now. Please try again in a moment."  # noqa: F541
    

def generate_suggested_questions(raw_json: dict, attrs: dict | None) -> list[str]:

    raw_json = raw_json or {}
    attrs = attrs or {}

    title = raw_json.get("title", "") or ""
    vendor = raw_json.get("vendor", "") or ""
    product_type = raw_json.get("product_type", "") or ""
    body = (raw_json.get("body_html", "") or "")[:900]
    tags = raw_json.get("tags", "") or ""
    variants = raw_json.get("variants") or []
    options = raw_json.get("options") or []

    v0 = variants[0] if variants else {}
    price = v0.get("price")
    variant_title = v0.get("title")

    facts = {
        "title": title,
        "vendor": vendor,
        "product_type": product_type,
        "tags": tags,
        "description": body,
        "options": options,
        "example_variant": {"title": variant_title, "price": price},
        "inferred_attributes": attrs,
    }

    fallback = [
        "What size/fit should I choose?",
        "What materials is this made from and how do I care for it?",
    ]

    system = """
You generate shopper questions for a product page.
Return ONLY a valid JSON array of exactly 2 strings, like:
["Question 1?", "Question 2?"]

Rules:
- Each question should be specific to the facts provided (materials, sizing, compatibility, what's included, care, use-case, etc.)
- If a key detail is missing, ask about it rather than guessing.
- No bullets, no extra text, no markdown.
""".strip()

    try:
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"FACTS:\n{facts}\n\nReturn the JSON array now."},
            ],
            temperature=0.2,
        )

        raw = (resp.output_text or "").strip()
        if not raw:
            return fallback

        questions = json.loads(raw)

        if not isinstance(questions, list):
            return fallback

        questions = [q.strip() for q in questions if isinstance(q, str) and q.strip()]
        if len(questions) < 2:
            questions += [q for q in fallback if q not in questions]
        return questions[:2]

    except Exception as e:
        print("QUESTION GEN ERROR:", repr(e))
        return fallback


