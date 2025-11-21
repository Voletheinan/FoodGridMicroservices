from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.schemas import Shipper, ShipperResponse, ShipperUpdate
from app import crud

router = APIRouter(prefix="/shippers", tags=["shippers"])


@router.post("", response_model=ShipperResponse, status_code=201)
async def create_shipper(shipper: Shipper, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new shipper"""
    result = await crud.create_shipper(db, shipper)
    return result


@router.get("/{shipper_id}", response_model=ShipperResponse)
async def get_shipper(shipper_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get shipper by ID"""
    shipper = await crud.get_shipper(db, shipper_id)
    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return shipper


@router.get("", response_model=list[ShipperResponse])
async def list_available_shippers(db: AsyncIOMotorDatabase = Depends(get_database)):
    """List available shippers"""
    shippers = await crud.list_available_shippers(db)
    return shippers


@router.put("/{shipper_id}/status", response_model=ShipperResponse)
async def update_shipper_status(shipper_id: str, update: ShipperUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Update shipper status"""
    result = await crud.update_shipper_status(db, shipper_id, update.status)
    if not result:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return result
