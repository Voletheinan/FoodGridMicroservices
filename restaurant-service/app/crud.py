from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas import Restaurant, MenuItem


async def create_restaurant(db: AsyncIOMotorDatabase, restaurant_data: Restaurant):
    """Create a new restaurant"""
    restaurants = db["restaurants"]
    restaurant_dict = restaurant_data.model_dump()
    restaurant_dict["menu_items"] = []
    result = await restaurants.insert_one(restaurant_dict)
    return {
        "id": str(result.inserted_id),
        **restaurant_dict,
    }


async def get_restaurant(db: AsyncIOMotorDatabase, restaurant_id: str):
    """Get restaurant by ID"""
    restaurants = db["restaurants"]
    try:
        restaurant = await restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if restaurant:
            return {
                "id": str(restaurant["_id"]),
                "name": restaurant["name"],
                "description": restaurant["description"],
                "address": restaurant["address"],
                "phone": restaurant["phone"],
                "menu_items": restaurant.get("menu_items", []),
            }
        return None
    except Exception:
        return None


async def list_restaurants(db: AsyncIOMotorDatabase):
    """List all restaurants"""
    restaurants = db["restaurants"]
    cursor = restaurants.find({})
    result = []
    async for restaurant in cursor:
        result.append({
            "id": str(restaurant["_id"]),
            "name": restaurant["name"],
            "description": restaurant["description"],
            "address": restaurant["address"],
            "phone": restaurant["phone"],
            "menu_items": restaurant.get("menu_items", []),
        })
    return result


async def create_menu_item(db: AsyncIOMotorDatabase, restaurant_id: str, menu_item: MenuItem):
    """Add menu item to restaurant"""
    restaurants = db["restaurants"]
    try:
        item_id = str(ObjectId())
        menu_item_dict = menu_item.model_dump()
        menu_item_dict["id"] = item_id
        
        await restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$push": {"menu_items": menu_item_dict}}
        )
        return menu_item_dict
    except Exception as e:
        return None


async def get_menu_items(db: AsyncIOMotorDatabase, restaurant_id: str):
    """Get all menu items for a restaurant"""
    restaurants = db["restaurants"]
    try:
        restaurant = await restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if restaurant:
            return restaurant.get("menu_items", [])
        return []
    except Exception:
        return []


async def update_menu_item(db: AsyncIOMotorDatabase, restaurant_id: str, item_id: str, menu_item: MenuItem):
    """Update a menu item"""
    restaurants = db["restaurants"]
    try:
        menu_item_dict = menu_item.model_dump()
        menu_item_dict["id"] = item_id
        
        await restaurants.update_one(
            {"_id": ObjectId(restaurant_id), "menu_items.id": item_id},
            {"$set": {"menu_items.$": menu_item_dict}}
        )
        return menu_item_dict
    except Exception:
        return None


async def delete_menu_item(db: AsyncIOMotorDatabase, restaurant_id: str, item_id: str):
    """Delete a menu item"""
    restaurants = db["restaurants"]
    try:
        await restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$pull": {"menu_items": {"id": item_id}}}
        )
        return True
    except Exception:
        return False
