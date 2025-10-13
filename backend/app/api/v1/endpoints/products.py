from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.db.mongodb import get_database
from app.models.product import Product, ProductCreate, PaginatedProductsResponse
from app.models.user import UserResponse, UserRole
from app.core.security import require_role, get_current_user

router = APIRouter()

@router.get("", response_model=PaginatedProductsResponse)
async def get_products(category: str = None, page: int = 1, limit: int = 20):
    db = get_database()
    query = {}
    if category:
        query["category"] = category
    
    skip = (page - 1) * limit
    total_products = await db.products.count_documents(query)
    products_cursor = db.products.find(query).skip(skip).limit(limit)
    products = await products_cursor.to_list(length=limit)
    
    return PaginatedProductsResponse(
        total=total_products,
        products=[Product(**p) for p in products]
    )

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    db = get_database()
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@router.post("/", response_model=Product)
async def create_product(product_data: ProductCreate, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = get_database()
    product = Product(**product_data.dict())
    await db.products.insert_one(product.dict())
    return product

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product_data: ProductCreate, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = get_database()
    result = await db.products.update_one({"id": product_id}, {"$set": product_data.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = await db.products.find_one({"id": product_id})
    return Product(**updated_product)

@router.delete("/{product_id}")
async def delete_product(product_id: str, current_user: UserResponse = Depends(require_role([UserRole.ADMIN]))):
    db = get_database()
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.get("/categories")
async def get_categories():
    db = get_database()
    categories = await db.products.distinct("category")
    return {"categories": categories}
