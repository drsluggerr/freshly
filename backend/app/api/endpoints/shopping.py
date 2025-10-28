from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.shopping import ShoppingList, ShoppingListItem, ShoppingListStatus

router = APIRouter()


@router.get("/lists", response_model=List[dict])
def get_shopping_lists(
    status: ShoppingListStatus = ShoppingListStatus.ACTIVE,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get shopping lists."""
    lists = db.query(ShoppingList).filter(
        ShoppingList.household_id == current_user.household_id,
        ShoppingList.status == status
    ).order_by(ShoppingList.created_at.desc()).all()

    return lists


@router.post("/lists", status_code=201)
def create_shopping_list(
    name: str,
    store: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new shopping list."""
    shopping_list = ShoppingList(
        household_id=current_user.household_id,
        created_by_id=current_user.id,
        name=name,
        store=store
    )

    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)

    return shopping_list


@router.post("/lists/{list_id}/items", status_code=201)
def add_item_to_list(
    list_id: int,
    name: str,
    quantity: float = 1.0,
    unit: str = None,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an item to a shopping list."""
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == list_id,
        ShoppingList.household_id == current_user.household_id
    ).first()

    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    item = ShoppingListItem(
        shopping_list_id=list_id,
        name=name,
        quantity=quantity,
        unit=unit,
        category=category
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.patch("/lists/{list_id}/items/{item_id}/purchase")
def mark_item_purchased(
    list_id: int,
    item_id: int,
    purchased: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark an item as purchased."""
    item = db.query(ShoppingListItem).join(ShoppingList).filter(
        ShoppingListItem.id == item_id,
        ShoppingListItem.shopping_list_id == list_id,
        ShoppingList.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_purchased = purchased
    if purchased:
        item.purchased_at = datetime.utcnow()
    else:
        item.purchased_at = None

    db.commit()
    db.refresh(item)

    return item


@router.delete("/lists/{list_id}/items/{item_id}", status_code=204)
def delete_shopping_item(
    list_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an item from shopping list."""
    item = db.query(ShoppingListItem).join(ShoppingList).filter(
        ShoppingListItem.id == item_id,
        ShoppingListItem.shopping_list_id == list_id,
        ShoppingList.household_id == current_user.household_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
