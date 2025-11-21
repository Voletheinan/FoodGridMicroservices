from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas import OrderCreate
from datetime import datetime


async def create_order(db: AsyncIOMotorDatabase, order_data: OrderCreate):
    """Create a new order (cart status)"""
    orders_collection = db["orders"]
    order_dict = order_data.model_dump()
    order_dict["status"] = "cart"
    order_dict["created_at"] = datetime.now().isoformat()
    result = await orders_collection.insert_one(order_dict)
    return {
        "id": str(result.inserted_id),
        "user_id": order_dict["user_id"],
        "restaurant_id": order_dict["restaurant_id"],
        "items": order_dict["items"],
        "status": order_dict["status"],
        "shipper_id": None,
        "created_at": order_dict["created_at"],
    }


async def get_order(db: AsyncIOMotorDatabase, order_id: str):
    """Retrieve an order by ID"""
    orders_collection = db["orders"]
    try:
        order = await orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            return {
                "id": str(order["_id"]),
                "user_id": order["user_id"],
                "restaurant_id": order["restaurant_id"],
                "items": order["items"],
                "status": order["status"],
                "shipper_id": order.get("shipper_id"),
                "created_at": order.get("created_at"),
            }
        return None
    except Exception:
        return None


async def update_order_status(db: AsyncIOMotorDatabase, order_id: str, status: str):
    """Update order status"""
    orders_collection = db["orders"]
    try:
        await orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status}}
        )
        return await get_order(db, order_id)
    except Exception:
        return None


async def assign_shipper(db: AsyncIOMotorDatabase, order_id: str, shipper_id: str):
    """Assign shipper to order"""
    orders_collection = db["orders"]
    try:
        await orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"shipper_id": shipper_id, "status": "shipped"}}
        )
        return await get_order(db, order_id)
    except Exception:
        return None


async def get_user_orders(db: AsyncIOMotorDatabase, user_id: str):
    """Get all orders for a user"""
    orders_collection = db["orders"]
    cursor = orders_collection.find({"user_id": user_id})
    result = []
    async for order in cursor:
        result.append({
            "id": str(order["_id"]),
            "user_id": order["user_id"],
            "restaurant_id": order["restaurant_id"],
            "items": order["items"],
            "status": order["status"],
            "shipper_id": order.get("shipper_id"),
            "created_at": order.get("created_at"),
        })
    return result


async def get_restaurant_orders(db: AsyncIOMotorDatabase, restaurant_id: str):
    """Get all orders for a restaurant"""
    orders_collection = db["orders"]
    cursor = orders_collection.find({"restaurant_id": restaurant_id})
    result = []
    async for order in cursor:
        result.append({
            "id": str(order["_id"]),
            "user_id": order["user_id"],
            "restaurant_id": order["restaurant_id"],
            "items": order["items"],
            "status": order["status"],
            "shipper_id": order.get("shipper_id"),
            "created_at": order.get("created_at"),
        })
    return result
