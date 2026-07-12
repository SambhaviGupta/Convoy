"""
Seeds the Neon database with demo data so the demo doesn't start from an
empty UI. Safe to re-run — it checks for existing records before inserting.

Usage:
    python -m app.seed
"""
from datetime import date, timedelta

from app.database import Base, engine, SessionLocal
from app import models
from app.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # --- Demo user (Fleet Manager) ---
        demo_user = db.query(models.User).filter(models.User.email == "manager@transitops.demo").first()
        if not demo_user:
            demo_user = models.User(
                name="Demo Fleet Manager",
                email="manager@transitops.demo",
                password_hash=hash_password("demo1234"),
                role=models.UserRole.FLEET_MANAGER,
            )
            db.add(demo_user)
            print("Created demo user: manager@transitops.demo / demo1234")
        else:
            print("Demo user already exists, skipping")

        # --- Vehicles ---
        van05 = db.query(models.Vehicle).filter(models.Vehicle.registration_number == "VAN-05").first()
        if not van05:
            van05 = models.Vehicle(
                registration_number="VAN-05",
                name_model="Tata Ace Gold",
                type="Van",
                max_load_capacity=500,
                odometer=12500,
                acquisition_cost=850000,
                status=models.VehicleStatus.AVAILABLE,
            )
            db.add(van05)
            print("Created vehicle VAN-05")
        else:
            print("VAN-05 already exists, skipping")

        truck12 = db.query(models.Vehicle).filter(models.Vehicle.registration_number == "TRK-12").first()
        if not truck12:
            truck12 = models.Vehicle(
                registration_number="TRK-12",
                name_model="Ashok Leyland Dost+",
                type="Truck",
                max_load_capacity=1500,
                odometer=48210,
                acquisition_cost=1450000,
                status=models.VehicleStatus.AVAILABLE,
            )
            db.add(truck12)
            print("Created vehicle TRK-12")
        else:
            print("TRK-12 already exists, skipping")

        # --- Drivers ---
        alex = db.query(models.Driver).filter(models.Driver.license_number == "DL-ALEX-2026").first()
        if not alex:
            alex = models.Driver(
                name="Alex",
                license_number="DL-ALEX-2026",
                license_category="LMV",
                license_expiry_date=date.today() + timedelta(days=365),
                contact_number="9876543210",
                safety_score=92,
                status=models.DriverStatus.AVAILABLE,
            )
            db.add(alex)
            print("Created driver Alex")
        else:
            print("Driver Alex already exists, skipping")

        priya = db.query(models.Driver).filter(models.Driver.license_number == "DL-PRIYA-2026").first()
        if not priya:
            priya = models.Driver(
                name="Priya",
                license_number="DL-PRIYA-2026",
                license_category="HMV",
                license_expiry_date=date.today() + timedelta(days=200),
                contact_number="9876500000",
                safety_score=88,
                status=models.DriverStatus.AVAILABLE,
            )
            db.add(priya)
            print("Created driver Priya")
        else:
            print("Driver Priya already exists, skipping")

        db.commit()
        db.refresh(van05)
        db.refresh(alex)

        # --- One demo trip (Draft, ready to dispatch live in the demo) ---
        existing_trip = (
            db.query(models.Trip)
            .filter(models.Trip.vehicle_id == van05.id, models.Trip.driver_id == alex.id)
            .first()
        )
        if not existing_trip:
            trip = models.Trip(
                source="Kanpur Warehouse",
                destination="Lucknow Distribution Hub",
                vehicle_id=van05.id,
                driver_id=alex.id,
                cargo_weight=450,
                planned_distance=90,
                status=models.TripStatus.DRAFT,
            )
            db.add(trip)
            db.commit()
            print("Created demo trip: Van-05 + Alex, 450kg, Draft status (ready to dispatch live)")
        else:
            print("Demo trip already exists, skipping")

        print("\nSeed complete. Login with manager@transitops.demo / demo1234")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
