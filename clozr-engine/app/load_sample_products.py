
import json
import uuid
from sqlalchemy import text

from app.db import SessionLocal
from app import models

DEV_STORE_DOMAIN = "clozr-dev-store.myshopify.com"

JSON_PATH = "../clozr-app/server/data/products_clozr_dev_store_myshopify_com.json"


def load_sample_products(reset: bool = True) -> None:
    db = SessionLocal()

    try:
        if reset:
            print("Truncating products_raw and product_attributes...")
            db.execute(text("TRUNCATE TABLE product_attributes, products_raw RESTART IDENTITY CASCADE;"))
            db.commit()

        # Ensure merchant exists
        merchant = (
            db.query(models.Merchant)
            .filter(models.Merchant.shop_domain == DEV_STORE_DOMAIN)
            .first()
        )

        if not merchant:
            merchant = models.Merchant(
                id=uuid.uuid4(),
                name="CLOZR Dev Store",
                domain=DEV_STORE_DOMAIN,
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)

        print(f"Using merchant: {merchant.id}")

        # Load JSON
        with open(JSON_PATH, "r") as f:
            data = json.load(f)

        products = data.get("products", data)
        print(f"Found {len(products)} products in the JSON file.")

        # Insert into DB
        for p in products:
            shop_product_id = str(p.get("id"))

            product = models.ProductRaw(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                shop_product_id=shop_product_id,
                raw_json=p,
            )

            db.add(product)
            print(f"Imported product {shop_product_id}: {p.get('title')}")

        db.commit()
        print("✔ Finished loading products.")

    finally:
        db.close()


if __name__ == "__main__":
    load_sample_products(reset=True)
