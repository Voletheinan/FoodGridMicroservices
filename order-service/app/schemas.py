from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int


class OrderCreate(BaseModel):
    user_id: str
    restaurant_id: str
    items: List[OrderItem]


class OrderStatusUpdate(BaseModel):
    status: str  # cart, confirmed, preparing, ready, shipped, delivered


class ShipperAssign(BaseModel):
    shipper_id: str


class OrderResponse(BaseModel):
    id: str
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    status: str
    shipper_id: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True
