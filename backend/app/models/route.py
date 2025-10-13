from pydantic import BaseModel

class Waypoint(BaseModel):
    latitude: float
    longitude: float
