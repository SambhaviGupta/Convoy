from datetime import date as _date
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import UserRole, VehicleStatus, DriverStatus, TripStatus


# ---------- Auth / User ----------
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: UserRole


class TokenOut(BaseModel):
    token: str
    user: UserOut


# ---------- Vehicle ----------
class VehicleCreate(BaseModel):
    registration_number: str
    name_model: str
    type: str
    max_load_capacity: float
    odometer: Optional[float] = 0
    acquisition_cost: Optional[float] = 0
    status: VehicleStatus = VehicleStatus.AVAILABLE


class VehicleUpdate(BaseModel):
    name_model: Optional[str] = None
    type: Optional[str] = None
    max_load_capacity: Optional[float] = None
    odometer: Optional[float] = None
    acquisition_cost: Optional[float] = None
    status: Optional[VehicleStatus] = None


class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registration_number: str
    name_model: str
    type: str
    max_load_capacity: float
    odometer: float
    acquisition_cost: float
    status: VehicleStatus


# ---------- Driver ----------
class DriverCreate(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry_date: _date
    contact_number: Optional[str] = None
    safety_score: float = 100
    status: DriverStatus = DriverStatus.AVAILABLE


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    license_category: Optional[str] = None
    license_expiry_date: Optional[_date] = None
    contact_number: Optional[str] = None
    safety_score: Optional[float] = None
    status: Optional[DriverStatus] = None


class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    license_number: str
    license_category: str
    license_expiry_date: _date
    contact_number: Optional[str]
    safety_score: float
    status: DriverStatus


# ---------- Trip ----------
class TripCreate(BaseModel):
    source: str
    destination: str
    vehicle_id: int
    driver_id: int
    cargo_weight: float
    planned_distance: Optional[float] = None


class TripCompleteInput(BaseModel):
    actual_odometer_end: float
    fuel_consumed: float


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source: str
    destination: str
    vehicle_id: int
    driver_id: int
    cargo_weight: float
    planned_distance: Optional[float]
    actual_odometer_end: Optional[float]
    fuel_consumed: Optional[float]
    status: TripStatus


# ---------- Maintenance ----------
class MaintenanceCreate(BaseModel):
    vehicle_id: int
    description: str
    cost: float = 0
    date: Optional[_date] = None


class MaintenanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    description: str
    cost: float
    date: _date
    is_active: bool


# ---------- Fuel / Expense ----------
class FuelLogCreate(BaseModel):
    vehicle_id: int
    liters: float
    cost: float
    date: Optional[_date] = None


class FuelLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    liters: float
    cost: float
    date: _date


class ExpenseCreate(BaseModel):
    vehicle_id: int
    type: str
    amount: float
    date: Optional[_date] = None
    notes: Optional[str] = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    type: str
    amount: float
    date: _date
    notes: Optional[str]


# ---------- Dashboard ----------
class KPIOut(BaseModel):
    active_vehicles: int
    available_vehicles: int
    vehicles_in_maintenance: int
    active_trips: int
    pending_trips: int
    drivers_on_duty: int
    fleet_utilization_percent: float


# ---------- Reports ----------
class VehicleReportOut(BaseModel):
    vehicle_id: int
    registration_number: str
    fuel_efficiency: Optional[float]  # distance per liter, from completed trips
    total_fuel_cost: float
    total_maintenance_cost: float
    operational_cost: float  # fuel + maintenance
    total_revenue: float
    roi: Optional[float]  # (revenue - operational_cost) / acquisition_cost
