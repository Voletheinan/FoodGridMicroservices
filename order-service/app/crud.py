from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas import OrderCreate
from datetime import datetime
import httpx
import os


async def fetch_restaurant_name(restaurant_id: str) -> str:
    """Fetch restaurant name from restaurant service"""
    try:
        restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8000")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{restaurant_service_url}/restaurants/{restaurant_id}", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("name", "Unknown")
    except:
        pass
    return "Unknown"


async def fetch_shipper_name(shipper_id: str) -> str:
    """Fetch shipper name from shipper service"""
    try:
        shipper_service_url = os.getenv("SHIPPER_SERVICE_URL", "http://shipper-service:8000")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{shipper_service_url}/shippers/{shipper_id}", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("name", "Unknown")
    except:
        pass
    return "Unknown"


async def fetch_user_name(user_id: str) -> str:
    """Fetch user name from user service"""
    try:
        user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{user_service_url}/users/{user_id}", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("username", "Unknown")
    except:
        pass
    return "Unknown"


async def fetch_menu_item_details(restaurant_id: str, item_id: str) -> dict:
    """Fetch menu item details from restaurant service"""
    try:
        restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8000")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{restaurant_service_url}/restaurants/{restaurant_id}/menu-items", timeout=5.0)
            if resp.status_code == 200:
                items = resp.json()
                for item in items:
                    if item.get("id") == item_id:
                        return {"name": item.get("name", "Unknown"), "price": item.get("price", 0)}
    except:
        pass
    return {"name": "Unknown", "price": 0}


async def create_order(db: AsyncIOMotorDatabase, order_data: OrderCreate):
    """Create a new order (cart status)"""
    orders_collection = db["orders"]
    order_dict = order_data.model_dump()
    order_dict["status"] = "cart"
    order_dict["created_at"] = datetime.now().isoformat()
    result = await orders_collection.insert_one(order_dict)
    
    # Fetch names
    user_name = await fetch_user_name(order_dict["user_id"])
    restaurant_name = await fetch_restaurant_name(order_dict["restaurant_id"])
    
    # Build items with details
    items_with_details = []
    for item in order_dict["items"]:
        menu_details = await fetch_menu_item_details(order_dict["restaurant_id"], item["menu_item_id"])
        items_with_details.append({
            "menu_item_id": item["menu_item_id"],
            "item_name": menu_details["name"],
            "price": menu_details["price"],
            "quantity": item["quantity"]
        })
    
    return {
        "id": str(result.inserted_id),
        "user_id": order_dict["user_id"],
        "user_name": user_name,
        "restaurant_id": order_dict["restaurant_id"],
        "restaurant_name": restaurant_name,
        "items": items_with_details,
        "status": order_dict["status"],
        "shipper_id": None,
        "shipper_name": None,
        "created_at": order_dict["created_at"],
    }


async def get_order(db: AsyncIOMotorDatabase, order_id: str):
    """Retrieve an order by ID"""
    orders_collection = db["orders"]
    try:
        order = await orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            # Fetch names
            user_name = await fetch_user_name(order["user_id"])
            restaurant_name = await fetch_restaurant_name(order["restaurant_id"])
            
            # Fetch shipper name if exists
            shipper_name = None
            if order.get("shipper_id"):
                shipper_name = await fetch_shipper_name(order["shipper_id"])
            
            # Build items with details
            items_with_details = []
            for item in order["items"]:
                menu_details = await fetch_menu_item_details(order["restaurant_id"], item["menu_item_id"])
                items_with_details.append({
                    "menu_item_id": item["menu_item_id"],
                    "item_name": menu_details["name"],
                    "price": menu_details["price"],
                    "quantity": item["quantity"]
                })
            
            return {
                "id": str(order["_id"]),
                "user_id": order["user_id"],
                "user_name": user_name,
                "restaurant_id": order["restaurant_id"],
                "restaurant_name": restaurant_name,
                "items": items_with_details,
                "status": order["status"],
                "shipper_id": order.get("shipper_id"),
                "shipper_name": shipper_name,
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
    """Assign shipper to order and update shipper status to busy"""
    orders_collection = db["orders"]
    try:
        # Update shipper status to busy in shipper service
        try:
            shipper_service_url = os.getenv("SHIPPER_SERVICE_URL", "http://shipper-service:8000")
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{shipper_service_url}/shippers/{shipper_id}/status",
                    json={"status": "busy"},
                    timeout=5.0
                )
        except:
            pass  # Continue even if shipper service call fails
        
        # Update order with shipper
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
        # Fetch names
        user_name = await fetch_user_name(order["user_id"])
        restaurant_name = await fetch_restaurant_name(order["restaurant_id"])
        
        # Fetch shipper name if exists
        shipper_name = None
        if order.get("shipper_id"):
            shipper_name = await fetch_shipper_name(order["shipper_id"])
        
        # Build items with details
        items_with_details = []
        for item in order["items"]:
            menu_details = await fetch_menu_item_details(order["restaurant_id"], item["menu_item_id"])
            items_with_details.append({
                "menu_item_id": item["menu_item_id"],
                "item_name": menu_details["name"],
                "price": menu_details["price"],
                "quantity": item["quantity"]
            })
        
        result.append({
            "id": str(order["_id"]),
            "user_id": order["user_id"],
            "user_name": user_name,
            "restaurant_id": order["restaurant_id"],
            "restaurant_name": restaurant_name,
            "items": items_with_details,
            "status": order["status"],
            "shipper_id": order.get("shipper_id"),
            "shipper_name": shipper_name,
            "created_at": order.get("created_at"),
        })
    return result


async def get_restaurant_orders(db: AsyncIOMotorDatabase, restaurant_id: str):
    """Get all orders for a restaurant"""
    orders_collection = db["orders"]
    cursor = orders_collection.find({"restaurant_id": restaurant_id})
    result = []
    async for order in cursor:
        # Fetch names
        user_name = await fetch_user_name(order["user_id"])
        restaurant_name = await fetch_restaurant_name(order["restaurant_id"])
        
        # Fetch shipper name if exists
        shipper_name = None
        if order.get("shipper_id"):
            shipper_name = await fetch_shipper_name(order["shipper_id"])
        
        # Build items with details
        items_with_details = []
        for item in order["items"]:
            menu_details = await fetch_menu_item_details(order["restaurant_id"], item["menu_item_id"])
            items_with_details.append({
                "menu_item_id": item["menu_item_id"],
                "item_name": menu_details["name"],
                "price": menu_details["price"],
                "quantity": item["quantity"]
            })
        
        result.append({
            "id": str(order["_id"]),
            "user_id": order["user_id"],
            "user_name": user_name,
            "restaurant_id": order["restaurant_id"],
            "restaurant_name": restaurant_name,
            "items": items_with_details,
            "status": order["status"],
            "shipper_id": order.get("shipper_id"),
            "shipper_name": shipper_name,
            "created_at": order.get("created_at"),
        })
    return result
