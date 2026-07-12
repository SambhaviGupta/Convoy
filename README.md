# Convoy 🚚

**Smart Transport Operations Platform** — built in a 4-hour hackathon sprint.

Convoy replaces spreadsheets and manual logbooks for logistics companies managing a vehicle fleet. It digitizes the complete lifecycle of transport operations — vehicle registration, driver management, trip dispatch, maintenance, and fuel/expense tracking — while automatically enforcing business rules that a spreadsheet can't.

## The Problem

Logistics companies still rely on manual logs to manage vehicles and drivers. This leads to:
- Scheduling conflicts (double-booking vehicles or drivers)
- Overloaded vehicles (cargo exceeding capacity)
- Drivers with expired licenses getting assigned to trips
- No real-time visibility into fleet status

## What Convoy Does

Convoy doesn't just store data — it **enforces the rules** so bad assignments are blocked before they happen.

- **Vehicle Registry** — track every vehicle's status live: `Available` / `On Trip` / `In Shop` / `Retired`
- **Driver Management** — track driver status and license validity: `Available` / `On Trip` / `Off Duty` / `Suspended`
- **Trip Dispatch with validation**
  - Cargo weight can't exceed the vehicle's max load capacity
  - A vehicle or driver already on a trip can't be double-booked
  - Drivers with expired or suspended licenses can't be dispatched
- **Automatic status transitions** — dispatching a trip flips vehicle + driver to `On Trip`; completing or cancelling flips them back to `Available` — no manual updates needed
- **Maintenance workflow** — logging a maintenance record instantly pulls that vehicle out of the dispatch pool until it's closed
- **Fuel & expense tracking** — logs costs per vehicle, rolled into operational cost calculations
- **Live dashboard** — active vehicles, available vehicles, vehicles in maintenance, active/pending trips, fleet utilization %

## Tech Stack

**Frontend**
- React + Vite
- React Router
- Tailwind CSS
- Axios

**Backend**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL (hosted on [Neon](https://neon.tech))
- JWT-based authentication
- Passlib + bcrypt for password hashing

## Project Structure
Convoy/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── database.py      # DB connection/engine setup
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── security.py      # Password hashing, JWT handling
│   │   ├── seed.py          # Demo data seeding
│   │   └── routers/         # API route handlers
│   ├── requirements.txt
│   └── .env                 # DATABASE_URL (not committed)
└── frontend/
├── src/
│   ├── api/              # Axios API layer
│   ├── context/          # Auth context
│   ├── components/       # Navbar, StatusBadge, ProtectedRoute
│   ├── pages/             # Login, Dashboard, Vehicles, Drivers, Trips, Maintenance
│   └── App.jsx
└── vite.config.js

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with your PostgreSQL connection string:
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require

Run the server:

```bash
python -m uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:5173`

## Demo Workflow

1. Sign up / log in as a Fleet Manager
2. Register vehicle **Van-05** with a max load capacity of 500kg
3. Register driver **Alex** with a valid license
4. Create a trip with 450kg cargo, assign Van-05 and Alex
5. Dispatch the trip → vehicle and driver automatically flip to `On Trip`
6. Complete the trip → both flip back to `Available`
7. Log a maintenance record on Van-05 → it disappears from the dispatch pool, status becomes `In Shop`
8. Close the maintenance record → vehicle becomes `Available` again
9. View live KPIs on the Dashboard

## Team

Built by a 2-person team for a hackathon within a 4-hour build window.

## License

Built for hackathon submission purposes.
