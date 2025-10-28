from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# Association table for recipe ingredients
recipe_ingredients = Table(
    'recipe_ingredients',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id')),
    Column('quantity', Float),
    Column('unit', String)
)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)

    # Recipe details
    servings = Column(Integer, default=4)
    prep_time_minutes = Column(Integer)
    cook_time_minutes = Column(Integer)
    total_time_minutes = Column(Integer)
    difficulty = Column(String)  # "easy", "medium", "hard"

    # Content
    instructions = Column(Text)

    # Categorization
    cuisine = Column(String)
    meal_type = Column(String)  # "breakfast", "lunch", "dinner", "snack", "dessert"
    dietary_tags = Column(JSON)  # ["vegan", "gluten-free", etc.]

    # Metadata
    source_url = Column(String)
    image_url = Column(String)
    author = Column(String)

    # User tracking
    household_id = Column(Integer, ForeignKey("households.id"))
    is_favorite = Column(Boolean, default=False)
    times_made = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ingredients = relationship("Ingredient", secondary=recipe_ingredients, back_populates="recipes")
    meal_plans = relationship("MealPlan", back_populates="recipe")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipes = relationship("Recipe", secondary=recipe_ingredients, back_populates="ingredients")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    # Planning
    planned_date = Column(DateTime(timezone=True), nullable=False, index=True)
    meal_type = Column(String)  # "breakfast", "lunch", "dinner", "snack"
    servings = Column(Integer, default=4)

    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))

    # Notes
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("User", back_populates="meal_plans")
    recipe = relationship("Recipe", back_populates="meal_plans")


class AIMealSuggestion(Base):
    """Store AI-generated meal suggestions for analytics."""
    __tablename__ = "ai_meal_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # AI response
    suggestions = Column(JSON)  # List of suggested recipes
    inventory_snapshot = Column(JSON)  # What was in inventory when suggested
    ai_provider = Column(String)  # "openai", "anthropic"
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)

    # User feedback
    was_accepted = Column(Boolean)
    accepted_recipe_id = Column(Integer, ForeignKey("recipes.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
