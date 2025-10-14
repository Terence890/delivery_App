from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings

class MongoDB: 
    client: AsyncIOMotorClient = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URL)
    try:
        await mongodb.client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except ConnectionFailure:
        print("MongoDB connection failed.")

async def close_mongo_connection():
    mongodb.client.close()

async def get_database():
    return mongodb.client[settings.DB_NAME]
