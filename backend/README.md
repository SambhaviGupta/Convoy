# TransitOps Backend (Person A)

FastAPI + SQLAlchemy + Neon Postgres.

## Setup (do this first)

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Paste your Neon connection string into .env as DATABASE_URL
```

Get your connection string from console.neon.tech → your project → **Connection string**.
Make sure it ends with `?sslmode=require` (Neon requires SSL).

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Then open **http://localhost:8000/docs** — Swagger UI. Tables are auto-created on
the Neon database on first startup (no manual migration needed for the hackathon).

## What's built so far (Hour 1 + 2 + 3 scope — backend is functionally complete)

- `POST /auth/signup`, `POST /auth/login` — JWT auth
- `GET/POST /vehicles`, `PUT /vehicles/{id}`, `GET /vehicles/available`
- `GET/POST /drivers`, `PUT /drivers/{id}`, `GET /drivers/available`
- `GET/POST /trips`, `POST /trips/{id}/dispatch`, `POST /trips/{id}/complete`, `POST /trips/{id}/cancel`
- `GET/POST /maintenance`, `POST /maintenance/{id}/close`
- `GET/POST /fuel-logs`
- `GET/POST /expenses`
- `GET /dashboard/kpis`
- `GET /reports/vehicle/{id}`, `GET /reports/export.csv`
- All routes except `/`, `/auth/*` require a Bearer token (click "Authorize" in
  Swagger, paste the `token` value returned from signup/login)

## Trip logic (the demo centerpiece)

`POST /trips` creates a trip in **Draft** status. It only blocks on
nonexistent vehicle/driver or cargo over capacity — everything else is
checked at dispatch, since Draft is meant to be a lightweight staging step.

`POST /trips/{id}/dispatch` is where all three mandatory rules are enforced,
in this order, each returning `400` with a specific message on failure:
1. `cargo_weight <= vehicle.max_load_capacity`
2. `vehicle.status == Available`
3. `driver.status == Available` and `driver.license_expiry_date >= today`

On success: trip → `Dispatched`, vehicle → `On Trip`, driver → `On Trip`.

`POST /trips/{id}/complete` (body: `actual_odometer_end`, `fuel_consumed`)
only works on a `Dispatched` trip. On success: trip → `Completed`, vehicle →
`Available` (odometer updated), driver → `Available`.

`POST /trips/{id}/cancel` works on `Draft` or `Dispatched` trips. If it was
`Dispatched`, vehicle and driver are restored to `Available`.

## Maintenance logic

`POST /maintenance` creates an active maintenance record and immediately
flips the vehicle to `In Shop` — this is what hides it from
`/vehicles/available` and therefore from the trip dispatch dropdown.

`POST /maintenance/{id}/close` closes the record and restores the vehicle to
`Available`, unless the vehicle is `Retired` or another active maintenance
record still exists for it (so two concurrent maintenance logs on the same
vehicle don't prematurely re-open it).

## Fuel & Expense logging

Plain create/list endpoints tied to a `vehicle_id`. These feed the reports
endpoint below.

## Dashboard KPIs

`GET /dashboard/kpis` returns: active vehicles (non-Retired), available
vehicles, vehicles in maintenance, active trips (Dispatched), pending trips
(Draft), drivers on duty (On Trip), and fleet utilization % — the share of
the active fleet currently On Trip.

## Reports

`GET /reports/vehicle/{id}` returns fuel efficiency (distance/liter from
completed trips), total fuel cost, total maintenance cost, operational cost
(fuel + maintenance), total revenue, and ROI.

**Assumption called out:** the spec's ROI formula needs a revenue figure, but
revenue isn't a modeled entity anywhere in the data model. This implementation
treats any `Expense` logged with `type = "Revenue"` as revenue for that
vehicle — a lightweight convention rather than a new table, to stay within
the given schema. If your actual data won't have "Revenue" expenses, `roi`
will just come back `null`, which is expected and not a bug.

`GET /reports/export.csv` streams a CSV of all vehicles with the same
figures — this is the bonus CSV export feature from the spec.

## Testing the full demo workflow in Swagger

1. `POST /auth/signup` with a Fleet Manager role → copy the `token`, click **Authorize**, paste it
2. `POST /vehicles` → Van-05, max_load_capacity 500
3. `POST /drivers` → Alex, license_expiry_date in the future
4. `POST /trips` → cargo_weight 450, using Van-05's and Alex's ids → status `Draft`
5. `POST /trips/{id}/dispatch` → succeeds, trip `Dispatched`, vehicle & driver both `On Trip`
6. Try creating another trip with cargo_weight 600 and dispatching it → `400` (over capacity) — this is the validation demo moment
7. `POST /trips/{id}/complete` with odometer + fuel → trip `Completed`, vehicle & driver both back to `Available`
8. `POST /maintenance` on Van-05 → `GET /vehicles/available` no longer shows it
9. `POST /maintenance/{id}/close` → Van-05 reappears in `/vehicles/available`
10. `POST /fuel-logs` and `POST /expenses` on Van-05
11. `GET /dashboard/kpis` → numbers reflect everything above
12. `GET /reports/vehicle/{id}` → fuel efficiency + costs show up

## Next up (3:15–3:45)

CORS is already done. Seed script is done — see below.

## Seeding demo data

Run this once your `.env` is pointed at your real Neon database:

```bash
python -m app.seed
```

It's idempotent (safe to re-run) and creates:
- A demo Fleet Manager user: `manager@transitops.demo` / `demo1234`
- Two vehicles: `VAN-05` (500kg capacity) and `TRK-12` (1500kg capacity), both `Available`
- Two drivers: `Alex` and `Priya`, both `Available` with valid licenses
- One `Draft` trip: Van-05 + Alex, 450kg cargo, Kanpur → Lucknow — this is
  left in `Draft` on purpose so you can dispatch it live during the demo
  instead of starting from a completely empty screen.

Login with the demo user, or `POST /auth/signup` your own — either works
against the same seeded data.

## Backend is now feature-complete for the 4-hour plan

Everything from the execution plan's Person A column (12:00–3:45) is done:
scaffold, auth, Vehicle/Driver CRUD, trip lifecycle + validation rules,
maintenance auto-flip, fuel/expense logging, dashboard KPIs, reports + CSV
export, CORS, and seed data.

What's left is the 3:45–4:00 slot — bug triage with Person B once the
frontend is actually calling this API, and the live demo run-through. Ping
me the moment something doesn't line up with what the frontend expects and
I'll fix it fast.
