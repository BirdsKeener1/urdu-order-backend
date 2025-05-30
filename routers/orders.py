from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Any
from models import Order, User
from database import Database
from auth import get_current_active_user
from voice_service import VoiceService
import asyncio

router = APIRouter()
voice_service = VoiceService()

@router.get("/", response_model=List[Order])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    call_status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Get list of orders"""
    orders = await db.get_orders(skip, limit, status, call_status)
    return orders

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Get order details"""
    order = await db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.post("/{order_id}/call")
async def initiate_call(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Initiate a manual call for an order"""
    order = await db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order["callStatus"] == "calling":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Call already in progress"
        )
    
    # Update order status
    await db.update_order(order_id, {"callStatus": "calling"})
    
    # Initiate call
    call_result = voice_service.make_call(
        order["customerPhone"],
        order["orderNumber"]
    )
    
    # Update order with call information
    await db.update_order(order_id, {
        "callStatus": call_result["status"],
        "lastCallAt": call_result["timestamp"]
    })
    
    return call_result

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Update order status"""
    order = await db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order status
    updated_order = await db.update_order(order_id, {"status": status})
    return updated_order

@router.get("/{order_id}/call-status")
async def get_call_status(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
) -> Any:
    """Get call status for an order"""
    order = await db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order.get("call_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No call initiated for this order"
        )
    
    call_status = voice_service.get_call_status(order["call_sid"])
    if not call_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    return call_status 