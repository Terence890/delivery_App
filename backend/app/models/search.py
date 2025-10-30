from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class SearchSort(str, Enum):
    """Available sorting options for search results"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"
    RELEVANCE = "relevance"

class ProductSearchRequest(BaseModel):
    """Request model for product search"""
    query: Optional[str] = Field(None, description="Search query for name, description, or brand")
    category: Optional[str] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    in_stock_only: Optional[bool] = Field(False, description="Show only products in stock")
    sort_by: Optional[SearchSort] = Field(SearchSort.RELEVANCE, description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")

class SearchFilters(BaseModel):
    """Available filters for search"""
    categories: List[str] = Field(default_factory=list)
    price_range: dict = Field(default_factory=dict)
    stock_available: bool = True

class ProductSearchResponse(BaseModel):
    """Response model for product search"""
    products: List[dict] = Field(default_factory=list)
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(20)
    total_pages: int = Field(0)
    filters: Optional[SearchFilters] = None
    search_time_ms: Optional[int] = None