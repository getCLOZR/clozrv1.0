# app/services/product_services.py
from sqlalchemy.orm import Session
from app import models
from app.attributes import extract_attributes_from_raw
from typing import Optional, List, Tuple
from uuid import UUID


def get_or_create_merchant(db: Session, shop_domain: str) -> models.Merchant:
    merchant = db.query(models.Merchant).filter_by(shop_domain=shop_domain).first()
    if merchant:
        return merchant
    merchant = models.Merchant(shop_domain=shop_domain)
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


def ingest_product(db: Session, merchant_domain: str, shop_product_id: str, raw_json: dict) -> models.ProductRaw:
    merchant = get_or_create_merchant(db, merchant_domain)
    product = models.ProductRaw(
        merchant_id=merchant.id,
        shop_product_id=shop_product_id,
        raw_json=raw_json,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # 2) extract attributes (V0 heuristics; later LLM)
    attrs = extract_attributes_from_raw(raw_json)

    product_attrs = models.ProductAttributes(
        product_id=product.id,
        category=attrs.get("category"),
        style=attrs.get("style"),
        warmth_level=attrs.get("warmth_level"),
        fit=attrs.get("fit"),
        material_main=attrs.get("material_main"),
        price_band=attrs.get("price_band"),
        primary_use=attrs.get("primary_use"),
        extra_metadata=attrs.get("metadata"),
    )
    db.add(product_attrs)
    db.commit()

    return product


def get_product_with_attributes(db: Session, product_id: UUID) -> Optional[tuple[models.ProductRaw, Optional[models.ProductAttributes]]]:
    """
    Returns (ProductRaw, ProductAttributes | None) for given product_id.
    """
    product = (
        db.query(models.ProductRaw)
        .filter(models.ProductRaw.id == product_id)
        .first()
    )
    if not product:
        return None

    attrs = (
        db.query(models.ProductAttributes)
        .filter(models.ProductAttributes.product_id == product_id)
        .first()
    )

    return product, attrs

def list_products_with_attributes(db: Session, limit: int = 20,offset: int = 0,) -> List[tuple[models.ProductRaw, Optional[models.ProductAttributes]]]:
    """
    Returns a list of (ProductRaw, ProductAttributes | None)
    with pagination.
    """
    products = (
        db.query(models.ProductRaw)
        .order_by(models.ProductRaw.created_at)
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Fetch attributes for all product_ids in one go
    product_ids = [p.id for p in products]
    attrs_by_pid = {}
    if product_ids:
        attrs = (
            db.query(models.ProductAttributes)
            .filter(models.ProductAttributes.product_id.in_(product_ids))
            .all()
        )
        attrs_by_pid = {a.product_id: a for a in attrs}

    result: List[tuple[models.ProductRaw, Optional[models.ProductAttributes]]] = []
    for p in products:
        result.append((p, attrs_by_pid.get(p.id)))

    return result

def search_products_with_attributes(
    db: Session,
    q: Optional[str] = None,
    category: Optional[str] = None,
    primary_use: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Tuple[models.ProductRaw, Optional[models.ProductAttributes]]]:
    """
    Very simple V0 search:
    - q: case-insensitive match in title or tags
    - category: matches attributes.category
    - primary_use: must be contained in attributes.primary_use (list)
    """
    # For now, we just reuse the list function and filter in Python.
    # This is fine for small catalogs and keeps logic simple.
    base_rows = list_products_with_attributes(db, limit=1000, offset=0)

    q_lower = q.lower() if q else None
    category_lower = category.lower() if category else None
    primary_use_lower = primary_use.lower() if primary_use else None

    filtered: List[Tuple[models.ProductRaw, Optional[models.ProductAttributes]]] = []

    for product, attrs in base_rows:
        raw = product.raw_json or {}
        title = (raw.get("title") or "").lower()
        tags = (raw.get("tags") or "").lower()

        # Text filter on title + tags
        if q_lower:
            if q_lower not in title and q_lower not in tags:
                continue

        # Category filter
        if category_lower:
            if not attrs or not attrs.category:
                continue
            if attrs.category.lower() != category_lower:
                continue

        # primary_use filter
        if primary_use_lower:
            if not attrs or not attrs.primary_use:
                continue
            lower_uses = [u.lower() for u in attrs.primary_use]
            if primary_use_lower not in lower_uses:
                continue

        filtered.append((product, attrs))

    # Paginate in Python for now
    sliced = filtered[offset : offset + limit]
    return sliced

## Not using yet put still wanna keep it for future use - Mughees

def build_product_sales_summary(product: models.ProductRaw, attrs: Optional[models.ProductAttributes],) -> dict:
    """
    V0 heuristic summary builder.
    Later, we can replace this with an LLM call that uses the same inputs.
    """
    raw = product.raw_json or {}

    title: str = raw.get("title", "Untitled product")
    tags_raw: str = raw.get("tags") or ""
    tags: List[str] = [t.strip() for t in tags_raw.split(",") if t.strip()]

    category = getattr(attrs, "category", None) if attrs else None
    primary_use = getattr(attrs, "primary_use", None) if attrs else None

    # Build a simple headline
    headline_parts: List[str] = []

    if category:
        headline_parts.append(category.capitalize())
    else:
        headline_parts.append("Versatile piece")

    if primary_use:
        # e.g. "for winter and campus wear"
        uses_text = " and ".join(primary_use) if len(primary_use) <= 2 else ", ".join(primary_use)
        headline_parts.append(f"for {uses_text} wear")
    else:
        headline_parts.append("for everyday use")

    headline = " ".join(headline_parts).strip()
    if not headline.endswith("."):
        headline += "."

    bullets: List[str] = []

    # Bullet 1 – Basic pitch
    bullets.append(f"Ideal for: {', '.join(primary_use) if primary_use else 'everyday wear'}.")

    # Bullet 2 – Category
    if category:
        bullets.append(f"Category: {category}.")
    else:
        bullets.append("Category: not classified yet (CLOZR will learn this from more data).")

    # Bullet 3 – Price hint (use first variant if present)
    variants = raw.get("variants") or []
    if variants:
        v0 = variants[0]
        price = v0.get("price")
        v_title = v0.get("title")
        if price and v_title:
            bullets.append(f"Example variant: {v_title} at ${price}.")
        elif price:
            bullets.append(f"Example price point around ${price}.")
    else:
        bullets.append("Pricing details available on the product page.")

    # Bullet 4 – Tags
    if tags:
        bullets.append("Key tags: " + ", ".join(tags) + ".")

    

    return {
        "product_id": product.id,
        "title": title,
        "headline": headline,
        "bullets": bullets,
        "tags": tags,
    }

def build_product_customer_overview_payload(product, overview: str, questions: list[str]) -> dict:
    """
    Minimal customer-facing payload for the CLOZR Overview box:
    - title
    - short AI-generated paragraph
    """
    raw = product.raw_json or {}
    return {
        "product_id": str(product.id),
        "title": raw.get("title", "Untitled product"),
        "overview": overview,
        "suggested_questions": questions,
    }
