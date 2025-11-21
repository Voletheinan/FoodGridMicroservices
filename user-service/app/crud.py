from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas import UserCreate, Address


async def create_user(db: AsyncIOMotorDatabase, user_data: UserCreate):
    """Create a new user in the database"""
    users_collection = db["users"]
    user_dict = user_data.model_dump()
    user_dict["addresses"] = []
    result = await users_collection.insert_one(user_dict)
    return {
        "id": str(result.inserted_id),
        "username": user_dict["username"],
        "email": user_dict["email"],
        "addresses": [],
    }


async def get_user(db: AsyncIOMotorDatabase, user_id: str):
    """Retrieve a user by ID"""
    users_collection = db["users"]
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "addresses": user.get("addresses", []),
            }
        return None
    except Exception:
        return None


async def add_address(db: AsyncIOMotorDatabase, user_id: str, address_data: Address):
    """Add address to user"""
    users_collection = db["users"]
    try:
        address_id = str(ObjectId())
        address_dict = address_data.model_dump()
        address_dict["id"] = address_id
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"addresses": address_dict}}
        )
        return address_dict
    except Exception:
        return None


async def get_user_addresses(db: AsyncIOMotorDatabase, user_id: str):
    """Get all addresses for a user"""
    users_collection = db["users"]
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return user.get("addresses", [])
        return []
    except Exception:
        return []


async def update_address(db: AsyncIOMotorDatabase, user_id: str, address_id: str, address_data: Address):
    """Update user address"""
    users_collection = db["users"]
    try:
        address_dict = address_data.model_dump()
        address_dict["id"] = address_id
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id), "addresses.id": address_id},
            {"$set": {"addresses.$": address_dict}}
        )
        return address_dict
    except Exception:
        return None


async def delete_address(db: AsyncIOMotorDatabase, user_id: str, address_id: str):
    """Delete user address"""
    users_collection = db["users"]
    try:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"addresses": {"id": address_id}}}
        )
        return True
    except Exception:
        return False
