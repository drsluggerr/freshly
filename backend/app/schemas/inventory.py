from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.inventory import UnitType, ItemCategory


class InventoryItemBase(BaseModel):
    name: str
    category: ItemCategory
    quantity: float
    unit: UnitType
    barcode: Optional[str] = None
    expiration_date: Optional[datetime] = None
    location_id: Optional[int] = None
    price: Optional[float] = None
    notes: Optional[str] = None
    brand: Optional[str] = None
    store: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ItemCategory] = None
    quantity: Optional[float] = None
    unit: Optional[UnitType] = None
    expiration_date: Optional[datetime] = None
    location_id: Optional[int] = None
    is_opened: Optional[bool] = None
    notes: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    original_quantity: Optional[float] = None
    purchase_date: datetime
    is_opened: bool
    is_wasted: bool
    added_by: Optional[int] = None
    household_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryItemWaste(BaseModel):
    item_id: int
    waste_reason: str


class ProductResponse(BaseModel):
    id: int
    name: str
    category: ItemCategory
    barcode: Optional[str] = None
    brand: Optional[str] = None
    default_unit: Optional[UnitType] = None
    average_shelf_life_days: Optional[int] = None

    class Config:
        from_attributes = True


class BulkInventoryAdd(BaseModel):
    items: list[InventoryItemCreate]


class PartialUsage(BaseModel):
    item_id: int
    quantity_used: float
