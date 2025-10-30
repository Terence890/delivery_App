from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from ...core.security import get_current_user, require_role
from ...models.user import UserResponse, UserRole
from ...models.product import Product, ProductCreate
from ...models.search import ProductSearchRequest, ProductSearchResponse
from ...services.product_service import ProductService
from ...db.mongodb import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

async def get_product_service() -> ProductService:
    """Dependency to get product service instance"""
    db = await get_database()
    return ProductService(db)

@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    query: Optional[str] = Query(None, description="Search query for name, description, or brand"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    in_stock_only: bool = Query(False, description="Show only products in stock"),
    sort_by: str = Query("relevance", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Advanced product search with filtering and sorting
    
    - **query**: Search in product name, description, or brand
    - **category**: Filter by specific category
    - **min_price/max_price**: Price range filtering
    - **in_stock_only**: Show only available products
    - **sort_by**: Sort results (name_asc, name_desc, price_asc, price_desc, created_asc, created_desc, relevance)
    - **page**: Page number for pagination
    - **limit**: Number of items per page (max 100)
    """
    try:
        search_request = ProductSearchRequest(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
            sort_by=sort_by,
            page=page,
            limit=limit
        )
        
        result = await product_service.search_products(search_request)
        return result
        
    except Exception as e:
        logger.error(f"Error in product search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching products"
        )

@router.get("/", response_model=ProductSearchResponse)
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get products with optional category filtering and pagination
    (Backward compatibility with existing frontend)
    """
    try:
        search_request = ProductSearchRequest(
            category=category,
            page=page,
            limit=limit
        )
        
        result = await product_service.search_products(search_request)
        return result
        
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching products"
        )

@router.get("/categories", response_model=dict)
async def get_categories(
    product_service: ProductService = Depends(get_product_service)
):
    """Get all available product categories"""
    try:
        categories = await product_service.get_categories()
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching categories"
        )

@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    product_service: ProductService = Depends(get_product_service)
):
    """Get a single product by ID"""
    try:
        product = await product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the product"
        )

@router.post("/", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    current_user: UserResponse = Depends(require_role([UserRole.ADMIN])),
    product_service: ProductService = Depends(get_product_service)
):
    """Create a new product (Admin only)"""
    try:
        product = await product_service.create_product(product_data)
        return product
        
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the product"
        )

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_data: ProductCreate,
    current_user: UserResponse = Depends(require_role([UserRole.ADMIN])),
    product_service: ProductService = Depends(get_product_service)
):
    """Update an existing product (Admin only)"""
    try:
        product = await product_service.update_product(product_id, product_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the product"
        )

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: UserResponse = Depends(require_role([UserRole.ADMIN])),
    product_service: ProductService = Depends(get_product_service)
):
    """Delete a product (Admin only)"""
    try:
        success = await product_service.delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the product"
        )

@router.get("/filters/available", response_model=dict)
async def get_available_filters(
    product_service: ProductService = Depends(get_product_service)
):
    """Get available search filters for the frontend"""
    try:
        filters = await product_service._get_available_filters()
        return {"filters": filters.dict()}
        
    except Exception as e:
        logger.error(f"Error getting available filters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching available filters"
        )