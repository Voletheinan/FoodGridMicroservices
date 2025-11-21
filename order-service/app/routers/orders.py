from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate, ShipperAssign
from app import crud
import httpx
import os

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new order (US 2 - Add to cart)

    Validate that referenced user and restaurant exist by calling their services.
    """
    user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
    restaurant_service_url = os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8000")

    async with httpx.AsyncClient() as client:
        # Validate user
        try:
            uresp = await client.get(f"{user_service_url}/users/{order.user_id}", timeout=5.0)
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Cannot reach user service")
        if uresp.status_code == 404:
            raise HTTPException(status_code=400, detail="User not found")

        # Validate restaurant
        try:
            rresp = await client.get(f"{restaurant_service_url}/restaurants/{order.restaurant_id}", timeout=5.0)
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Cannot reach restaurant service")
        if rresp.status_code == 404:
            raise HTTPException(status_code=400, detail="Restaurant not found")

    result = await crud.create_order(db, order)
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get order by ID (US 4 - Track order)"""
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: str, update: OrderStatusUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Update order status (US 3 - Place order, US 6 - Confirm order)"""
    result = await crud.update_order_status(db, order_id, update.status)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.put("/{order_id}/shipper", response_model=OrderResponse)
async def assign_shipper(order_id: str, assign: ShipperAssign, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Assign shipper to order (US 7 - Shipper accept order)"""
    result = await crud.assign_shipper(db, order_id, assign.shipper_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.get("/users/{user_id}/orders")
async def get_user_orders(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all orders for a user (US 4 - Track orders)"""
    orders = await crud.get_user_orders(db, user_id)
    return orders


@router.get("/restaurants/{restaurant_id}/orders")
async def get_restaurant_orders(restaurant_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all orders for a restaurant (US 6 - Manage orders)"""
    orders = await crud.get_restaurant_orders(db, restaurant_id)
    return orders
