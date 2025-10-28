from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.receipt import Receipt, ReceiptLineItem
from app.models.inventory import InventoryItem
from app.schemas.receipt import (
    ReceiptResponse,
    ReceiptProcessingResponse,
    ReceiptConfirmation,
    ReceiptLineItemResponse
)
from app.services.ocr_service import OCRService
from app.core.config import settings

router = APIRouter()
ocr_service = OCRService()


async def process_receipt_async(
    receipt_id: int,
    image_path: str,
    db: Session,
    household_id: int
):
    """Background task to process receipt with OCR."""
    try:
        # Process with OCR
        result = await ocr_service.process_receipt(image_path)

        # Update receipt with OCR results
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            return

        receipt.merchant_name = result.get("merchant_name")
        receipt.merchant_address = result.get("merchant_address")
        receipt.total_amount = result.get("total_amount")
        receipt.tax_amount = result.get("tax_amount")
        receipt.receipt_number = result.get("receipt_number")
        receipt.ocr_provider = result.get("provider")
        receipt.processing_time_ms = result.get("processing_time_ms")
        receipt.processing_status = "completed"
        receipt.is_processed = True

        if result.get("purchase_date"):
            receipt.purchase_date = datetime.fromisoformat(result["purchase_date"])

        # Check for duplicates
        existing_receipts = db.query(Receipt).filter(
            Receipt.household_id == household_id,
            Receipt.id != receipt_id
        ).all()

        duplicate_id = ocr_service.detect_duplicate(result, existing_receipts)
        if duplicate_id:
            receipt.is_duplicate = True
            receipt.duplicate_of_id = duplicate_id

        # Add line items
        for line_item_data in result.get("line_items", []):
            line_item = ReceiptLineItem(
                receipt_id=receipt_id,
                description=line_item_data.get("description"),
                quantity=line_item_data.get("quantity", 1.0),
                unit_price=line_item_data.get("unit_price"),
                total_price=line_item_data.get("total_price")
            )
            db.add(line_item)

        db.commit()

    except Exception as e:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if receipt:
            receipt.processing_status = "failed"
            receipt.processing_error = str(e)
            db.commit()


@router.post("/upload", response_model=ReceiptProcessingResponse, status_code=201)
async def upload_receipt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process a receipt image."""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save file
    os.makedirs(settings.RECEIPTS_DIR, exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.RECEIPTS_DIR, unique_filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create receipt record
    receipt = Receipt(
        uploaded_by_id=current_user.id,
        household_id=current_user.household_id,
        image_path=file_path,
        image_url=f"/receipts/{unique_filename}",
        processing_status="processing"
    )

    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    # Process in background
    background_tasks.add_task(
        process_receipt_async,
        receipt.id,
        file_path,
        db,
        current_user.household_id
    )

    return {
        "receipt_id": receipt.id,
        "status": "processing",
        "processing_time_ms": 0,
        "line_items_count": 0,
        "is_duplicate": False
    }


@router.get("/", response_model=List[ReceiptResponse])
def get_receipts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all receipts for the user's household."""
    receipts = db.query(Receipt).filter(
        Receipt.household_id == current_user.household_id
    ).order_by(Receipt.created_at.desc()).offset(skip).limit(limit).all()

    return receipts


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific receipt with line items."""
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.household_id == current_user.household_id
    ).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return receipt


@router.post("/{receipt_id}/confirm", status_code=200)
def confirm_receipt_items(
    receipt_id: int,
    confirmation: ReceiptConfirmation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Confirm and add receipt line items to inventory."""
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.household_id == current_user.household_id
    ).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    if receipt.items_added:
        raise HTTPException(status_code=400, detail="Items already added to inventory")

    # Get confirmed line items
    line_items = db.query(ReceiptLineItem).filter(
        ReceiptLineItem.receipt_id == receipt_id,
        ReceiptLineItem.id.in_(confirmation.confirmed_items)
    ).all()

    # Add to inventory
    from app.services.ai_service import AIService
    ai_service = AIService()

    for line_item in line_items:
        # Determine category
        category = await ai_service.categorize_product(line_item.description)

        # Estimate expiration
        shelf_life_days = await ai_service.estimate_expiration_date(
            line_item.description,
            category,
            receipt.purchase_date.isoformat() if receipt.purchase_date else datetime.utcnow().isoformat()
        )

        expiration_date = (receipt.purchase_date or datetime.utcnow()) + timedelta(days=shelf_life_days)

        inventory_item = InventoryItem(
            name=line_item.user_corrected_name or line_item.description,
            category=category,
            quantity=line_item.quantity,
            unit="item",
            price=line_item.total_price,
            purchase_date=receipt.purchase_date or datetime.utcnow(),
            expiration_date=expiration_date,
            store=receipt.merchant_name,
            household_id=current_user.household_id,
            added_by=current_user.id,
            receipt_id=receipt_id,
            original_quantity=line_item.quantity
        )
        db.add(inventory_item)

    receipt.items_added = True
    db.commit()

    return {"message": f"Added {len(line_items)} items to inventory"}


@router.delete("/{receipt_id}", status_code=204)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a receipt."""
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.household_id == current_user.household_id
    ).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    # Delete image file
    if receipt.image_path and os.path.exists(receipt.image_path):
        os.remove(receipt.image_path)

    db.delete(receipt)
    db.commit()
