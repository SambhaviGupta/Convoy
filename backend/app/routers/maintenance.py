from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


def _get_vehicle_or_404(db: Session, vehicle_id: int) -> models.Vehicle:
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.get("", response_model=List[schemas.MaintenanceOut])
def list_maintenance(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.MaintenanceLog).order_by(models.MaintenanceLog.id.desc()).all()


@router.post("", response_model=schemas.MaintenanceOut)
def create_maintenance(
    payload: schemas.MaintenanceCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    vehicle = _get_vehicle_or_404(db, payload.vehicle_id)

    log = models.MaintenanceLog(
        vehicle_id=payload.vehicle_id,
        description=payload.description,
        cost=payload.cost,
        date=payload.date or date.today(),
        is_active=True,
    )
    db.add(log)

    # Rule: creating an active maintenance record auto-flips vehicle to In Shop,
    # removing it from the dispatch/driver selection pool
    vehicle.status = models.VehicleStatus.IN_SHOP

    db.commit()
    db.refresh(log)
    return log


@router.post("/{maintenance_id}/close", response_model=schemas.MaintenanceOut)
def close_maintenance(
    maintenance_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == maintenance_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    if not log.is_active:
        raise HTTPException(status_code=400, detail="Maintenance record is already closed")

    log.is_active = False
    vehicle = _get_vehicle_or_404(db, log.vehicle_id)

    # Rule: closing maintenance restores the vehicle to Available, unless it's Retired
    if vehicle.status != models.VehicleStatus.RETIRED:
        # Only restore if no other active maintenance record still holds this vehicle In Shop
        other_active = (
            db.query(models.MaintenanceLog)
            .filter(
                models.MaintenanceLog.vehicle_id == vehicle.id,
                models.MaintenanceLog.is_active == True,  # noqa: E712
                models.MaintenanceLog.id != log.id,
            )
            .first()
        )
        if not other_active:
            vehicle.status = models.VehicleStatus.AVAILABLE

    db.commit()
    db.refresh(log)
    return log
