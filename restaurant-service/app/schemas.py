from pydantic import BaseModel
from typing import List, Optional


class MenuItem(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    available: bool = True


class Restaurant(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    address: str
    phone: str
    menu_items: List[MenuItem] = []


class RestaurantResponse(BaseModel):
    id: str
    name: str
    description: str
    address: str
    phone: str
    menu_items: List[MenuItem]

    class Config:
        populate_by_name = True


class MenuItemResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    available: bool

    class Config:
        populate_by_name = True
