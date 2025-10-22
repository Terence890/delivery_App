import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(str(ROOT_DIR / '.env'))

async def create_geospatial_index():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Successfully connected to MongoDB")
        
        # Create a 2dsphere index on the geometry field for geospatial queries
        result = await db.delivery_zones.create_index([("geometry", "2dsphere")])
        print(f"✓ Created 2dsphere index: {result}")
        
        # List all indexes to verify
        indexes = await db.delivery_zones.index_information()
        print("Current indexes:")
        for name, info in indexes.items():
            print(f"  {name}: {info}")
        
        # Also create indexes for other collections
        await db.orders.create_index([("delivery_location", "2dsphere")])
        print("✓ Created 2dsphere index for orders.delivery_location")
        
        await db.orders.create_index([("user_id", 1)])
        print("✓ Created index for orders.user_id")
        
        await db.users.create_index([("role", 1)])
        print("✓ Created index for users.role")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()
        print("Closed MongoDB connection")

if __name__ == "__main__":
    asyncio.run(create_geospatial_index())