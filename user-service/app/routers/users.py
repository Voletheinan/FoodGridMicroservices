from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.schemas import UserCreate, UserResponse, Address, AddressResponse
from app import crud

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new user"""
    result = await crud.create_user(db, user)
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get user by ID"""
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/addresses", response_model=AddressResponse)
async def add_address(user_id: str, address: Address, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Add address to user"""
    result = await crud.add_address(db, user_id, address)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("/{user_id}/addresses", response_model=list[AddressResponse])
async def get_user_addresses(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all addresses for user"""
    addresses = await crud.get_user_addresses(db, user_id)
    return addresses


@router.put("/{user_id}/addresses/{address_id}", response_model=AddressResponse)
async def update_address(user_id: str, address_id: str, address: Address, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Update user address"""
    result = await crud.update_address(db, user_id, address_id, address)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return result


@router.delete("/{user_id}/addresses/{address_id}")
async def delete_address(user_id: str, address_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete user address"""
    success = await crud.delete_address(db, user_id, address_id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted"}
