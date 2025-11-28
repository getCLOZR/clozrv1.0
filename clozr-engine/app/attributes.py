# app/attributes.py

from typing import Dict, Any


def extract_attributes_from_raw(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    V0 heuristic extractor.
    Later, replace this with an LLM call that returns structured attributes.
    """
    title = (raw_json.get("title") or "").lower()
    body = (raw_json.get("body_html") or "").lower()
    tags = [t.lower() for t in raw_json.get("tags", [])]

    text = " ".join([title, body, " ".join(tags)])

    # Very rough heuristics just so we have *something* working
    category = None
    if "hoodie" in text:
        category = "hoodie"
    elif "jacket" in text:
        category = "jacket"
    elif "t-shirt" in text or "tee" in text:
        category = "t-shirt"

    warmth_level = None
    if any(w in text for w in ["fleece", "insulated", "puffer", "down"]):
        warmth_level = "high"
    elif "lightweight" in text:
        warmth_level = "low"

    primary_use = []
    if "winter" in text:
        primary_use.append("winter")
    if "campus" in text or "class" in text:
        primary_use.append("campus")
    if "running" in text or "gym" in text:
        primary_use.append("sport")

    # This is the shape expected by ProductAttributes
    return {
        "category": category,
        "style": None,          # TODO LLM later
        "warmth_level": warmth_level,
        "fit": None,            # TODO LLM later
        "material_main": None,  # TODO LLM later
        "price_band": None,     # TODO LLM later
        "primary_use": primary_use or None,
        "metadata": {},         # space for extra stuff
    }
