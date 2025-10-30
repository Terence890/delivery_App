# Enterprise-Level Backend Architecture

## 🏗️ Architecture Overview

This backend has been restructured into an enterprise-level architecture with proper separation of concerns:

```
backend/
├── app/                          # Application package
│   ├── api/                      # API layer
│   │   └── v1/                   # API version 1
│   │       ├── products.py       # Product endpoints
│   │       └── router.py         # Main API router
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Configuration settings
│   │   └── security.py           # Authentication & security
│   ├── db/                       # Database layer
│   │   └── mongodb.py            # MongoDB connection
│   ├── models/                   # Data models
│   │   ├── product.py            # Product models
│   │   ├── search.py             # Search models
│   │   └── user.py               # User models
│   └── services/                 # Business logic layer
│       └── product_service.py    # Product service
├── main.py                       # New enterprise FastAPI app
├── server.py                     # Legacy monolithic app
└── start_new_api.py              # Startup script
```

## 🚀 Quick Start

### Start the New Enterprise API

```bash
# Option 1: Using the startup script
python start_new_api.py

# Option 2: Direct uvicorn command
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Test the Search Functionality

The new API includes advanced search capabilities:

```bash
# Basic search
curl "http://localhost:8000/api/v1/products/search?query=coffee"

# Search with filters
curl "http://localhost:8000/api/v1/products/search?query=milk&category=dairy&min_price=10&max_price=50&in_stock_only=true"

# Get all products (backward compatibility)
curl "http://localhost:8000/api/v1/products"

# Get categories
curl "http://localhost:8000/api/v1/products/categories"
```

## 🔍 Search Features

### Advanced Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search in name, description, brand |
| `category` | string | Filter by category |
| `min_price` | float | Minimum price filter |
| `max_price` | float | Maximum price filter |
| `in_stock_only` | boolean | Show only available products |
| `sort_by` | string | Sort order (name_asc, price_desc, etc.) |
| `page` | integer | Page number |
| `limit` | integer | Items per page (max 100) |

### Search Response Format

```json
{
  "products": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "total_pages": 8,
  "search_time_ms": 45,
  "filters": {
    "categories": ["drinks", "snacks", "dairy"],
    "price_range": {"min": 5.0, "max": 299.99}
  }
}
```

## 🏭 Enterprise Features

### 1. Modular Architecture
- **Separation of Concerns**: API, Services, Models, Database
- **Dependency Injection**: Clean service dependencies
- **Version Control**: API versioning support

### 2. Advanced Search
- **Multi-field Search**: Name, description, brand, category
- **Filtering**: Price range, category, stock availability
- **Sorting**: Multiple sort options
- **Pagination**: Efficient result pagination
- **Performance**: Search timing and optimization

### 3. Error Handling
- **Structured Errors**: Consistent error responses
- **Logging**: Comprehensive request/error logging
- **Validation**: Input validation with Pydantic

### 4. Security
- **JWT Authentication**: Secure token-based auth
- **Role-based Access**: Admin-only endpoints
- **Input Sanitization**: Protected against injection

## 📊 Performance Optimizations

### Database Indexing
```javascript
// Recommended MongoDB indexes
db.products.createIndex({ name: "text", description: "text", brand: "text" })
db.products.createIndex({ category: 1 })
db.products.createIndex({ price: 1 })
db.products.createIndex({ stock: 1 })
db.products.createIndex({ created_at: -1 })
```

### Search Optimizations
- **Regex Search**: Case-insensitive pattern matching
- **Compound Queries**: Efficient multi-field searches
- **Pagination**: Limit memory usage for large datasets
- **Response Caching**: Future enhancement for static data

## 🔧 Configuration

### Environment Variables
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=delivery_app_db
JWT_SECRET=your-secret-key
ALGORITHM=HS256
```

### Settings
The `app/core/config.py` file manages all configuration with environment variable support.

## 🧪 Testing

### API Testing
```bash
# Test search functionality
python -m pytest tests/test_search.py

# Test product service
python -m pytest tests/test_product_service.py
```

### Manual Testing
Visit `http://localhost:8000/docs` for interactive API documentation and testing.

## 📈 Migration from Legacy

### Backward Compatibility
The new API maintains backward compatibility with existing endpoints:

- `/products` → `/api/v1/products`
- `/categories` → `/api/v1/products/categories`

### Frontend Integration
Update your frontend API calls to use the new endpoints:

```javascript
// Old way
const response = await apiClient.get('/products', { params: { category: 'drinks' } });

// New way with search
const response = await apiClient.get('/api/v1/products/search', { 
  params: { query: 'coffee', category: 'drinks' } 
});
```

## 🚀 Next Steps

1. **Add More Services**: Cart, Order, User services
2. **Implement Caching**: Redis for search results
3. **Add Analytics**: Search analytics and logging
4. **API Rate Limiting**: Prevent abuse
5. **Full-Text Search**: Elasticsearch integration
6. **GraphQL API**: Alternative to REST

## 📝 API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`