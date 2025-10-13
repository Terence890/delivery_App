from fastapi import APIRouter, HTTPException, Depends

from app.db.mongodb import get_database
from app.models.user import UserResponse, UserRole
from app.core.security import require_role

router = APIRouter()

@router.get("/stats")
async def get_admin_stats(current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = get_database()
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
