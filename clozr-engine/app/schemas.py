# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime



class ProductIngestPayload(BaseModel):
    merchant_domain: str
    shop_product_id: str
    raw_json: dict


class ProductIntelligenceResponse(BaseModel):
    product_id: UUID
    summary: str
    reasons_to_buy: List[str]
    fit_guidance: Optional[str] = None
    attributes: dict

class ProductRawSchema(BaseModel):
    id: UUID
    merchant_id: Optional[UUID]
    shop_product_id: Optional[str]
    raw_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductAttributesSchema(BaseModel):
    id: UUID
    product_id: UUID
    category: Optional[str]
    style: Optional[str]
    warmth_level: Optional[str]
    fit: Optional[str]
    material_main: Optional[str]
    price_band: Optional[str]
    primary_use: Optional[List[str]]
    extra_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductDetailResponse(BaseModel):
    product: ProductRawSchema
    attributes: Optional[ProductAttributesSchema]  # in case we have raw but not enriched yet


class ProductListItem(BaseModel):
    id: UUID
    shop_product_id: Optional[str]
    title: str
    category: Optional[str]
    primary_use: Optional[List[str]]

    class Config:
        orm_mode = True

class ProductSummaryResponse(BaseModel):
    product_id: UUID
    title: str
    headline: str
    bullets: List[str]
    tags: List[str]

    class Config:
        orm_mode = True