from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class UserRole:
    CUSTOMER = "customer"
    DELIVERY_AGENT = "delivery_agent"
    ADMIN = "admin"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password: str
    name: str
    role: str = UserRole.CUSTOMER
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_zone_id: Optional[str] = None  # For delivery agents
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = UserRole.CUSTOMER
    phone: Optional[str] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_zone_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
