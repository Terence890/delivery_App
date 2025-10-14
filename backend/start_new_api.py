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
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 New search endpoints:")
    print("   - GET /api/v1/products/search - Advanced search with filters")
    print("   - GET /api/v1/products - Basic product listing")
    print("   - GET /api/v1/products/categories - Get categories")
    print("   - GET /api/v1/products/filters/available - Get available filters")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )