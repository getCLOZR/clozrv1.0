from sqlalchemy.orm import Session
from app import models
from app.services.openai_overview import generate_short_overview, MODEL


def get_or_generate_ai_overview(
    db: Session,
    product: models.ProductRaw,
    attrs: models.ProductAttributes | None,
) -> str:
    existing = db.get(models.ProductAIOverview, product.id)
    if existing and existing.overview:
        return existing.overview

    attrs_dict = {}
    if attrs:
        attrs_dict = {
            "category": attrs.category,
            "style": attrs.style,
            "warmth_level": attrs.warmth_level,
            "fit": attrs.fit,
            "material_main": attrs.material_main,
            "price_band": attrs.price_band,
            "primary_use": attrs.primary_use,
            "extra_metadata": attrs.extra_metadata,
        }

    overview = generate_short_overview(product.raw_json or {}, attrs_dict)

    row = models.ProductAIOverview(
        product_id=product.id,
        overview=overview,
        model=MODEL,
    )
    db.merge(row)
    db.commit()

    return overview
