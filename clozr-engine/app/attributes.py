# app/attributes.py

# from typing import Dict, Any

# app/services/attributes.py

from typing import List, Optional
from typing import List, Optional, Dict, Any

# import re

def infer_category(title: str, product_type: Optional[str], tags: List[str]) -> Optional[str]:
    text = " ".join(
        [title or "", product_type or "", " ".join(tags or [])]
    ).lower()

    # Jackets / outerwear
    if any(k in text for k in ["puffer", "parka", "jacket", "shell", "coat"]):
        return "jacket"

    # Hoodies / sweatshirts
    if any(k in text for k in ["hoodie", "hooded", "fleece", "pullover", "crewneck", "sweatshirt"]):
        return "hoodie"

    # T-shirts
    if any(k in text for k in ["t-shirt", "t shirt", "tee", "graphic tee"]):
        return "t-shirt"

    # Long sleeves / shirts
    if any(k in text for k in ["long sleeve", "flannel", "oxford", "button down", "shirt"]):
        return "shirt"

    # Pants
    if any(k in text for k in ["pants", "trouser", "jogger", "chino", "jean"]):
        return "pants"

    # Sweaters
    if any(k in text for k in ["sweater", "cardigan", "knit"]):
        return "sweater"

    return None


def extract_product_attributes(raw: dict) -> dict:
    title = raw.get("title", "")
    product_type = raw.get("product_type")
    tags_raw = raw.get("tags") or ""
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    category = infer_category(title, product_type, tags)

    primary_use: List[str] = []
    text = " ".join([title or "", raw.get("body_html") or "", tags_raw]).lower()

    if any(k in text for k in ["winter", "snow", "cold", "fleece", "parka", "puffer"]):
        primary_use.append("winter")
    if any(k in text for k in ["campus", "class", "college", "everyday", "daily"]):
        primary_use.append("campus")
    if any(k in text for k in ["running", "jog", "training", "gym"]):
        primary_use.append("training")

    return {
        "category": category,
        "style": None,
        "warmth_level": "high" if "winter" in primary_use else None,
        "fit": None,
        "material_main": None,
        "price_band": None,
        "primary_use": primary_use or None,
        "extra_metadata": {},
    }


def extract_attributes_from_raw(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backwards-compatible wrapper used by the enrichment pipeline.
    Internally delegates to extract_product_attributes.
    """
    return extract_product_attributes(raw_json)