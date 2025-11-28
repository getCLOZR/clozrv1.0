# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

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
