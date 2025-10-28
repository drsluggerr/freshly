from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.ADMIN)
    household_id = Column(Integer, ForeignKey("households.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    household = relationship("Household", back_populates="members")
    inventory_items = relationship("InventoryItem", back_populates="added_by_user")
    receipts = relationship("Receipt", back_populates="uploaded_by")
    shopping_lists = relationship("ShoppingList", back_populates="created_by")
    meal_plans = relationship("MealPlan", back_populates="created_by")
    actions = relationship("UserAction", back_populates="user")


class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    members = relationship("User", back_populates="household")
    storage_locations = relationship("StorageLocation", back_populates="household")


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Fridge", "Freezer", "Pantry"
    zone = Column(String)  # e.g., "Top Shelf", "Drawer 1"
    icon = Column(String)
    color = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    household = relationship("Household", back_populates="storage_locations")
    inventory_items = relationship("InventoryItem", back_populates="location")
