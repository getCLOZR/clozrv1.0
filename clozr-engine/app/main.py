# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.schemas import ProductIngestPayload, ProductIntelligenceResponse
from app.services import product_services

app = FastAPI(title="CLOZR Product Intelligence Engine")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/products/ingest")
def ingest_product(payload: ProductIngestPayload, db: Session = Depends(get_db)):
    product = product_services.ingest_product(
        db=db,
        merchant_domain=payload.merchant_domain,
        shop_product_id=payload.shop_product_id,
        raw_json=payload.raw_json,
    )
    return {"status": "stored", "product_id": str(product.id)}


@app.get("/products/{product_id}/intelligence", response_model=ProductIntelligenceResponse)
def get_product_intelligence(product_id: UUID):
    # TODO: replace with real DB-backed intelligence
    return ProductIntelligenceResponse(
        product_id=product_id,
        summary="A warm, casual hoodie ideal for winter campus wear.",
        reasons_to_buy=[
            "Fleece-lined for extra warmth",
            "Comfortable regular fit",
            "Budget-friendly price point",
        ],
        fit_guidance="Runs slightly large based on customer feedback.",
        attributes={
            "category": "hoodie",
            "warmth_level": "high",
            "primary_use": ["winter", "campus", "casual"],
        },
    )
