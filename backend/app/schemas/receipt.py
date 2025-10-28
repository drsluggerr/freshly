from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReceiptLineItemBase(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    user_corrected_name: Optional[str] = None
    category: Optional[str] = None


class ReceiptLineItemResponse(ReceiptLineItemBase):
    id: int
    receipt_id: int
    confidence_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReceiptBase(BaseModel):
    merchant_name: Optional[str] = None
    purchase_date: Optional[datetime] = None
    total_amount: Optional[float] = None


class ReceiptCreate(BaseModel):
    # Will be populated from OCR
    pass


class ReceiptResponse(ReceiptBase):
    id: int
    uploaded_by_id: int
    merchant_address: Optional[str] = None
    receipt_number: Optional[str] = None
    processing_status: str
    is_duplicate: bool
    is_processed: bool
    items_added: bool
    created_at: datetime
    line_items: List[ReceiptLineItemResponse] = []

    class Config:
        from_attributes = True


class ReceiptProcessingResponse(BaseModel):
    receipt_id: int
    status: str
    processing_time_ms: int
    line_items_count: int
    total_amount: Optional[float] = None
    merchant_name: Optional[str] = None
    is_duplicate: bool


class ReceiptConfirmation(BaseModel):
    receipt_id: int
    confirmed_items: List[int]  # List of line item IDs to add to inventory
    corrections: Optional[dict] = None  # Any user corrections to line items
