from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.schemas import Restaurant, MenuItem, RestaurantResponse, MenuItemResponse
from app import crud

router = APIRouter(tags=["restaurants"])


@router.post("/restaurants", response_model=RestaurantResponse, status_code=201)
async def create_restaurant(restaurant: Restaurant, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new restaurant"""
    result = await crud.create_restaurant(db, restaurant)
    return result


@router.get("/restaurants", response_model=list[RestaurantResponse])
async def list_restaurants(db: AsyncIOMotorDatabase = Depends(get_database)):
    """List all restaurants"""
    restaurants = await crud.list_restaurants(db)
    return restaurants


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(restaurant_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get restaurant by ID"""
    restaurant = await crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItemResponse, status_code=201)
async def add_menu_item(restaurant_id: str, menu_item: MenuItem, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Add menu item to restaurant"""
    result = await crud.create_menu_item(db, restaurant_id, menu_item)
    if not result:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return result


@router.get("/restaurants/{restaurant_id}/menu-items", response_model=list[MenuItemResponse])
async def get_menu_items(restaurant_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all menu items for a restaurant"""
    items = await crud.get_menu_items(db, restaurant_id)
    return items


@router.put("/restaurants/{restaurant_id}/menu-items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(restaurant_id: str, item_id: str, menu_item: MenuItem, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Update a menu item"""
    result = await crud.update_menu_item(db, restaurant_id, item_id, menu_item)
    if not result:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return result


@router.delete("/restaurants/{restaurant_id}/menu-items/{item_id}")
async def delete_menu_item(restaurant_id: str, item_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete a menu item"""
    success = await crud.delete_menu_item(db, restaurant_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu item deleted"}
