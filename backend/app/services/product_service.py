import time
import logging
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.product import Product, ProductCreate, PaginatedProductsResponse
from ..models.search import ProductSearchRequest, ProductSearchResponse, SearchSort, SearchFilters

logger = logging.getLogger(__name__)

class ProductService:
    """Enterprise-level product service with advanced search capabilities"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.products
    
    async def search_products(self, search_request: ProductSearchRequest) -> ProductSearchResponse:
        """
        Advanced product search with multiple filters and sorting options
        
        Args:
            search_request: Search parameters and filters
            
        Returns:
            ProductSearchResponse with results and metadata
        """
        start_time = time.time()
        
        try:
            # Build MongoDB query
            query = await self._build_search_query(search_request)
            
            # Calculate pagination
            skip = (search_request.page - 1) * search_request.limit
            
            # Get total count for pagination
            total_count = await self.collection.count_documents(query)
            
            # Build sort criteria
            sort_criteria = self._build_sort_criteria(search_request.sort_by)
            
            # Execute search with pagination and sorting
            cursor = self.collection.find(query).sort(sort_criteria).skip(skip).limit(search_request.limit)
            products = await cursor.to_list(length=search_request.limit)
            
            # Convert to Product objects
            product_list = [Product(**product).dict() for product in products]
            
            # Calculate total pages
            total_pages = (total_count + search_request.limit - 1) // search_request.limit
            
            # Get available filters (for frontend filter suggestions)
            filters = await self._get_available_filters() if search_request.query else None
            
            # Calculate search time
            search_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Product search completed: query='{search_request.query}', "
                       f"results={len(product_list)}, time={search_time_ms}ms")
            
            return ProductSearchResponse(
                products=product_list,
                total=total_count,
                page=search_request.page,
                limit=search_request.limit,
                total_pages=total_pages,
                filters=filters,
                search_time_ms=search_time_ms
            )
            
        except Exception as e:
            logger.error(f"Error in product search: {str(e)}")
            raise
    
    async def _build_search_query(self, search_request: ProductSearchRequest) -> Dict[str, Any]:
        """Build MongoDB query from search parameters"""
        query = {}
        
        # Text search across multiple fields
        if search_request.query:
            search_regex = {"$regex": search_request.query, "$options": "i"}
            query["$or"] = [
                {"name": search_regex},
                {"description": search_regex},
                {"brand": search_regex},
                {"category": search_regex}
            ]
        
        # Category filter
        if search_request.category:
            query["category"] = search_request.category
        
        # Price range filter
        if search_request.min_price is not None or search_request.max_price is not None:
            price_filter = {}
            if search_request.min_price is not None:
                price_filter["$gte"] = search_request.min_price
            if search_request.max_price is not None:
                price_filter["$lte"] = search_request.max_price
            query["price"] = price_filter
        
        # Stock filter
        if search_request.in_stock_only:
            query["stock"] = {"$gt": 0}
        
        return query
    
    def _build_sort_criteria(self, sort_by: SearchSort) -> List[tuple]:
        """Build MongoDB sort criteria from sort option"""
        sort_map = {
            SearchSort.NAME_ASC: [("name", 1)],
            SearchSort.NAME_DESC: [("name", -1)],
            SearchSort.PRICE_ASC: [("price", 1)],
            SearchSort.PRICE_DESC: [("price", -1)],
            SearchSort.CREATED_ASC: [("created_at", 1)],
            SearchSort.CREATED_DESC: [("created_at", -1)],
            SearchSort.RELEVANCE: [("created_at", -1)]  # Default to newest first
        }
        return sort_map.get(sort_by, [("created_at", -1)])
    
    async def _get_available_filters(self) -> SearchFilters:
        """Get available filter options for the frontend"""
        try:
            # Get all unique categories
            categories = await self.collection.distinct("category")
            
            # Get price range
            price_pipeline = [
                {"$group": {
                    "_id": None,
                    "min_price": {"$min": "$price"},
                    "max_price": {"$max": "$price"}
                }}
            ]
            price_result = await self.collection.aggregate(price_pipeline).to_list(1)
            price_range = {}
            if price_result:
                price_range = {
                    "min": price_result[0]["min_price"],
                    "max": price_result[0]["max_price"]
                }
            
            return SearchFilters(
                categories=sorted(categories),
                price_range=price_range,
                stock_available=True
            )
        except Exception as e:
            logger.error(f"Error getting available filters: {str(e)}")
            return SearchFilters()
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a single product by ID"""
        try:
            product = await self.collection.find_one({"id": product_id})
            return Product(**product) if product else None
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            return None
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        try:
            product = Product(**product_data.dict())
            await self.collection.insert_one(product.dict())
            logger.info(f"Product created: {product.id}")
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise
    
    async def update_product(self, product_id: str, product_data: ProductCreate) -> Optional[Product]:
        """Update an existing product"""
        try:
            result = await self.collection.update_one(
                {"id": product_id}, 
                {"$set": product_data.dict()}
            )
            if result.matched_count == 0:
                return None
            
            updated_product = await self.collection.find_one({"id": product_id})
            logger.info(f"Product updated: {product_id}")
            return Product(**updated_product)
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise
    
    async def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        try:
            result = await self.collection.delete_one({"id": product_id})
            success = result.deleted_count > 0
            if success:
                logger.info(f"Product deleted: {product_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise
    
    async def get_categories(self) -> List[str]:
        """Get all available product categories"""
        try:
            categories = await self.collection.distinct("category")
            return sorted(categories)
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []