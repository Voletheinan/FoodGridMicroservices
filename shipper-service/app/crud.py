from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas import Shipper, ShipperUpdate


async def create_shipper(db: AsyncIOMotorDatabase, shipper_data: Shipper):
    """Create a new shipper"""
    shippers = db["shippers"]
    shipper_dict = shipper_data.model_dump()
    result = await shippers.insert_one(shipper_dict)
    return {
        "id": str(result.inserted_id),
        **shipper_dict,
    }


async def get_shipper(db: AsyncIOMotorDatabase, shipper_id: str):
    """Get shipper by ID"""
    shippers = db["shippers"]
    try:
        shipper = await shippers.find_one({"_id": ObjectId(shipper_id)})
        if shipper:
            return {
                "id": str(shipper["_id"]),
                "name": shipper["name"],
                "phone": shipper["phone"],
                "vehicle": shipper["vehicle"],
                "status": shipper["status"],
            }
        return None
    except Exception:
        return None


async def list_available_shippers(db: AsyncIOMotorDatabase):
    """List all available shippers"""
    shippers = db["shippers"]
    cursor = shippers.find({"status": "available"})
    result = []
    async for shipper in cursor:
        result.append({
            "id": str(shipper["_id"]),
            "name": shipper["name"],
            "phone": shipper["phone"],
            "vehicle": shipper["vehicle"],
            "status": shipper["status"],
        })
    return result


async def update_shipper_status(db: AsyncIOMotorDatabase, shipper_id: str, status: str):
    """Update shipper status"""
    shippers = db["shippers"]
    try:
        await shippers.update_one(
            {"_id": ObjectId(shipper_id)},
            {"$set": {"status": status}}
        )
        return await get_shipper(db, shipper_id)
    except Exception:
        return None
