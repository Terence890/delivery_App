from typing import Optional, Dict, Any
import math

def is_point_in_polygon(point: tuple, polygon: list) -> bool:
    """
    Check if a point is inside a polygon using the ray casting algorithm.
    
    Args:
        point: Tuple of (longitude, latitude)
        polygon: List of [longitude, latitude] points forming a polygon (GeoJSON format)
    
    Returns:
        bool: True if point is inside polygon, False otherwise
    """
    x, y = point
    n = len(polygon[0]) if polygon and polygon[0] else 0
    if n < 3:
        return False
    
    inside = False
    p1x, p1y = polygon[0][0]
    
    for i in range(1, n + 1):
        p2x, p2y = polygon[0][i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

async def get_zone_for_location(db, longitude: float, latitude: float) -> Optional[Dict[str, Any]]:
    """
    Find which delivery zone contains a specific location.
    
    Args:
        db: Database connection
        longitude: Longitude coordinate
        latitude: Latitude coordinate
    
    Returns:
        dict: Delivery zone document if found, None otherwise
    """
    # Use MongoDB's geospatial query if available
    try:
        # Try to use MongoDB's native geospatial query
        point = {
            "type": "Point",
            "coordinates": [longitude, latitude]  # GeoJSON format [lng, lat]
        }
        
        zone = await db.delivery_zones.find_one({
            "geometry": {
                "$geoIntersects": {
                    "$geometry": point
                }
            }
        })
        
        return zone
    except Exception:
        # Fallback to manual polygon checking
        zones = await db.delivery_zones.find().to_list(1000)
        
        for zone in zones:
            if 'geometry' in zone and zone['geometry'].get('type') == 'Polygon':
                if is_point_in_polygon((longitude, latitude), zone['geometry']['coordinates']):
                    return zone
        
        return None

def extract_coordinates_from_address(address: str) -> Optional[tuple]:
    """
    Extract coordinates from an address string.
    This is a simplified implementation - in a real system, you would use a geocoding service.
    
    Args:
        address: Address string that may contain coordinates
    
    Returns:
        tuple: (latitude, longitude) if found, None otherwise
    """
    # Check if address contains coordinates in format "lat,lng: 13.1056,77.5951"
    if "lat,lng:" in address:
        try:
            coords_part = address.split("lat,lng:")[1].strip()
            lat, lng = map(float, coords_part.split(","))
            return (lat, lng)
        except:
            pass
    
    # In a real implementation, you would call a geocoding service here
    # For example: Google Maps Geocoding API, OpenStreetMap Nominatim, etc.
    
    return None