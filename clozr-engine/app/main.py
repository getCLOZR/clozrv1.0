# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app import models

from app.db import get_db
from app.schemas import ProductIngestPayload, ProductIntelligenceResponse, ProductDetailResponse, ProductListItem, ProductOverviewResponse, ProductSummaryResponse, ProductChatRequest, ProductChatResponse
from app.services import product_services
from app.services.product_services import (get_product_with_attributes, list_products_with_attributes, search_products_with_attributes, build_product_sales_summary)
from app.services.ai_overview_services import get_or_generate_ai_overview
from app.services.product_services import build_product_customer_overview_payload
from app.services.openai_overview import generate_chat_response


app = FastAPI(title="CLOZR Product Intelligence Engine")

# Add CORS middleware to allow requests from Shopify stores
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - for production, specify: ["https://*.myshopify.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/products", response_model=List[ProductListItem])
def list_products(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    rows = list_products_with_attributes(db, limit=limit, offset=offset)

    items: List[ProductListItem] = []
    for product, attrs in rows:
        raw = product.raw_json or {}
        title = raw.get("title", "Untitled product")

        items.append(
            ProductListItem(
                id=product.id,
                shop_product_id=product.shop_product_id,
                title=title,
                category=(attrs.category if attrs else None),
                primary_use=(attrs.primary_use if attrs else None),
            )
        )

    return items

@app.get("/products/search", response_model=List[ProductListItem])
def search_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    primary_use: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    rows = search_products_with_attributes(
        db,
        q=q,
        category=category,
        primary_use=primary_use,
        limit=limit,
        offset=offset,
    )

    items: List[ProductListItem] = []
    for product, attrs in rows:
        raw = product.raw_json or {}
        title = raw.get("title", "Untitled product")

        items.append(
            ProductListItem(
                id=product.id,
                shop_product_id=product.shop_product_id,
                title=title,
                category=(attrs.category if attrs else None),
                primary_use=(attrs.primary_use if attrs else None),
            )
        )

    return items


@app.get("/products/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    result = get_product_with_attributes(db, product_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product, attrs = result
    return {
        "product": product,
        "attributes": attrs,
    }

@app.get("/products/{product_id}/summary", response_model=ProductSummaryResponse)
def get_product_summary(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    result = get_product_with_attributes(db, product_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product, attrs = result
    summary_dict = build_product_sales_summary(product, attrs)

    return summary_dict


@app.get("/shopify/products/{shop_product_id}/summary", response_model=ProductOverviewResponse)
def get_product_summary_by_shop_id(
    shop_product_id: str,
    db: Session = Depends(get_db),
):
    # Fetch product + attributes by Shopify product id
    result = (
        db.query(models.ProductRaw, models.ProductAttributes)
        .outerjoin(
            models.ProductAttributes,
            models.ProductAttributes.product_id == models.ProductRaw.id,
        )
        .filter(models.ProductRaw.shop_product_id == shop_product_id)
        .first()
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Product not found for this Shopify id")

    product, attrs = result

    overview = get_or_generate_ai_overview(db, product, attrs)
    return build_product_customer_overview_payload(product, overview)


@app.post("/shopify/products/chat", response_model=ProductChatResponse)
def chat_about_product(
    payload: ProductChatRequest,
    db: Session = Depends(get_db),
):
    """
    Chat endpoint for product questions.
    Accepts product context (ID, shop, initial overview) and user question.
    Returns LLM-generated response grounded in product context.
    """
    try:
        print(f"Chat request received: product_id={payload.product_id}, shop={payload.shop_domain}, question={payload.question[:50]}...")
        
        # Fetch merchant first
        merchant = db.query(models.Merchant).filter(
            models.Merchant.shop_domain == payload.shop_domain
        ).first()

        raw_json = {}
        attrs_dict = {}
        
        if merchant:
            # Fetch product + attributes for additional context
            result = (
                db.query(models.ProductRaw, models.ProductAttributes)
                .outerjoin(
                    models.ProductAttributes,
                    models.ProductAttributes.product_id == models.ProductRaw.id,
                )
                .filter(models.ProductRaw.shop_product_id == payload.product_id)
                .filter(models.ProductRaw.merchant_id == merchant.id)
                .first()
            )

            if result:
                product, attrs = result
                raw_json = product.raw_json or {}
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
                print(f"Product found: {raw_json.get('title', 'Unknown')}")
            else:
                print(f"Product not found: product_id={payload.product_id}, merchant_id={merchant.id}")
        else:
            print(f"Merchant not found: shop_domain={payload.shop_domain}")

        # Generate LLM response with context
        response = generate_chat_response(
            product_id=payload.product_id,
            shop_domain=payload.shop_domain,
            initial_overview=payload.initial_overview,
            question=payload.question,
            raw_json=raw_json,
            attrs=attrs_dict,
        )

        print(f"Chat response generated: {response[:50]}...")
        return ProductChatResponse(response=response)
    except Exception as e:
        import traceback
        print(f"Error in chat_about_product: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


