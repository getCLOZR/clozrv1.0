# app/services/product_services.py
from sqlalchemy.orm import Session
from app import models
from app.attributes import extract_attributes_from_raw

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