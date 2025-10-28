from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    household_id = Column(Integer, ForeignKey("households.id"))

    # Receipt metadata
    merchant_name = Column(String)
    merchant_address = Column(String)
    purchase_date = Column(DateTime(timezone=True))
    total_amount = Column(Float)
    tax_amount = Column(Float)
    currency = Column(String, default="USD")

    # Receipt details
    receipt_number = Column(String, index=True)
    payment_method = Column(String)

    # File storage
    image_url = Column(String)
    image_path = Column(String)

    # OCR processing
    ocr_provider = Column(String)  # "veryfi", "mindee", "taggun"
    ocr_raw_response = Column(JSON)  # Store full API response
    processing_time_ms = Column(Integer)
    processing_status = Column(String, default="pending")  # "pending", "processing", "completed", "failed"
    processing_error = Column(Text)

    # Duplicate detection
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, ForeignKey("receipts.id"))

    # Tracking
    is_processed = Column(Boolean, default=False)
    items_added = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    uploaded_by = relationship("User", back_populates="receipts")
    items = relationship("InventoryItem", back_populates="receipt")
    line_items = relationship("ReceiptLineItem", back_populates="receipt")


class ReceiptLineItem(Base):
    """Individual line items extracted from receipts."""
    __tablename__ = "receipt_line_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)

    # Extracted data
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float)
    total_price = Column(Float)

    # Matching
    matched_product_id = Column(Integer, ForeignKey("products.id"))
    confidence_score = Column(Float)  # 0-1 confidence in product match

    # User corrections
    user_corrected_name = Column(String)
    category = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    receipt = relationship("Receipt", back_populates="line_items")
