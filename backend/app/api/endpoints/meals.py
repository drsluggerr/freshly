from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.meal import Recipe, MealPlan, AIMealSuggestion
from app.models.inventory import InventoryItem
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/suggest")
async def get_meal_suggestions(
    dietary_preferences: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-powered meal suggestions based on current inventory."""
    # Get current inventory
    inventory_items = db.query(InventoryItem).filter(
        InventoryItem.household_id == current_user.household_id,
        InventoryItem.is_wasted == False
    ).all()

    if not inventory_items:
        raise HTTPException(status_code=400, detail="No inventory items found")

    # Format inventory for AI
    inventory_data = [
        {
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "expiration_date": item.expiration_date.isoformat() if item.expiration_date else None,
            "category": item.category
        }
        for item in inventory_items
    ]

    # Get AI suggestions
    result = await ai_service.suggest_meals(inventory_data, dietary_preferences)

    # Store suggestion for analytics
    suggestion_record = AIMealSuggestion(
        household_id=current_user.household_id,
        user_id=current_user.id,
        suggestions=result["suggestions"],
        inventory_snapshot=inventory_data,
        ai_provider="openai",
        prompt_tokens=result.get("prompt_tokens"),
        completion_tokens=result.get("completion_tokens")
    )
    db.add(suggestion_record)
    db.commit()

    return {
        "suggestions": result["suggestions"],
        "inventory_used": len(inventory_items)
    }


@router.get("/recipes", response_model=List[dict])
def get_recipes(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    meal_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recipes."""
    query = db.query(Recipe).filter(
        (Recipe.household_id == current_user.household_id) | (Recipe.household_id == None)
    )

    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))

    if meal_type:
        query = query.filter(Recipe.meal_type == meal_type)

    recipes = query.offset(skip).limit(limit).all()
    return recipes


@router.get("/plan", response_model=List[dict])
def get_meal_plan(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get meal plan for a date range."""
    if not start_date:
        start_date = datetime.utcnow()

    if not end_date:
        end_date = start_date + timedelta(days=7)

    meal_plans = db.query(MealPlan).filter(
        MealPlan.household_id == current_user.household_id,
        MealPlan.planned_date >= start_date,
        MealPlan.planned_date <= end_date
    ).order_by(MealPlan.planned_date).all()

    return meal_plans


@router.post("/plan", status_code=201)
def create_meal_plan(
    recipe_id: int,
    planned_date: datetime,
    meal_type: str,
    servings: int = 4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a meal to the meal plan."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    meal_plan = MealPlan(
        household_id=current_user.household_id,
        created_by_id=current_user.id,
        recipe_id=recipe_id,
        planned_date=planned_date,
        meal_type=meal_type,
        servings=servings
    )

    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)

    return meal_plan


@router.delete("/plan/{plan_id}", status_code=204)
def delete_meal_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a meal from the meal plan."""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == plan_id,
        MealPlan.household_id == current_user.household_id
    ).first()

    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    db.delete(meal_plan)
    db.commit()
