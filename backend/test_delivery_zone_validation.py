import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid
from datetime import datetime

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(str(ROOT_DIR / '.env'))

# Bangalore zone data from your GeoJSON
bangalore_zone_data = {
    "name": "Bangalore Zone",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [77.59514283308448, 13.105616358890572],
                [77.58487986886689, 13.099344219862346],
                [77.60072726983896, 13.089739905564429],
                [77.60938069609892, 13.104048417481849],
                [77.59514283308448, 13.105616358890572]
            ]
        ]
    }
}

async def test_delivery_zone_validation():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Successfully connected to MongoDB")
        
        # Clear any existing test data
        await db.delivery_zones.delete_many({})
        await db.orders.delete_many({})
        await db.users.delete_many({})
        await db.carts.delete_many({})
        await db.products.delete_many({})
        
        # Create a delivery zone
        delivery_zone = {
            "id": str(uuid.uuid4()),
            "name": bangalore_zone_data["name"],
            "geometry": bangalore_zone_data["geometry"],
            "assigned_agents": [],
            "created_at": datetime.utcnow()
        }
        
        result = await db.delivery_zones.insert_one(delivery_zone)
        print(f"✓ Created Bangalore delivery zone with ID: {result.inserted_id}")
        
        # Create a test user
        user = {
            "id": "test-user-001",
            "email": "test@example.com",
            "password": "hashed_password",
            "name": "Test User",
            "role": "customer",
            "phone": "1234567890",
            "address": "Test Address",
            "created_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user)
        print("✓ Created test user")
        
        # Create a test product
        product = {
            "id": "test-product-001",
            "name": "Test Product",
            "brand": "Test Brand",
            "description": "Test Description",
            "price": 10.0,
            "category": "Test Category",
            "stock": 100,
            "unit": "piece",
            "variant": "standard",
            "image": "base64_image_data",
            "created_at": datetime.utcnow()
        }
        
        await db.products.insert_one(product)
        print("✓ Created test product")
        
        # Create a test cart
        cart = {
            "id": "test-cart-001",
            "user_id": "test-user-001",
            "items": [
                {
                    "product_id": "test-product-001",
                    "quantity": 2
                }
            ],
            "updated_at": datetime.utcnow()
        }
        
        await db.carts.insert_one(cart)
        print("✓ Created test cart")
        
        # Test 1: Valid address within Bangalore zone
        print("\n--- Test 1: Valid address within Bangalore zone ---")
        valid_address = "123 Test Street, Bangalore lat,lng: 13.1000,77.5900"
        
        # Extract coordinates
        if "lat,lng:" in valid_address:
            coords_part = valid_address.split("lat,lng:")[1].strip()
            lat, lng = map(float, coords_part.split(","))
            print(f"Extracted coordinates: lat={lat}, lng={lng}")
            
            # Check if point is in zone
            point = {
                "type": "Point",
                "coordinates": [lng, lat]  # GeoJSON format [lng, lat]
            }
            
            zone = await db.delivery_zones.find_one({
                "geometry": {
                    "$geoIntersects": {
                        "$geometry": point
                    }
                }
            })
            
            if zone:
                print("✓ Address is within delivery zone")
            else:
                print("✗ Address is NOT within delivery zone")
        
        # Test 2: Invalid address outside Bangalore zone
        print("\n--- Test 2: Invalid address outside Bangalore zone ---")
        invalid_address = "123 Test Street, Outside lat,lng: 12.0000,77.0000"
        
        # Extract coordinates
        if "lat,lng:" in invalid_address:
            coords_part = invalid_address.split("lat,lng:")[1].strip()
            lat, lng = map(float, coords_part.split(","))
            print(f"Extracted coordinates: lat={lat}, lng={lng}")
            
            # Check if point is in zone
            point = {
                "type": "Point",
                "coordinates": [lng, lat]  # GeoJSON format [lng, lat]
            }
            
            zone = await db.delivery_zones.find_one({
                "geometry": {
                    "$geoIntersects": {
                        "$geometry": point
                    }
                }
            })
            
            if zone:
                print("✓ Address is within delivery zone")
            else:
                print("✗ Address is NOT within delivery zone")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up test data
        try:
            await db.delivery_zones.delete_many({})
            await db.orders.delete_many({})
            await db.users.delete_many({})
            await db.carts.delete_many({})
            await db.products.delete_many({})
            print("\n✓ Cleaned up test data")
        except:
            print("\n! Failed to clean up test data")
        
        client.close()
        print("Closed MongoDB connection")

if __name__ == "__main__":
    asyncio.run(test_delivery_zone_validation())