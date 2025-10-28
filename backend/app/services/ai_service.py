import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings


class AIService:
    """Service for AI-powered features using OpenAI or Anthropic."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def suggest_meals(self, inventory_items: List[Dict[str, Any]], dietary_preferences: List[str] = None) -> Dict[str, Any]:
        """
        Generate meal suggestions based on current inventory.

        Args:
            inventory_items: List of items currently in inventory
            dietary_preferences: Optional list of dietary restrictions (vegan, gluten-free, etc.)

        Returns:
            Dict with suggested meals and reasoning
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        # Build inventory summary
        inventory_summary = self._build_inventory_summary(inventory_items)

        # Build dietary restrictions prompt
        dietary_text = ""
        if dietary_preferences:
            dietary_text = f"\n\nDietary restrictions: {', '.join(dietary_preferences)}"

        prompt = f"""You are a helpful cooking assistant. Based on the following inventory items, suggest 3-5 delicious meals that can be made using primarily these ingredients.

Inventory:
{inventory_summary}
{dietary_text}

For each meal suggestion, provide:
1. Meal name
2. Brief description
3. Main ingredients from inventory that will be used
4. Any additional ingredients needed (if minimal)
5. Estimated prep time
6. Difficulty level (easy/medium/hard)

Focus on:
- Using items that are expiring soon first
- Creating balanced, nutritious meals
- Minimizing additional grocery purchases
- Variety in meal types (breakfast, lunch, dinner, snacks)

Return your response as a JSON array of meal objects."""

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant that suggests meals based on available ingredients. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "suggestions": result.get("meals", []),
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "model": "gpt-4-turbo-preview"
        }

    async def estimate_expiration_date(self, product_name: str, category: str, purchase_date: str) -> int:
        """
        Estimate shelf life for a product in days.

        Returns:
            Number of days until expiration
        """
        # Simple heuristic-based estimation
        # In production, this could use AI or a database of known shelf lives

        category_defaults = {
            "produce": 7,
            "dairy": 14,
            "meat": 3,
            "seafood": 2,
            "bakery": 5,
            "frozen": 180,
            "canned": 365,
            "dry_goods": 180,
            "beverages": 90,
            "snacks": 60,
            "condiments": 120,
            "spices": 365,
        }

        return category_defaults.get(category.lower(), 30)

    async def categorize_product(self, product_name: str) -> str:
        """
        Automatically categorize a product based on its name.

        Returns:
            Category name
        """
        if not self.client:
            # Fallback to simple keyword matching
            return self._simple_categorization(product_name)

        prompt = f"""Categorize the following product into one of these categories:
- produce
- dairy
- meat
- seafood
- bakery
- frozen
- canned
- dry_goods
- beverages
- snacks
- condiments
- spices
- other

Product: {product_name}

Return only the category name, nothing else."""

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a product categorization assistant. Return only the category name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )

        return response.choices[0].message.content.strip().lower()

    def _build_inventory_summary(self, inventory_items: List[Dict[str, Any]]) -> str:
        """Build a human-readable inventory summary."""
        lines = []
        for item in inventory_items:
            expiration = ""
            if item.get("expiration_date"):
                expiration = f" (expires: {item['expiration_date']})"

            lines.append(f"- {item['name']}: {item['quantity']} {item['unit']}{expiration}")

        return "\n".join(lines)

    def _simple_categorization(self, product_name: str) -> str:
        """Simple keyword-based categorization fallback."""
        product_lower = product_name.lower()

        keywords = {
            "produce": ["apple", "banana", "orange", "lettuce", "tomato", "carrot", "potato", "onion"],
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream"],
            "meat": ["chicken", "beef", "pork", "turkey", "ham"],
            "seafood": ["fish", "salmon", "tuna", "shrimp"],
            "bakery": ["bread", "bagel", "roll", "croissant"],
            "frozen": ["frozen", "ice cream"],
            "canned": ["canned", "can of"],
            "beverages": ["juice", "soda", "coffee", "tea", "water"],
            "snacks": ["chips", "cookies", "crackers", "nuts"],
            "condiments": ["ketchup", "mustard", "mayo", "sauce", "dressing"],
            "spices": ["salt", "pepper", "spice", "seasoning"],
        }

        for category, words in keywords.items():
            if any(word in product_lower for word in words):
                return category

        return "other"
