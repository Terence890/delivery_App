from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.db.mongodb import get_database
from app.models.delivery_zone import DeliveryZone, DeliveryZoneCreate, DeliveryZoneLegacy
from app.models.user import UserResponse, UserRole
from app.core.security import require_role, get_current_user

router = APIRouter()

@router.get("", response_model=List[DeliveryZone])
async def get_delivery_zones(current_user: UserResponse = Depends(get_current_user)):
    db = await get_database()
    zones = await db.delivery_zones.find().to_list(1000)
    
    # Convert legacy format to new format if needed
    converted_zones = []
    for zone in zones:
        if 'coordinates' in zone and 'geometry' not in zone:
            # Convert legacy format to GeoJSON
            coords = [[point['lng'], point['lat']] for point in zone['coordinates']]
            # Close the polygon if not already closed
            if coords and coords[0] != coords[-1]:
                coords.append(coords[0])
            zone['geometry'] = {
                'type': 'Polygon',
                'coordinates': [coords]
            }
            # Remove old coordinates field
            del zone['coordinates']
        converted_zones.append(zone)
    
    return [DeliveryZone(**z) for z in converted_zones]

@router.post("/", response_model=DeliveryZone)
async def create_delivery_zone(zone_data: DeliveryZoneCreate, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = await get_database()
    zone = DeliveryZone(**zone_data.dict())
    await db.delivery_zones.insert_one(zone.dict())
    return zone

@router.put("/{zone_id}/assign-agent")
async def assign_agent_to_zone(zone_id: str, agent_id: str, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = await get_database()
    zone = await db.delivery_zones.find_one({"id": zone_id})
    if not zone:
        raise HTTPException(status_code=404, detail="Delivery zone not found")
    
    # Check if agent exists and is delivery agent
    agent = await db.users.find_one({"id": agent_id, "role": UserRole.DELIVERY_AGENT})
    if not agent:
        raise HTTPException(status_code=404, detail="Delivery agent not found")
    
    # Add agent to zone
    assigned_agents = zone.get('assigned_agents', [])
    if agent_id not in assigned_agents:
        assigned_agents.append(agent_id)
    
    await db.delivery_zones.update_one(
        {"id": zone_id},
        {"$set": {"assigned_agents": assigned_agents}}
    )
    
    # Update agent's zone
    await db.users.update_one(
        {"id": agent_id},
        {"$set": {"delivery_zone_id": zone_id}}
    )
    
    return {"message": "Agent assigned to zone"}