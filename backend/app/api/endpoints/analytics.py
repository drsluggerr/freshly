from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.inventory import InventoryItem, ItemCategory

router = APIRouter()


@router.get("/waste-stats")
def get_waste_statistics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get waste statistics for the household."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total wasted items
    wasted_items = db.query(InventoryItem).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == True,
        InventoryItem.wasted_date >= start_date
    ).all()

    total_wasted = len(wasted_items)
    total_value = sum(item.price or 0 for item in wasted_items)

    # Waste by category
    waste_by_category = db.query(
        InventoryItem.category,
        func.count(InventoryItem.id).label("count"),
        func.sum(InventoryItem.price).label("total_value")
    ).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == True,
        InventoryItem.wasted_date >= start_date
    ).group_by(InventoryItem.category).all()

    # Most wasted items
    most_wasted = db.query(
        InventoryItem.name,
        func.count(InventoryItem.id).label("count")
    ).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == True,
        InventoryItem.wasted_date >= start_date
    ).group_by(InventoryItem.name).order_by(func.count(InventoryItem.id).desc()).limit(10).all()

    # Waste reasons
    waste_reasons = db.query(
        InventoryItem.waste_reason,
        func.count(InventoryItem.id).label("count")
    ).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == True,
        InventoryItem.wasted_date >= start_date,
        InventoryItem.waste_reason != None
    ).group_by(InventoryItem.waste_reason).all()

    return {
        "total_wasted_items": total_wasted,
        "total_value_wasted": round(total_value, 2),
        "waste_by_category": [
            {
                "category": cat,
                "count": count,
                "total_value": round(float(total_value or 0), 2)
            }
            for cat, count, total_value in waste_by_category
        ],
        "most_wasted_items": [
            {"name": name, "count": count}
            for name, count in most_wasted
        ],
        "waste_reasons": [
            {"reason": reason, "count": count}
            for reason, count in waste_reasons
        ]
    }


@router.get("/spending")
def get_spending_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get spending statistics."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total spending
    total_spent = db.query(func.sum(InventoryItem.price)).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.purchase_date >= start_date
    ).scalar() or 0

    # Spending by category
    spending_by_category = db.query(
        InventoryItem.category,
        func.sum(InventoryItem.price).label("total"),
        func.count(InventoryItem.id).label("count")
    ).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.purchase_date >= start_date
    ).group_by(InventoryItem.category).all()

    # Spending over time (daily)
    spending_timeline = db.query(
        func.date(InventoryItem.purchase_date).label("date"),
        func.sum(InventoryItem.price).label("total")
    ).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.purchase_date >= start_date
    ).group_by(func.date(InventoryItem.purchase_date)).order_by(func.date(InventoryItem.purchase_date)).all()

    return {
        "total_spent": round(float(total_spent), 2),
        "spending_by_category": [
            {
                "category": cat,
                "total": round(float(total or 0), 2),
                "count": count
            }
            for cat, total, count in spending_by_category
        ],
        "spending_timeline": [
            {
                "date": date.isoformat(),
                "total": round(float(total or 0), 2)
            }
            for date, total in spending_timeline
        ]
    }


@router.get("/inventory-summary")
def get_inventory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current inventory summary."""
    # Total items
    total_items = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == False
    ).scalar()

    # Items by category
    items_by_category = db.query(
        InventoryItem.category,
        func.count(InventoryItem.id).label("count")
    ).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == False
    ).group_by(InventoryItem.category).all()

    # Expiring soon (7 days)
    expiring_soon = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == False,
        InventoryItem.expiration_date <= datetime.utcnow() + timedelta(days=7),
        InventoryItem.expiration_date >= datetime.utcnow()
    ).scalar()

    # Expired
    expired = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == False,
        InventoryItem.expiration_date < datetime.utcnow()
    ).scalar()

    return {
        "total_items": total_items,
        "items_by_category": [
            {"category": cat, "count": count}
            for cat, count in items_by_category
        ],
        "expiring_soon": expiring_soon,
        "expired": expired
    }
