import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MONGO_URL = os.getenv("MONGO_URL", "mongodb://root:password@mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "user_db")

client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo(retries: int = 5, delay: float = 1.0):
    global client, db
    for attempt in range(1, retries + 1):
        try:
            client = AsyncIOMotorClient(MONGO_URL)
            await client.admin.command('ping')
            db = client[MONGO_DB]
            print(f"Connected to MongoDB: {MONGO_DB}")
            return
        except Exception as e:
            print(f"MongoDB connection failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
    raise Exception("Could not connect to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    return db
