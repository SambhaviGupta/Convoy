from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 - ensures models are registered before create_all
from app.routers import auth, vehicles, drivers, trips, maintenance, fuel_logs, expenses, dashboard, reports

app = FastAPI(title="Convoy API", version="0.1.0")

# Wide-open CORS for hackathon speed — tighten origins before any real deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates any tables that don't exist yet on the Neon database. Safe to
    # run every startup — it no-ops for tables that already exist.
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok", "service": "TransitOps API"}


app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(drivers.router)
app.include_router(trips.router)
app.include_router(maintenance.router)
app.include_router(fuel_logs.router)
app.include_router(expenses.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
