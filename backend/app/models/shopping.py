from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class ShoppingListStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String, nullable=False)
    store = Column(String)
    status = Column(SQLEnum(ShoppingListStatus), default=ShoppingListStatus.ACTIVE)

    # Auto-generation
    generated_from_meal_plan = Column(Boolean, default=False)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    created_by = relationship("User", back_populates="shopping_lists")
    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)

    # Item details
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String)
    category = Column(String)

    # Shopping details
    aisle = Column(String)
    estimated_price = Column(Float)
    actual_price = Column(Float)
    store = Column(String)

    # Status
    is_purchased = Column(Boolean, default=False)
    purchased_at = Column(DateTime(timezone=True))

    # Tracking
    is_staple = Column(Boolean, default=False)  # For recurring items
    notes = Column(Text)

    # Duplicate detection
    already_have_warning = Column(Boolean, default=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="items")


class StoreAisle(Base):
    """Store aisle layout for organizing shopping lists."""
    __tablename__ = "store_aisles"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    store_name = Column(String, nullable=False)
    aisle_number = Column(String, nullable=False)
    aisle_name = Column(String)
    categories = Column(Text)  # Comma-separated categories in this aisle

    created_at = Column(DateTime(timezone=True), server_default=func.now())
