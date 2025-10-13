from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class DeliveryZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    coordinates: List[dict]  # [{lat, lng}] polygon points
    assigned_agents: List[str] = []  # user IDs of delivery agents
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryZoneCreate(BaseModel):
    name: str
    coordinates: List[dict]
