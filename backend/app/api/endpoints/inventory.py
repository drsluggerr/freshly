from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.inventory import InventoryItem, Product, UserAction, ItemCategory
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    BulkInventoryAdd,
    PartialUsage,
    InventoryItemWaste,
    ProductResponse
)
import json

router = APIRouter()


@router.get("/", response_model=List[InventoryItemResponse])
def get_inventory(
    skip: int = 0,
    limit: int = 100,
    location_id: Optional[int] = None,
    category: Optional[ItemCategory] = None,
    expiring_soon: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory items with optional filters."""
    query = db.query(InventoryItem).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == False
    )

    if location_id:
        query = query.filter(InventoryItem.location_id == location_id)

    if category:
        query = query.filter(InventoryItem.category == category)

    if search:
        query = query.filter(
            or_(
                InventoryItem.name.ilike(f"%{search}%"),
                InventoryItem.brand.ilike(f"%{search}%")
            )
        )

    if expiring_soon:
        # Items expiring within 7 days
        expiry_threshold = datetime.utcnow() + timedelta(days=7)
        query = query.filter(
            InventoryItem.expiration_date <= expiry_threshold,
            InventoryItem.expiration_date >= datetime.utcnow()
        )

    items = query.order_by(InventoryItem.expiration_date.asc()).offset(skip).limit(limit).all()
    return items


@router.post("/", response_model=InventoryItemResponse, status_code=201)
def create_inventory_item(
    item_in: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new item to inventory."""
    item = InventoryItem(
        **item_in.model_dump(),
        household_id=current_user.household_id,
        added_by=current_user.id,
        original_quantity=item_in.quantity
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    # Record action for undo
    action = UserAction(
        user_id=current_user.id,
        action_type="add_item",
        entity_type="inventory_item",
        entity_id=item.id,
        old_state=None,
        new_state=json.dumps(item_in.model_dump(), default=str)
    )
    db.add(action)
    db.commit()

    return item


@router.post("/bulk", response_model=List[InventoryItemResponse], status_code=201)
def bulk_add_inventory(
    bulk_in: BulkInventoryAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bulk add items to inventory (from receipt processing)."""
    created_items = []

    for item_in in bulk_in.items:
        item = InventoryItem(
            **item_in.model_dump(),
            household_id=current_user.household_id,
            added_by=current_user.id,
            original_quantity=item_in.quantity
        )
        db.add(item)
        created_items.append(item)

    db.commit()

    for item in created_items:
        db.refresh(item)

    # Record bulk action
    action = UserAction(
        user_id=current_user.id,
        action_type="bulk_add_items",
        entity_type="inventory_item",
        entity_id=created_items[0].id if created_items else 0,
        old_state=None,
        new_state=json.dumps([i.model_dump() for i in bulk_in.items], default=str)
    )
    db.add(action)
    db.commit()

    return created_items


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific inventory item."""
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.patch("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    item_id: int,
    item_in: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an inventory item."""
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Store old state
    old_state = {
        "name": item.name,
        "quantity": item.quantity,
        "expiration_date": item.expiration_date,
        "location_id": item.location_id
    }

    # Update fields
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    # Record action
    action = UserAction(
        user_id=current_user.id,
        action_type="update_item",
        entity_type="inventory_item",
        entity_id=item.id,
        old_state=json.dumps(old_state, default=str),
        new_state=json.dumps(update_data, default=str)
    )
    db.add(action)
    db.commit()

    return item


@router.post("/{item_id}/use", response_model=InventoryItemResponse)
def use_partial_quantity(
    item_id: int,
    usage: PartialUsage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Record partial usage of an item."""
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if usage.quantity_used > item.quantity:
        raise HTTPException(status_code=400, detail="Cannot use more than available quantity")

    old_quantity = item.quantity
    item.quantity -= usage.quantity_used

    if item.quantity == 0:
        db.delete(item)
    else:
        if not item.is_opened:
            item.is_opened = True
            item.opened_date = datetime.utcnow()

    db.commit()

    if item.quantity > 0:
        db.refresh(item)

    # Record action
    action = UserAction(
        user_id=current_user.id,
        action_type="use_partial",
        entity_type="inventory_item",
        entity_id=item.id,
        old_state=json.dumps({"quantity": old_quantity}, default=str),
        new_state=json.dumps({"quantity": item.quantity, "used": usage.quantity_used}, default=str)
    )
    db.add(action)
    db.commit()

    return item


@router.delete("/{item_id}", status_code=204)
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an inventory item."""
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Store for undo
    old_state = {
        "name": item.name,
        "quantity": item.quantity,
        "unit": item.unit,
        "category": item.category
    }

    db.delete(item)
    db.commit()

    # Record action
    action = UserAction(
        user_id=current_user.id,
        action_type="delete_item",
        entity_type="inventory_item",
        entity_id=item_id,
        old_state=json.dumps(old_state, default=str),
        new_state=None
    )
    db.add(action)
    db.commit()


@router.post("/{item_id}/waste", response_model=InventoryItemResponse)
def mark_as_wasted(
    item_id: int,
    waste_data: InventoryItemWaste,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark an item as wasted for tracking."""
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_wasted = True
    item.waste_reason = waste_data.waste_reason
    item.wasted_date = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return item


@router.get("/products/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search products for autocomplete."""
    products = db.query(Product).filter(
        Product.name.ilike(f"%{q}%")
    ).limit(limit).all()

    return products
