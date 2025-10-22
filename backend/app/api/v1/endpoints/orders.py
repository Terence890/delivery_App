from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import httpx

from app.db.mongodb import get_database
from app.models.order import Order, OrderCreate, OrderStatusUpdate, OrderItem
from app.models.product import Product
from app.models.user import UserResponse, UserRole
from app.models.route import Waypoint
from app.core.security import require_role, get_current_user
from app.services.geospatial_service import get_zone_for_location, extract_coordinates_from_address

router = APIRouter()

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

@router.post("", response_model=Order)
async def create_order(order_data: OrderCreate, current_user: UserResponse = Depends(get_current_user)):
    db = await get_database()
    
    # Get cart items
    cart = await db.carts.find_one({"user_id": current_user.id})
    if not cart or not cart.get('items'):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Validate delivery address is within a delivery zone
    coordinates = None
    
    # Check if coordinates are provided directly (from Expo location)
    if order_data.delivery_coordinates and 'latitude' in order_data.delivery_coordinates and 'longitude' in order_data.delivery_coordinates:
        try:
            latitude = float(order_data.delivery_coordinates['latitude'])
            longitude = float(order_data.delivery_coordinates['longitude'])
            coordinates = (latitude, longitude)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400, 
                detail="Invalid delivery coordinates format. Latitude and longitude must be numeric."
            )
    else:
        # Extract coordinates from address string (fallback method)
        coordinates = extract_coordinates_from_address(order_data.delivery_address)
        if not coordinates:
            # In a real implementation, we would use a geocoding service here
            raise HTTPException(
                status_code=400, 
                detail="Could not extract coordinates from delivery address. Please include coordinates in format 'lat,lng: 13.1056,77.5951' at the end of the address or provide delivery_coordinates object"
            )
    
    latitude, longitude = coordinates
    zone = await get_zone_for_location(db, longitude, latitude)
    if not zone:
        raise HTTPException(
            status_code=400, 
            detail="Delivery not available for this address. The location is outside all delivery zones."
        )
    
    # Calculate order items and total
    order_items = []
    total_amount = 0
    
    for cart_item in cart['items']:
        product = await db.products.find_one({"id": cart_item['product_id']})
        if not product:
            continue
        
        # Check stock
        if product['stock'] < cart_item['quantity']:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        item_total = product['price'] * cart_item['quantity']
        total_amount += item_total
        
        order_items.append(OrderItem(
            product_id=product['id'],
            product_name=product['name'],
            quantity=cart_item['quantity'],
            price=product['price']
        ).dict())
        
        # Update stock
        await db.products.update_one(
            {"id": product['id']},
            {"$inc": {"stock": -cart_item['quantity']}}
        )
    
    # Calculate estimated delivery time
    estimated_time = None
    try:
        # Get the delivery agent's location (for demo purposes, we'll use a fixed point)
        # In a real implementation, you would get the actual agent's location
        agent_location = {"latitude": 13.1056, "longitude": 77.5951}  # Example agent location
        customer_location = {"latitude": latitude, "longitude": longitude}
        
        # Calculate distance between agent and customer
        distance = calculate_distance(agent_location, customer_location)
        
        # Estimate delivery time
        estimated_time = estimate_delivery_time(distance)
    except Exception as e:
        # If there's an error calculating ETA, we'll just leave it as None
        print(f"Error calculating estimated delivery time: {e}")
    
    # Create order with delivery location and estimated time
    order = Order(
        user_id=current_user.id,
        user_name=current_user.name,
        user_phone=current_user.phone or "N/A",
        user_address=order_data.delivery_address,
        items=order_items,
        total_amount=total_amount,
        delivery_location={
            "latitude": latitude,
            "longitude": longitude
        },
        estimated_delivery_time=estimated_time
    )
    
    await db.orders.insert_one(order.dict())
    
    # Clear cart
    await db.carts.update_one(
        {"user_id": current_user.id},
        {"$set": {"items": []}}
    )
    
    return order

@router.get("", response_model=List[Order])
async def get_orders(current_user: UserResponse = Depends(get_current_user)):
    db = await get_database()
    if current_user.role == UserRole.ADMIN:
        orders = await db.orders.find().sort("created_at", -1).to_list(1000)
    elif current_user.role == UserRole.DELIVERY_AGENT:
        orders = await db.orders.find({
            "$or": [
                {"delivery_agent_id": current_user.id},
                {"status": "confirmed"}
            ]
        }).sort("created_at", -1).to_list(1000)
    else:
        orders = await db.orders.find({"user_id": current_user.id}).sort("created_at", -1).to_list(1000)
    
    return [Order(**o) for o in orders]

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str, current_user: UserResponse = Depends(get_current_user)):
    db = await get_database()
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.DELIVERY_AGENT] and order['user_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return Order(**order)

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, status_update: OrderStatusUpdate, current_user: UserResponse = Depends(get_current_user)):
    db = await get_database()
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.role == UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Not authorized to update order status")
    
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": status_update.status, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Order status updated"}

@router.post("/{order_id}/accept")
async def accept_order(order_id: str, current_user: UserResponse = Depends(require_role([UserRole.DELIVERY_AGENT]))):
    db = await get_database()
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.get('delivery_agent_id'):
        raise HTTPException(status_code=400, detail="Order already accepted by another agent")
    
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "delivery_agent_id": current_user.id,
            "status": "preparing",
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Order accepted"}