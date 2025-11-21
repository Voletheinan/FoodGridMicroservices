from pydantic import BaseModel
from typing import Optional


class Shipper(BaseModel):
    name: str
    phone: str
    vehicle: str
    status: str = "available"  # available, busy, offline


class ShipperResponse(BaseModel):
    id: str
    name: str
    phone: str
    vehicle: str
    status: str

    class Config:
        populate_by_name = True


class ShipperUpdate(BaseModel):
    status: str  # available, busy, offline
