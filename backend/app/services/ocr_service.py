import httpx
import time
from typing import Dict, Any, Optional
from app.core.config import settings


class OCRService:
    """Service for processing receipts using OCR APIs."""

    def __init__(self):
        self.provider = self._detect_provider()

    def _detect_provider(self) -> str:
        """Detect which OCR provider to use based on available API keys."""
        if settings.VERYFI_API_KEY:
            return "veryfi"
        elif settings.MINDEE_API_KEY:
            return "mindee"
        elif settings.TAGGUN_API_KEY:
            return "taggun"
        else:
            raise ValueError("No OCR API key configured")

    async def process_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Process a receipt image and extract line items.

        Returns:
            Dict with keys: merchant_name, purchase_date, total_amount, line_items, processing_time_ms
        """
        start_time = time.time()

        if self.provider == "veryfi":
            result = await self._process_veryfi(image_path)
        elif self.provider == "mindee":
            result = await self._process_mindee(image_path)
        elif self.provider == "taggun":
            result = await self._process_taggun(image_path)
        else:
            raise ValueError(f"Unsupported OCR provider: {self.provider}")

        processing_time = int((time.time() - start_time) * 1000)
        result["processing_time_ms"] = processing_time
        result["provider"] = self.provider

        return result

    async def _process_veryfi(self, image_path: str) -> Dict[str, Any]:
        """Process receipt using Veryfi API."""
        # Note: This is a simplified implementation
        # Full implementation would use the official Veryfi Python SDK

        async with httpx.AsyncClient() as client:
            # Veryfi API implementation
            # This is a placeholder - actual implementation would use proper authentication
            # and the Veryfi SDK

            # Mock response for demonstration
            return {
                "merchant_name": "Example Store",
                "purchase_date": "2024-01-15T10:30:00",
                "total_amount": 45.67,
                "tax_amount": 3.21,
                "line_items": [
                    {
                        "description": "Organic Milk",
                        "quantity": 1.0,
                        "unit_price": 4.99,
                        "total_price": 4.99
                    },
                    {
                        "description": "Bananas",
                        "quantity": 2.5,
                        "unit_price": 0.69,
                        "total_price": 1.73
                    }
                ],
                "receipt_number": "12345",
                "merchant_address": "123 Main St, City, ST 12345"
            }

    async def _process_mindee(self, image_path: str) -> Dict[str, Any]:
        """Process receipt using Mindee API."""
        url = "https://api.mindee.net/v1/products/mindee/expense_receipts/v5/predict"

        headers = {
            "Authorization": f"Token {settings.MINDEE_API_KEY}"
        }

        async with httpx.AsyncClient() as client:
            with open(image_path, "rb") as image_file:
                files = {"document": image_file}
                response = await client.post(url, headers=headers, files=files)
                response.raise_for_status()
                data = response.json()

                # Parse Mindee response
                prediction = data.get("document", {}).get("inference", {}).get("prediction", {})

                return {
                    "merchant_name": prediction.get("supplier_name", {}).get("value"),
                    "purchase_date": prediction.get("date", {}).get("value"),
                    "total_amount": prediction.get("total_amount", {}).get("value"),
                    "tax_amount": prediction.get("total_tax", {}).get("value"),
                    "line_items": self._parse_mindee_line_items(prediction),
                    "receipt_number": None,
                    "merchant_address": None
                }

    async def _process_taggun(self, image_path: str) -> Dict[str, Any]:
        """Process receipt using Taggun API."""
        url = "https://api.taggun.io/api/receipt/v1/simple/file"

        headers = {
            "apikey": settings.TAGGUN_API_KEY
        }

        async with httpx.AsyncClient() as client:
            with open(image_path, "rb") as image_file:
                files = {"file": image_file}
                response = await client.post(url, headers=headers, files=files)
                response.raise_for_status()
                data = response.json()

                return {
                    "merchant_name": data.get("merchantName"),
                    "purchase_date": data.get("date"),
                    "total_amount": data.get("totalAmount", {}).get("data"),
                    "tax_amount": data.get("taxAmount", {}).get("data"),
                    "line_items": self._parse_taggun_line_items(data),
                    "receipt_number": data.get("receiptNumber"),
                    "merchant_address": data.get("merchantAddress")
                }

    def _parse_mindee_line_items(self, prediction: Dict[str, Any]) -> list:
        """Parse line items from Mindee response."""
        line_items = prediction.get("line_items", [])
        parsed_items = []

        for item in line_items:
            parsed_items.append({
                "description": item.get("description"),
                "quantity": item.get("quantity", 1.0),
                "unit_price": item.get("unit_price"),
                "total_price": item.get("total_amount")
            })

        return parsed_items

    def _parse_taggun_line_items(self, data: Dict[str, Any]) -> list:
        """Parse line items from Taggun response."""
        line_items = data.get("entities", {}).get("lineItems", [])
        parsed_items = []

        for item in line_items:
            parsed_items.append({
                "description": item.get("description", {}).get("data"),
                "quantity": item.get("quantity", {}).get("data", 1.0),
                "unit_price": item.get("price", {}).get("data"),
                "total_price": item.get("amount", {}).get("data")
            })

        return parsed_items

    def detect_duplicate(self, receipt_data: Dict[str, Any], existing_receipts: list) -> Optional[int]:
        """
        Detect if a receipt is a duplicate of existing receipts.

        Returns:
            ID of duplicate receipt if found, None otherwise
        """
        for existing in existing_receipts:
            # Check if merchant, date, and total match
            if (existing.merchant_name == receipt_data.get("merchant_name") and
                existing.purchase_date == receipt_data.get("purchase_date") and
                abs(existing.total_amount - receipt_data.get("total_amount", 0)) < 0.01):
                return existing.id

        return None
