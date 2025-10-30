from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    user_phone: str
    user_address: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    delivery_agent_id: Optional[str] = None
    delivery_location: Optional[dict] = None  # {latitude, longitude}
    estimated_delivery_time: Optional[dict] = None  # {minutes: int, formatted: str}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    items: List[dict]  # Use dict here to avoid circular dependency with CartItem
    delivery_address: str
    delivery_coordinates: Optional[dict] = None  # {latitude: float, longitude: float}

class OrderStatusUpdate(BaseModel):
    status: str