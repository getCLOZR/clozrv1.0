# # app/shopify_import.py
# import os
# from app.db import SessionLocal
# from app.shopify_client import get_products
# from app.services.product_services import ingest_product


# def import_products_from_shopify(limit: int = 50):
#     db = SessionLocal()
#     try:
#         products = get_products(limit=limit)
#         merchant_domain = os.getenv("SHOPIFY_STORE_DOMAIN")

#         print(f"Fetched {len(products)} products from Shopify")

#         for p in products:
#             shop_product_id = str(p["id"])
#             raw_json = p

#             product = ingest_product(
#                 db=db,
#                 merchant_domain=merchant_domain,
#                 shop_product_id=shop_product_id,
#                 raw_json=raw_json,
#             )
#             print(f"Ingested product {shop_product_id} -> {product.id}")
#     finally:
#         db.close()


# if __name__ == "__main__":
#     import_products_from_shopify(limit=50)
