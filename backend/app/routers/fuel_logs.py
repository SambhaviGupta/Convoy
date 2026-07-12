from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/fuel-logs", tags=["fuel-logs"])


@router.get("", response_model=List[schemas.FuelLogOut])
def list_fuel_logs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.FuelLog).order_by(models.FuelLog.id.desc()).all()


@router.post("", response_model=schemas.FuelLogOut)
def create_fuel_log(
    payload: schemas.FuelLogCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == payload.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    log = models.FuelLog(
        vehicle_id=payload.vehicle_id,
        liters=payload.liters,
        cost=payload.cost,
        date=payload.date or date.today(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
