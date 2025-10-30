from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import httpx
import logging
from datetime import datetime, timedelta

from app.models.route import Waypoint
from app.models.user import UserResponse, UserRole
from app.core.security import require_role

router = APIRouter()
logger = logging.getLogger(__name__)

# Average delivery speed in km/h
AVERAGE_DELIVERY_SPEED = 30  # Adjust based on your requirements

def calculate_distance(coord1: dict, coord2: dict) -> float:
    """
    Calculate the approximate distance between two coordinates using the haversine formula.
    Returns distance in kilometers.
    """
    import math
    
    # Earth's radius in kilometers
    R = 6371.0
    
    lat1_rad = math.radians(coord1['latitude'])
    lon1_rad = math.radians(coord1['longitude'])
    lat2_rad = math.radians(coord2['latitude'])
    lon2_rad = math.radians(coord2['longitude'])
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def estimate_delivery_time(distance_km: float, speed_kmh: float = AVERAGE_DELIVERY_SPEED) -> dict:
    """
    Estimate delivery time based on distance and speed.
    Returns a dictionary with estimated time and formatted string.
    """
    if distance_km <= 0:
        return {
            "minutes": 5,
            "formatted": "5 minutes or less"
        }
    
    # Calculate time in hours
    time_hours = distance_km / speed_kmh
    
    # Convert to minutes
    time_minutes = int(time_hours * 60)
    
    # Ensure minimum time of 5 minutes
    time_minutes = max(time_minutes, 5)
    
    # Format the time string
    if time_minutes < 60:
        formatted_time = f"{time_minutes} minutes"
    else:
        hours = time_minutes // 60
        minutes = time_minutes % 60
        if minutes == 0:
            formatted_time = f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            formatted_time = f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minute{'s' if minutes > 1 else ''}"
    
    return {
        "minutes": time_minutes,
        "formatted": formatted_time
    }

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
            
            # Calculate total distance
            total_distance = 0.0
            for i in range(len(waypoints) - 1):
                distance = calculate_distance(
                    {"latitude": waypoints[i].latitude, "longitude": waypoints[i].longitude},
                    {"latitude": waypoints[i+1].latitude, "longitude": waypoints[i+1].longitude}
                )
                total_distance += distance
            
            # Estimate delivery time
            estimated_time = estimate_delivery_time(total_distance)
            
            return {
                "route": route_coordinates,
                "distance_km": round(total_distance, 2),
                "estimated_delivery_time": estimated_time
            }
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

@router.post("/optimize-with-eta")
async def optimize_route_with_eta(waypoints: List[Waypoint], current_user: UserResponse = Depends(require_role([UserRole.DELIVERY_AGENT, UserRole.ADMIN]))):
    """
    Optimize route and provide detailed ETA information including delivery times for each waypoint.
    """
    if not waypoints or len(waypoints) < 2:
        raise HTTPException(status_code=400, detail="At least two waypoints are required for routing.")

    # Format waypoints for OSRM API
    osrm_waypoints = ";".join([f"{wp.longitude},{wp.latitude}" for wp in waypoints])
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{osrm_waypoints}?geometries=geojson&overview=full&steps=true"

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
            
            # Calculate total distance and individual segment distances
            total_distance = 0.0
            segment_distances = []
            
            for i in range(len(waypoints) - 1):
                distance = calculate_distance(
                    {"latitude": waypoints[i].latitude, "longitude": waypoints[i].longitude},
                    {"latitude": waypoints[i+1].latitude, "longitude": waypoints[i+1].longitude}
                )
                segment_distances.append(distance)
                total_distance += distance
            
            # Estimate delivery time for the entire route
            estimated_time = estimate_delivery_time(total_distance)
            
            # Calculate ETA for each waypoint
            waypoint_etas = []
            cumulative_time = 0
            
            # Start time is now
            start_time = datetime.now()
            waypoint_etas.append({
                "waypoint_index": 0,
                "waypoint": waypoints[0].dict(),
                "eta": start_time.isoformat(),
                "cumulative_minutes": 0
            })
            
            for i, distance in enumerate(segment_distances):
                segment_time = estimate_delivery_time(distance)
                cumulative_time += segment_time["minutes"]
                
                eta_time = start_time + timedelta(minutes=cumulative_time)
                waypoint_etas.append({
                    "waypoint_index": i + 1,
                    "waypoint": waypoints[i + 1].dict(),
                    "eta": eta_time.isoformat(),
                    "cumulative_minutes": cumulative_time
                })
            
            return {
                "route": route_coordinates,
                "distance_km": round(total_distance, 2),
                "estimated_delivery_time": estimated_time,
                "waypoint_etas": waypoint_etas
            }
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