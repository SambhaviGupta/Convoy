from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=List[schemas.DriverOut])
def list_drivers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Driver).all()


@router.get("/available", response_model=List[schemas.DriverOut])
def list_available_drivers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(models.Driver)
        .filter(
            models.Driver.status == models.DriverStatus.AVAILABLE,
            models.Driver.license_expiry_date >= date.today(),
        )
        .all()
    )


@router.post("", response_model=schemas.DriverOut)
def create_driver(
    payload: schemas.DriverCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    existing = (
        db.query(models.Driver)
        .filter(models.Driver.license_number == payload.license_number)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="License number already exists")

    driver = models.Driver(**payload.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put("/{driver_id}", response_model=schemas.DriverOut)
def update_driver(
    driver_id: int,
    payload: schemas.DriverUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver
