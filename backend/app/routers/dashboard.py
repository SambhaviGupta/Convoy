from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=schemas.KPIOut)
def get_kpis(db: Session = Depends(get_db), _=Depends(get_current_user)):
    vehicles = db.query(models.Vehicle).all()
    drivers = db.query(models.Driver).all()
    trips = db.query(models.Trip).all()

    active_vehicles = [v for v in vehicles if v.status != models.VehicleStatus.RETIRED]
    available_vehicles = [v for v in vehicles if v.status == models.VehicleStatus.AVAILABLE]
    vehicles_in_maintenance = [v for v in vehicles if v.status == models.VehicleStatus.IN_SHOP]
    on_trip_vehicles = [v for v in vehicles if v.status == models.VehicleStatus.ON_TRIP]

    active_trips = [t for t in trips if t.status == models.TripStatus.DISPATCHED]
    pending_trips = [t for t in trips if t.status == models.TripStatus.DRAFT]

    drivers_on_duty = [d for d in drivers if d.status == models.DriverStatus.ON_TRIP]

    # Utilization: share of the active (non-retired) fleet currently out on a trip
    fleet_utilization_percent = (
        round((len(on_trip_vehicles) / len(active_vehicles)) * 100, 2)
        if active_vehicles
        else 0.0
    )

    return schemas.KPIOut(
        active_vehicles=len(active_vehicles),
        available_vehicles=len(available_vehicles),
        vehicles_in_maintenance=len(vehicles_in_maintenance),
        active_trips=len(active_trips),
        pending_trips=len(pending_trips),
        drivers_on_duty=len(drivers_on_duty),
        fleet_utilization_percent=fleet_utilization_percent,
    )
