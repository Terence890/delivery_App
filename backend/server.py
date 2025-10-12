from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
import httpx # Import httpx for making async HTTP requests

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(str(ROOT_DIR / '.env'))

# ============= DATABASE =============

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ['JWT_SECRET']
ALGORITHM = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    client.close()

# Create the main app
app = FastAPI(lifespan=lifespan)
api_router = APIRouter()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Delivery App API"}

# ============= MODELS =============

class UserRole:
    CUSTOMER = "customer"
    DELIVERY_AGENT = "delivery_agent"
    ADMIN = "admin"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password: str
    name: str
    role: str = UserRole.CUSTOMER
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_zone_id: Optional[str] = None  # For delivery agents
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = UserRole.CUSTOMER
    phone: Optional[str] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_zone_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

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

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    user_phone: str
    user_address: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    delivery_agent_id: Optional[str] = None
    delivery_location: Optional[dict] = None  # {lat, lng}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    items: List[CartItem]
    delivery_address: str

class OrderStatusUpdate(BaseModel):
    status: str

class DeliveryZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    coordinates: List[dict]  # [{lat, lng}] polygon points
    assigned_agents: List[str] = []  # user IDs of delivery agents
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryZoneCreate(BaseModel):
    name: str
    coordinates: List[dict]

# ============= AUTHENTICATION HELPERS =============

