#!/usr/bin/env python3
"""
Startup script for the new enterprise-level API
Run this instead of server.py to use the new modular structure
"""

import uvicorn
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("🚀 Starting Enterprise Delivery API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔗 ReDoc Documentation: http://localhost:8000/redoc")
    print("🏥 Health Check: http://localhost:8000/health")
    print()
    print("🔍 SEARCH FUNCTIONALITY:")
    print("   - GET /api/v1/products?search=coffee - Search products")
    print("   - GET /api/v1/products?category=drinks - Filter by category")
    print("   - GET /api/v1/products?search=milk&category=dairy - Combined search")
    print()
    print("🔐 AUTHENTICATION ENDPOINTS:")
    print("   - POST /api/v1/auth/register - User registration")
    print("   - POST /api/v1/auth/login - User login")
    print("   - GET /api/v1/auth/me - Get current user")
    print("   - PUT /api/v1/auth/profile - Update profile")
    print()
    print("📦 PRODUCT ENDPOINTS:")
    print("   - GET /api/v1/products - List/search products")
    print("   - GET /api/v1/products/{id} - Get product")
    print("   - POST /api/v1/products - Create product (Admin)")
    print("   - PUT /api/v1/products/{id} - Update product (Admin)")
    print("   - DELETE /api/v1/products/{id} - Delete product (Admin)")
    print("   - GET /api/v1/products/categories - Get categories")
    print()
    print("🛒 CART ENDPOINTS:")
    print("   - GET /api/v1/cart - Get user cart")
    print("   - POST /api/v1/cart/add - Add to cart")
    print("   - POST /api/v1/cart/update - Update cart item")
    print("   - POST /api/v1/cart/remove/{id} - Remove from cart")
    print("   - DELETE /api/v1/cart/clear - Clear cart")
    print()
    print("📋 ORDER ENDPOINTS:")
    print("   - GET /api/v1/orders - List orders (role-based)")
    print("   - POST /api/v1/orders - Create order")
    print("   - GET /api/v1/orders/{id} - Get order details")
    print("   - PUT /api/v1/orders/{id}/status - Update order status")
    print("   - POST /api/v1/orders/{id}/accept - Accept order (Agent)")
    print()
    print("🚚 DELIVERY ZONES:")
    print("   - GET /api/v1/delivery-zones - List zones")
    print("   - POST /api/v1/delivery-zones - Create zone (Admin)")
    print("   - PUT /api/v1/delivery-zones/{id}/assign-agent - Assign agent (Admin)")
    print()
    print("🗺️ ROUTING:")
    print("   - POST /api/v1/route/optimize - Optimize delivery route")
    print()
    print("👨‍💼 ADMIN:")
    print("   - GET /api/v1/admin/stats - Dashboard statistics")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )