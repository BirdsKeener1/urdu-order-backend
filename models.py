from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CALLED = "called"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    SUPPORT = "support"

class CallStatus(str, Enum):
    NOT_CALLED = "not_called"
    CALLING = "calling"
    COMPLETED = "completed"
    FAILED = "failed"

class CallHistory(BaseModel):
    timestamp: datetime
    status: str
    duration: Optional[int] = None
    response: Optional[str] = None

class Order(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    shopifyOrderId: str
    orderNumber: str
    customerName: str
    customerPhone: str
    amount: float
    status: OrderStatus = OrderStatus.PENDING
    callStatus: CallStatus = CallStatus.NOT_CALLED
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastCallAt: Optional[datetime] = None
    callHistory: List[CallHistory] = []

class Store(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    shopifyDomain: str
    accessToken: str
    webhookSecret: str
    voiceSettings: dict = {
        "language": "ur",
        "voiceId": "default",
        "retryAttempts": 3,
        "retryDelay": 300  # seconds
    }
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    hashed_password: str
    store_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 