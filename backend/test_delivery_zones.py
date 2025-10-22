import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(str(ROOT_DIR / '.env'))

async def test_delivery_zones_storage():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Successfully connected to MongoDB")
        
        # Check if delivery_zones collection exists
        collections = await db.list_collection_names()
        print(f"Available collections: {collections}")
        
        if 'delivery_zones' in collections:
            # Count documents in delivery_zones collection
            count = await db.delivery_zones.count_documents({})
            print(f"Number of delivery zones stored: {count}")
            
            # Show sample documents
            if count > 0:
                print("\nSample delivery zones:")
                cursor = db.delivery_zones.find().limit(3)
                async for zone in cursor:
                    print(f"- ID: {zone.get('id', 'N/A')}")
                    print(f"  Name: {zone.get('name', 'N/A')}")
                    print(f"  Coordinates count: {len(zone.get('coordinates', []))}")
                    print(f"  Assigned agents: {zone.get('assigned_agents', [])}")
                    print()
            else:
                print("No delivery zones found in the collection")
        else:
            print("delivery_zones collection does not exist")
            
        # Test creating a sample delivery zone
        print("Testing delivery zone creation...")
        sample_zone = {
            "id": "test-zone-001",
            "name": "Test Zone",
            "coordinates": [
                {"lat": 40.7128, "lng": -74.0060},
                {"lat": 40.7580, "lng": -73.9855},
                {"lat": 40.7614, "lng": -73.9776}
            ],
            "assigned_agents": [],
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        result = await db.delivery_zones.insert_one(sample_zone)
        print(f"✓ Created test zone with ID: {result.inserted_id}")
        
        # Retrieve and verify
        stored_zone = await db.delivery_zones.find_one({"id": "test-zone-001"})
        if stored_zone:
            print("✓ Successfully retrieved test zone")
            print(f"  Name: {stored_zone.get('name')}")
            print(f"  Coordinates: {stored_zone.get('coordinates')}")
        else:
            print("✗ Failed to retrieve test zone")
            
        # Clean up test zone
        await db.delivery_zones.delete_one({"id": "test-zone-001"})
        print("✓ Cleaned up test zone")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()
        print("Closed MongoDB connection")

if __name__ == "__main__":
    asyncio.run(test_delivery_zones_storage())