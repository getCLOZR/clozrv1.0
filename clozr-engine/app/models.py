# app/models.py
from sqlalchemy import Column, String, JSON, TIMESTAMP, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import uuid

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_domain = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))


class ProductRaw(Base):
    __tablename__ = "products_raw"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    shop_product_id = Column(String, nullable=False)
    raw_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class ProductAttributes(Base):
    __tablename__ = "product_attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products_raw.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    category = Column(String, nullable=True)        # e.g. "hoodie"
    style = Column(String, nullable=True)           # e.g. "casual", "streetwear"
    warmth_level = Column(String, nullable=True)    # e.g. "low/medium/high"
    fit = Column(String, nullable=True)             # e.g. "regular", "oversized"
    material_main = Column(String, nullable=True)   # e.g. "cotton fleece"
    price_band = Column(String, nullable=True)      # e.g. "$", "$$", "$$$"

    # JSON for anything extra or future fields
    primary_use = Column(JSON, nullable=True)       # e.g. ["winter", "campus", "casual"]
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))


