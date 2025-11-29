import json
import os

from app.db import SessionLocal
from app.services.product_services import ingest_product


SAMPLE_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # clozr-engine/
    "sample_products.json",
)


def import_sample_products():
    db = SessionLocal()
    try:
        with open(SAMPLE_FILE_PATH, "r") as f:
            data = json.load(f)

        products = data.get("products", [])
        merchant_domain = "clozr-dev-store.myshopify.com"  # or any sample domain

        print(f"Loaded {len(products)} products from sample_products.json")

        for p in products:
            shop_product_id = str(p["id"])
            raw_json = p

            product = ingest_product(
                db=db,
                merchant_domain=merchant_domain,
                shop_product_id=shop_product_id,
                raw_json=raw_json,
            )
            print(f"Ingested sample product {shop_product_id} -> {product.id}")

    finally:
        db.close()


if __name__ == "__main__":
    import_sample_products()