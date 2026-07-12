import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


def _vehicle_financials(db: Session, vehicle: models.Vehicle) -> schemas.VehicleReportOut:
    fuel_logs = db.query(models.FuelLog).filter(models.FuelLog.vehicle_id == vehicle.id).all()
    maintenance_logs = (
        db.query(models.MaintenanceLog).filter(models.MaintenanceLog.vehicle_id == vehicle.id).all()
    )
    expenses = db.query(models.Expense).filter(models.Expense.vehicle_id == vehicle.id).all()
    completed_trips = (
        db.query(models.Trip)
        .filter(
            models.Trip.vehicle_id == vehicle.id,
            models.Trip.status == models.TripStatus.COMPLETED,
        )
        .all()
    )

    total_fuel_liters = sum(f.liters for f in fuel_logs)
    total_fuel_cost = sum(f.cost for f in fuel_logs)
    total_maintenance_cost = sum(m.cost for m in maintenance_logs)
    total_distance = sum((t.planned_distance or 0) for t in completed_trips)

    # Revenue isn't a modeled entity in the spec — treated here as the sum of
    # Expense records logged with type "Revenue" (a lightweight convention
    # rather than a dedicated table, to stay within the given schema).
    total_revenue = sum(e.amount for e in expenses if e.type.lower() == "revenue")

    operational_cost = total_fuel_cost + total_maintenance_cost

    fuel_efficiency = (
        round(total_distance / total_fuel_liters, 2) if total_fuel_liters > 0 else None
    )
    roi = (
        round((total_revenue - operational_cost) / vehicle.acquisition_cost, 4)
        if vehicle.acquisition_cost > 0
        else None
    )

    return schemas.VehicleReportOut(
        vehicle_id=vehicle.id,
        registration_number=vehicle.registration_number,
        fuel_efficiency=fuel_efficiency,
        total_fuel_cost=round(total_fuel_cost, 2),
        total_maintenance_cost=round(total_maintenance_cost, 2),
        operational_cost=round(operational_cost, 2),
        total_revenue=round(total_revenue, 2),
        roi=roi,
    )


@router.get("/vehicle/{vehicle_id}", response_model=schemas.VehicleReportOut)
def get_vehicle_report(
    vehicle_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return _vehicle_financials(db, vehicle)


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db), _=Depends(get_current_user)):
    vehicles = db.query(models.Vehicle).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "registration_number", "name_model", "type", "status",
            "fuel_efficiency", "total_fuel_cost", "total_maintenance_cost",
            "operational_cost", "total_revenue", "roi",
        ]
    )
    for vehicle in vehicles:
        r = _vehicle_financials(db, vehicle)
        writer.writerow(
            [
                vehicle.registration_number, vehicle.name_model, vehicle.type, vehicle.status.value,
                r.fuel_efficiency, r.total_fuel_cost, r.total_maintenance_cost,
                r.operational_cost, r.total_revenue, r.roi,
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transitops_report.csv"},
    )