security = HTTPBearer()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return UserResponse(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker

# ============= AUTH ROUTES =============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = User(
            **user_data.dict(exclude={'password'}),
            password=hash_password(user_data.password)
        )
        await db.users.insert_one(user.dict())
        
        # Create token
        access_token = create_access_token(data={"sub": user.id, "role": user.role})
        
        user_response = UserResponse(**user.dict())
        return TokenResponse(access_token=access_token, user=user_response)
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="Could not connect to the database.")
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user['id'], "role": user['role']})
    user_response = UserResponse(**user)
    return TokenResponse(access_token=access_token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

# ============= PRODUCT ROUTES =============

@api_router.get("/products", response_model=PaginatedProductsResponse)
async def get_products(category: str = None, page: int = 1, limit: int = 20):
    query = {}
    if category:
        query["category"] = category
    
    # Calculate skip value for pagination
    skip = (page - 1) * limit
    
    # Get total count of products for the query
    total_products = await db.products.count_documents(query)
    
    # Fetch products with pagination
    products_cursor = db.products.find(query).skip(skip).limit(limit)
    products = await products_cursor.to_list(length=limit)
    
    return PaginatedProductsResponse(
        total=total_products,
        products=[Product(**p) for p in products]
    )

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    product = Product(**product_data.dict())
    await db.products.insert_one(product.dict())
    return product

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_data: ProductCreate, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    result = await db.products.update_one({"id": product_id}, {"$set": product_data.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = await db.products.find_one({"id": product_id})
    return Product(**updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@api_router.get("/categories")
async def get_categories():
    categories = await db.products.distinct("category")
    return {"categories": categories}

# ============= CART ROUTES =============

@api_router.get("/cart")
async def get_cart(current_user: UserResponse = Depends(get_current_user)):
    cart = await db.carts.find_one({"user_id": current_user.id})
    if not cart:
        cart = Cart(user_id=current_user.id).dict()
        await db.carts.insert_one(cart)
    
    # Populate product details
    cart_items = []
    for item in cart.get('items', []):
        product = await db.products.find_one({"id": item['product_id']})
        if product:
            cart_items.append({
                **item,
                "product": Product(**product).dict()
            })
    
    return {"items": cart_items}

@api_router.post("/cart/add")
async def add_to_cart(item: CartItem, current_user: UserResponse = Depends(get_current_user)):
    # Check if product exists
    product = await db.products.find_one({"id": item.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get or create cart
    cart = await db.carts.find_one({"user_id": current_user.id})
    if not cart:
        cart = Cart(user_id=current_user.id).dict()
        await db.carts.insert_one(cart)
    
    # Update cart items
    items = cart.get('items', [])
    existing_item = next((i for i in items if i['product_id'] == item.product_id), None)
    
    if existing_item:
        existing_item['quantity'] += item.quantity
    else:
        items.append(item.dict())
    
    await db.carts.update_one(
        {"user_id": current_user.id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Item added to cart"}

@api_router.post("/cart/remove/{product_id}")
async def remove_from_cart(product_id: str, current_user: UserResponse = Depends(get_current_user)):
    cart = await db.carts.find_one({"user_id": current_user.id})
    if cart:
        items = [i for i in cart.get('items', []) if i['product_id'] != product_id]
        await db.carts.update_one(
            {"user_id": current_user.id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}}
        )
    return {"message": "Item removed from cart"}

@api_router.post("/cart/update")
async def update_cart_item(item: CartItem, current_user: UserResponse = Depends(get_current_user)):
    cart = await db.carts.find_one({"user_id": current_user.id})
    if cart:
        items = cart.get('items', [])
        for i in items:
            if i['product_id'] == item.product_id:
                i['quantity'] = item.quantity
                break
        await db.carts.update_one(
            {"user_id": current_user.id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}}
        )
    return {"message": "Cart updated"}

@api_router.delete("/cart/clear")
async def clear_cart(current_user: UserResponse = Depends(get_current_user)):
    await db.carts.update_one(
        {"user_id": current_user.id},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )
    return {"message": "Cart cleared"}

# ============= ORDER ROUTES =============

@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, current_user: UserResponse = Depends(get_current_user)):
    # Get cart items
    cart = await db.carts.find_one({"user_id": current_user.id})
    if not cart or not cart.get('items'):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
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
    
    # Create order
    order = Order(
        user_id=current_user.id,
        user_name=current_user.name,
        user_phone=current_user.phone or "N/A",
        user_address=order_data.delivery_address,
        items=order_items,
        total_amount=total_amount
    )
    
    await db.orders.insert_one(order.dict())
    
    # Clear cart
    await db.carts.update_one(
        {"user_id": current_user.id},
        {"$set": {"items": []}}
    )
    
    return order

@api_router.get("/orders", response_model=List[Order])
async def get_orders(current_user: UserResponse = Depends(get_current_user)):
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

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, current_user: UserResponse = Depends(get_current_user)):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.DELIVERY_AGENT] and order['user_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return Order(**order)

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status_update: OrderStatusUpdate, current_user: UserResponse = Depends(get_current_user)):
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

@api_router.post("/orders/{order_id}/accept")
async def accept_order(order_id: str, current_user: UserResponse = Depends(require_role([UserRole.DELIVERY_AGENT]))):
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

# ============= DELIVERY ZONE ROUTES =============

@api_router.get("/delivery-zones", response_model=List[DeliveryZone])
async def get_delivery_zones(current_user: UserResponse = Depends(get_current_user)):
    zones = await db.delivery_zones.find().to_list(1000)
    return [DeliveryZone(**z) for z in zones]

@api_router.post("/delivery-zones", response_model=DeliveryZone)
async def create_delivery_zone(zone_data: DeliveryZoneCreate, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    zone = DeliveryZone(**zone_data.dict())
    await db.delivery_zones.insert_one(zone.dict())
    return zone

@api_router.put("/delivery-zones/{zone_id}/assign-agent")
async def assign_agent_to_zone(zone_id: str, agent_id: str, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
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

# ============= ROUTING ROUTES =============

class Waypoint(BaseModel):
    latitude: float
    longitude: float

@api_router.post("/route/optimize")
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

# ============= ADMIN STATS =============

@api_router.get("/admin/stats")
async def get_admin_stats(current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    total_products = await db.products.count_documents({})
    total_orders = await db.orders.count_documents({})
    total_customers = await db.users.count_documents({"role": UserRole.CUSTOMER})
    total_agents = await db.users.count_documents({"role": UserRole.DELIVERY_AGENT})
    
    # Calculate revenue
    orders = await db.orders.find({"status": "delivered"}).to_list(1000)
    total_revenue = sum(order.get('total_amount', 0) for order in orders)
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_agents": total_agents,
        "total_revenue": total_revenue
    }

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)