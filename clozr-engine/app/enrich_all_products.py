# app/enrich_all_products.py

from app.db import SessionLocal
from app import models
from app.attributes import extract_attributes_from_raw


def enrich_all_products() -> None:
    db = SessionLocal()
    try:
        products = db.query(models.ProductRaw).all()
        print(f"Found {len(products)} products in products_raw")

        for p in products:
            attrs_dict = extract_attributes_from_raw(p.raw_json or {})

            # either update existing row or insert a new one
            existing = (
                db.query(models.ProductAttributes)
                .filter(models.ProductAttributes.product_id == p.id)
                .one_or_none()
            )

            if existing:
                for k, v in attrs_dict.items():
                    setattr(existing, k, v)
                print(f"Updated attributes for product {p.id}")
            else:
                new_attrs = models.ProductAttributes(
                    product_id=p.id,
                    **attrs_dict,
                )
                db.add(new_attrs)
                print(f"Created attributes for product {p.id}")

        db.commit()
        print("✅ Done enriching all products.")

    finally:
        db.close()


if __name__ == "__main__":
    enrich_all_products()
