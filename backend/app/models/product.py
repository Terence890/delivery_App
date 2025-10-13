from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: str
    description: str
    price: float
    category: str
    stock: int
    unit: str
    variant: str
    code: Optional[str] = None
    barcode: Optional[str] = None
    image: str  # base64 encoded
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaginatedProductsResponse(BaseModel):
    total: int
    products: List[Product]

class ProductCreate(BaseModel):
    name: str
    brand: str
    description: str
    price: float
    category: str
    stock: int
    unit: str
    variant: str
    code: Optional[str] = None
    barcode: Optional[str] = None
    image: str
