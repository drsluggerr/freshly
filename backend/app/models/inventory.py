from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class UnitType(str, enum.Enum):
    # Weight
    OZ = "oz"
    LB = "lb"
    G = "g"
    KG = "kg"
    # Volume
    FL_OZ = "fl_oz"
    CUP = "cup"
    ML = "ml"
    L = "L"
    # Count
    ITEM = "item"
    SERVING = "serving"


class ItemCategory(str, enum.Enum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    MEAT = "meat"
    SEAFOOD = "seafood"
    BAKERY = "bakery"
    FROZEN = "frozen"
    CANNED = "canned"
    DRY_GOODS = "dry_goods"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    CONDIMENTS = "condiments"
    SPICES = "spices"
    OTHER = "other"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(SQLEnum(ItemCategory), nullable=False)
    barcode = Column(String, index=True)

    # Quantity
    quantity = Column(Float, nullable=False)
    unit = Column(SQLEnum(UnitType), nullable=False)
    original_quantity = Column(Float)  # For tracking partial usage

    # Dates
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())
    expiration_date = Column(DateTime(timezone=True))
    opened_date = Column(DateTime(timezone=True))

    # Location
    location_id = Column(Integer, ForeignKey("storage_locations.id"))

    # Pricing
    price = Column(Float)
    currency = Column(String, default="USD")

    # Status
    is_opened = Column(Boolean, default=False)
    is_wasted = Column(Boolean, default=False)
    waste_reason = Column(String)
    wasted_date = Column(DateTime(timezone=True))

    # Metadata
    notes = Column(Text)
    brand = Column(String)
    store = Column(String)
    image_url = Column(String)

    # Tracking
    added_by = Column(Integer, ForeignKey("users.id"))
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    household_id = Column(Integer, ForeignKey("households.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    location = relationship("StorageLocation", back_populates="inventory_items")
    added_by_user = relationship("User", back_populates="inventory_items")
    receipt = relationship("Receipt", back_populates="items")


class Product(Base):
    """Master product database for autocomplete and smart matching."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(SQLEnum(ItemCategory), nullable=False)
    barcode = Column(String, unique=True, index=True)
    brand = Column(String)
    default_unit = Column(SQLEnum(UnitType))
    average_shelf_life_days = Column(Integer)  # For expiration estimates
    image_url = Column(String)

    # Price tracking
    average_price = Column(Float)
    last_price = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserAction(Base):
    """For undo/redo functionality."""
    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # e.g., "add_item", "delete_item", "update_quantity"
    entity_type = Column(String, nullable=False)  # e.g., "inventory_item", "receipt"
    entity_id = Column(Integer, nullable=False)
    old_state = Column(Text)  # JSON snapshot of old state
    new_state = Column(Text)  # JSON snapshot of new state
    is_undone = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="actions")
