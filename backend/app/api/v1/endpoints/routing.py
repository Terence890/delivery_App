from fastapi import APIRouter, HTTPException, Depends
from typing import List
import httpx
import logging

from app.models.route import Waypoint
from app.models.user import UserResponse, UserRole
from app.core.security import require_role

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/optimize")
async def optimize_route(waypoints: List[Waypoint], current_user: UserResponse = Depends(require_role([UserRole.DELIVERY_AGENT, UserRole.ADMIN]))):
    if not waypoints or len(waypoints) < 2:
        raise HTTPException(status_code=400, detail="At least two waypoints are required for routing.")

    # Format waypoints for OSRM API
    osrm_waypoints = ";".join([f"{wp.longitude},{wp.latitude}" for wp in waypoints])
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{osrm_waypoints}?geometries=geojson&overview=full"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(osrm_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            osrm_data = response.json()

        if osrm_data.get("routes") and len(osrm_data["routes"]) > 0:
            route_geometry = osrm_data["routes"][0]["geometry"]["coordinates"]
            # OSRM returns [longitude, latitude], convert to [latitude, longitude]
            route_coordinates = [{
                "latitude": coord[1],
                "longitude": coord[0]
            } for coord in route_geometry]
            return {"route": route_coordinates}
        else:
            raise HTTPException(status_code=404, detail="No route found for the given waypoints.")

    except httpx.HTTPStatusError as e:
        logger.error(f"OSRM HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Routing service error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"OSRM request error: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to routing service: {e}")
    except Exception as e:
        logger.error(f"Unexpected routing error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during routing.")
