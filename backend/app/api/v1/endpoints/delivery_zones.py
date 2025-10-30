from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.db.mongodb import get_database
from app.models.delivery_zone import DeliveryZone, DeliveryZoneCreate, DeliveryZoneLegacy, GeoJSONPolygon
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
async def create_delivery_zone(zone_data: Dict[str, Any], current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = await get_database()
    
    # Handle GeoJSON FeatureCollection format
    if zone_data.get('type') == 'FeatureCollection':
        features = zone_data.get('features', [])
        if not features:
            raise HTTPException(status_code=400, detail="FeatureCollection must contain at least one feature")
        
        # Process the first feature (assuming single polygon)
        feature = features[0]
        geometry = feature.get('geometry', {})
        
        if geometry.get('type') != 'Polygon':
            raise HTTPException(status_code=400, detail="Geometry must be a Polygon")
        
        # Create delivery zone with the polygon data
        delivery_zone_data = {
            "id": str(uuid.uuid4()),
            "name": feature.get('properties', {}).get('name', f'Delivery Zone {str(uuid.uuid4())[:8]}'),
            "geometry": {
                "type": "Polygon",
                "coordinates": geometry.get('coordinates', [])
            },
            "assigned_agents": [],
            "created_at": datetime.utcnow()
        }
        
        await db.delivery_zones.insert_one(delivery_zone_data)
        return DeliveryZone(**delivery_zone_data)
    
    # Handle standard DeliveryZoneCreate format
    elif 'name' in zone_data and 'geometry' in zone_data:
        try:
            delivery_zone_create = DeliveryZoneCreate(**zone_data)
            zone = DeliveryZone(**delivery_zone_create.dict())
            await db.delivery_zones.insert_one(zone.dict())
            return zone
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid delivery zone format: {str(e)}")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid delivery zone data format. Must be either DeliveryZoneCreate or GeoJSON FeatureCollection.")

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