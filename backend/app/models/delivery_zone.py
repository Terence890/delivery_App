from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]  # [longitude, latitude] pairs

class DeliveryZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    geometry: GeoJSONPolygon
    assigned_agents: List[str] = []  # user IDs of delivery agents
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryZoneCreate(BaseModel):
    name: str
    geometry: GeoJSONPolygon

# Keep the old model for backward compatibility
class DeliveryZoneLegacy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    coordinates: List[dict]  # [{lat, lng}] polygon points
    assigned_agents: List[str] = []  # user IDs of delivery agents
    created_at: datetime = Field(default_factory=datetime.utcnow)