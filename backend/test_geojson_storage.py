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

# Sample GeoJSON data from the user
sample_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "coordinates": [
                    [
                        [
                            77.59514283308448,
                            13.105616358890572
                        ],
                        [
                            77.58487986886689,
                            13.099344219862346
                        ],
                        [
                            77.60072726983896,
                            13.089739905564429
                        ],
                        [
                            77.60938069609892,
                            13.104048417481849
                        ],
                        [
                            77.59514283308448,
                            13.105616358890572
                        ]
                    ]
                ],
                "type": "Polygon"
            }
        }
    ]
}

async def test_geojson_storage():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Successfully connected to MongoDB")
        
        # Extract the polygon coordinates from the GeoJSON
        polygon_coords = sample_geojson["features"][0]["geometry"]["coordinates"]
        
        # Create a delivery zone document with GeoJSON format
        delivery_zone = {
            "id": str(uuid.uuid4()),
            "name": "Test GeoJSON Zone",
            "geometry": {
                "type": "Polygon",
                "coordinates": polygon_coords
            },
            "assigned_agents": [],
            "created_at": datetime.utcnow()
        }
        
        # Insert the delivery zone into MongoDB
        result = await db.delivery_zones.insert_one(delivery_zone)
        print(f"✓ Created delivery zone with ID: {result.inserted_id}")
        
        # Retrieve and verify the stored data
        stored_zone = await db.delivery_zones.find_one({"id": delivery_zone["id"]})
        if stored_zone:
            print("✓ Successfully retrieved delivery zone")
            print(f"  Name: {stored_zone.get('name')}")
            print(f"  Geometry type: {stored_zone.get('geometry', {}).get('type')}")
            print(f"  Coordinates count: {len(stored_zone.get('geometry', {}).get('coordinates', [[]])[0])}")
            
            # Verify GeoJSON structure
            geometry = stored_zone.get('geometry', {})
            if geometry.get('type') == 'Polygon' and 'coordinates' in geometry:
                print("✓ GeoJSON structure is correct")
            else:
                print("✗ GeoJSON structure is incorrect")
        else:
            print("✗ Failed to retrieve delivery zone")
            
        # Clean up test zone
        await db.delivery_zones.delete_one({"id": delivery_zone["id"]})
        print("✓ Cleaned up test zone")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()
        print("Closed MongoDB connection")

if __name__ == "__main__":
    asyncio.run(test_geojson_storage())