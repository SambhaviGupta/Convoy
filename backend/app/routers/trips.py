from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/trips", tags=["trips"])


def _get_vehicle_or_404(db: Session, vehicle_id: int) -> models.Vehicle:
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def _get_driver_or_404(db: Session, driver_id: int) -> models.Driver:
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


def _get_trip_or_404(db: Session, trip_id: int) -> models.Trip:
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("", response_model=List[schemas.TripOut])
def list_trips(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Trip).order_by(models.Trip.id.desc()).all()


@router.post("", response_model=schemas.TripOut)
def create_trip(
    payload: schemas.TripCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Creates a trip in Draft status. Full eligibility validation (capacity,
    availability, license expiry) runs at dispatch time, not here — Draft is
    meant to be a lightweight staging step. We still block the two things
    that can never be fixed later: nonexistent vehicle/driver.
    """
    vehicle = _get_vehicle_or_404(db, payload.vehicle_id)
    driver = _get_driver_or_404(db, payload.driver_id)

    if payload.cargo_weight > vehicle.max_load_capacity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cargo weight {payload.cargo_weight}kg exceeds vehicle "
                f"max load capacity {vehicle.max_load_capacity}kg"
            ),
        )

    trip = models.Trip(
        source=payload.source,
        destination=payload.destination,
        vehicle_id=payload.vehicle_id,
        driver_id=payload.driver_id,
        cargo_weight=payload.cargo_weight,
        planned_distance=payload.planned_distance,
        status=models.TripStatus.DRAFT,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.post("/{trip_id}/dispatch", response_model=schemas.TripOut)
def dispatch_trip(
    trip_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    trip = _get_trip_or_404(db, trip_id)

    if trip.status != models.TripStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Only Draft trips can be dispatched (current status: {trip.status.value})",
        )

    vehicle = _get_vehicle_or_404(db, trip.vehicle_id)
    driver = _get_driver_or_404(db, trip.driver_id)

    # Rule: cargo weight must not exceed vehicle max load capacity
    if trip.cargo_weight > vehicle.max_load_capacity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cargo weight {trip.cargo_weight}kg exceeds vehicle "
                f"max load capacity {vehicle.max_load_capacity}kg"
            ),
        )

    # Rule: vehicle must be Available (Retired/In Shop/On Trip vehicles can never dispatch)
    if vehicle.status != models.VehicleStatus.AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail=f"Vehicle {vehicle.registration_number} is not Available (status: {vehicle.status.value})",
        )

    # Rule: driver must be Available, not Suspended, license not expired
    if driver.status != models.DriverStatus.AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail=f"Driver {driver.name} is not Available (status: {driver.status.value})",
        )
    if driver.license_expiry_date < date.today():
        raise HTTPException(
            status_code=400,
            detail=f"Driver {driver.name}'s license expired on {driver.license_expiry_date}",
        )

    # All rules passed — dispatch and auto-flip both statuses
    trip.status = models.TripStatus.DISPATCHED
    vehicle.status = models.VehicleStatus.ON_TRIP
    driver.status = models.DriverStatus.ON_TRIP

    db.commit()
    db.refresh(trip)
    return trip


@router.post("/{trip_id}/complete", response_model=schemas.TripOut)
def complete_trip(
    trip_id: int,
    payload: schemas.TripCompleteInput,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)

    if trip.status != models.TripStatus.DISPATCHED:
        raise HTTPException(
            status_code=400,
            detail=f"Only Dispatched trips can be completed (current status: {trip.status.value})",
        )

    vehicle = _get_vehicle_or_404(db, trip.vehicle_id)
    driver = _get_driver_or_404(db, trip.driver_id)

    trip.actual_odometer_end = payload.actual_odometer_end
    trip.fuel_consumed = payload.fuel_consumed
    trip.status = models.TripStatus.COMPLETED

    # Auto-flip both back to Available
    vehicle.status = models.VehicleStatus.AVAILABLE
    vehicle.odometer = payload.actual_odometer_end
    driver.status = models.DriverStatus.AVAILABLE

    db.commit()
    db.refresh(trip)
    return trip


@router.post("/{trip_id}/cancel", response_model=schemas.TripOut)
def cancel_trip(
    trip_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    trip = _get_trip_or_404(db, trip_id)

    if trip.status not in (models.TripStatus.DRAFT, models.TripStatus.DISPATCHED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel a trip with status {trip.status.value}",
        )

    was_dispatched = trip.status == models.TripStatus.DISPATCHED
    trip.status = models.TripStatus.CANCELLED

    # Only restore statuses if the trip had actually taken the vehicle/driver
    # out of the pool (i.e. it was Dispatched, not still Draft)
    if was_dispatched:
        vehicle = _get_vehicle_or_404(db, trip.vehicle_id)
        driver = _get_driver_or_404(db, trip.driver_id)
        vehicle.status = models.VehicleStatus.AVAILABLE
        driver.status = models.DriverStatus.AVAILABLE

    db.commit()
    db.refresh(trip)
    return trip
