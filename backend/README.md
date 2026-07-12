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

## What's built so far (Hour 1 + Hour 2 scope)

- `POST /auth/signup`, `POST /auth/login` — JWT auth
- `GET/POST /vehicles`, `PUT /vehicles/{id}`, `GET /vehicles/available`
- `GET/POST /drivers`, `PUT /drivers/{id}`, `GET /drivers/available`
- `GET/POST /trips`, `POST /trips/{id}/dispatch`, `POST /trips/{id}/complete`, `POST /trips/{id}/cancel`
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

## Testing the full demo workflow in Swagger

1. `POST /auth/signup` with a Fleet Manager role → copy the `token`, click **Authorize**, paste it
2. `POST /vehicles` → Van-05, max_load_capacity 500
3. `POST /drivers` → Alex, license_expiry_date in the future
4. `POST /trips` → cargo_weight 450, using Van-05's and Alex's ids → status `Draft`
5. `POST /trips/{id}/dispatch` → succeeds, trip `Dispatched`, vehicle & driver both `On Trip`
6. Try creating another trip with cargo_weight 600 and dispatching it → `400` (over capacity) — this is the validation demo moment
7. `POST /trips/{id}/complete` with odometer + fuel → trip `Completed`, vehicle & driver both back to `Available`

## Next up (Hour 3, 2:15–2:45)

Maintenance endpoints (auto flips vehicle to In Shop / back to Available) +
Fuel & Expense logging. Say the word and I'll build that next.

## Coming after that

- `/dashboard/kpis` aggregation (Hour 3, 2:45–3:15)
- CORS is already wide-open (`allow_origins=["*"]`) so Person B can hit this
  from `localhost:5173` with zero extra config
