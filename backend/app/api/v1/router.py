from fastapi import APIRouter

from .products import router as products_router

api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(products_router)

# You can add more routers here as needed
# api_router.include_router(auth_router)
# api_router.include_router(cart_router)
# api_router.include_router(order_router)