from sqlalchemy.orm import Session
from app import models
from app.services.openai_overview import generate_short_overview, MODEL
from app.services.openai_overview import generate_suggested_questions



def get_or_generate_ai_overview(
    db: Session,
    product: models.ProductRaw,
    attrs: models.ProductAttributes | None,
) -> tuple[str, list[str]]:
    existing = db.get(models.ProductAIOverview, product.id)

    # If cached and complete, return both
    if existing and existing.overview and existing.suggested_questions:
        return existing.overview, (existing.suggested_questions or [])

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

    # Generate missing pieces
    overview = existing.overview if (existing and existing.overview) else generate_short_overview(product.raw_json or {}, attrs_dict)
    questions = generate_suggested_questions(product.raw_json or {}, attrs_dict)

    row = models.ProductAIOverview(
        product_id=product.id,
        overview=overview,
        suggested_questions=questions,
        model=MODEL,
    )
    db.merge(row)
    db.commit()

    return overview, questions
