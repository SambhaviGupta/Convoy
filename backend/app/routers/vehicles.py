from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=List[schemas.VehicleOut])
def list_vehicles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Vehicle).all()


@router.get("/available", response_model=List[schemas.VehicleOut])
def list_available_vehicles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(models.Vehicle)
        .filter(models.Vehicle.status == models.VehicleStatus.AVAILABLE)
        .all()
    )


@router.post("", response_model=schemas.VehicleOut)
def create_vehicle(
    payload: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    existing = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.registration_number == payload.registration_number)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Registration number already exists")

    vehicle = models.Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.put("/{vehicle_id}", response_model=schemas.VehicleOut)
def update_vehicle(
    vehicle_id: int,
    payload: schemas.VehicleUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle
