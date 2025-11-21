from pydantic import BaseModel
from typing import Optional, List


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class AddressResponse(BaseModel):
    id: str
    street: str
    city: str
    state: str
    zip_code: str
    country: str

    class Config:
        populate_by_name = True


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    addresses: List[AddressResponse] = []

    class Config:
        populate_by_name = True
