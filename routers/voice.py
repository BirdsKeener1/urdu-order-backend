from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from typing import Any, Dict
from models import User
from database import Database
from auth import get_current_active_user
from voice_service import VoiceService
import os

router = APIRouter()
voice_service = VoiceService()

@router.get("/welcome/{order_number}")
async def welcome_call(
    order_number: str,
    request: Request,
    db: Database = Depends()
) -> Response:
    """Handle welcome call and generate IVR response"""
    # Generate IVR response
    response = voice_service.generate_ivr_response(order_number)
    return Response(content=response, media_type="application/xml")

@router.post("/handle-input/{order_number}")
async def handle_ivr_input(
    order_number: str,
    request: Request,
    db: Database = Depends()
) -> Response:
    """Handle IVR input from customer"""
    # Get form data
    form_data = await request.form()
    digit = form_data.get("Digits")
    
    if not digit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input received"
        )
    
    # Get order from database
    order = await db.get_order_by_number(order_number)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Handle input
    response = voice_service.handle_input(order_number, digit)
    
    # Update order status based on input
    if digit == "1":  # Confirm order
        await db.update_order(order["id"], {"status": "confirmed"})
    elif digit == "0":  # Cancel order
        await db.update_order(order["id"], {"status": "cancelled"})
    elif digit == "2":  # Support
        await db.update_order(order["id"], {"status": "support"})
    
    return Response(content=response, media_type="application/xml")

@router.get("/settings")
async def get_voice_settings(
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Get voice settings for the store"""
    if not current_user.store_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No store connected"
        )
    
    store = await db.get_store(current_user.store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    return store["voiceSettings"]

@router.put("/settings")
async def update_voice_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Update voice settings for the store"""
    if not current_user.store_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No store connected"
        )
    
    store = await db.get_store(current_user.store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Update settings
    updated_store = await db.update_store(
        store["id"],
        {"voiceSettings": settings}
    )
    
    return updated_store["voiceSettings"]

@router.post("/test")
async def test_voice_call(
    phone_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Test voice call with current settings"""
    if not current_user.store_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No store connected"
        )
    
    store = await db.get_store(current_user.store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Make test call
    call_result = voice_service.make_call(
        phone_number,
        "TEST-ORDER"
    )
    
    return call_result 