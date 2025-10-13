from fastapi import APIRouter

from app.api.v1.endpoints import auth, products, cart, orders, delivery_zones, routing, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(delivery_zones.router, prefix="/delivery-zones", tags=["delivery-zones"])
api_router.include_router(routing.router, prefix="/route", tags=["routing"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
