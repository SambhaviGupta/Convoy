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

## What's built so far (Hour 1 scope)

- `POST /auth/signup`, `POST /auth/login` — JWT auth
- `GET/POST /vehicles`, `PUT /vehicles/{id}`, `GET /vehicles/available`
- `GET/POST /drivers`, `PUT /drivers/{id}`, `GET /drivers/available`
- All routes except `/`, `/auth/*` require a Bearer token (click "Authorize" in
  Swagger, paste the `token` value returned from signup/login)

## Testing quickly in Swagger

1. `POST /auth/signup` with a Fleet Manager role → copy the `token`
2. Click **Authorize** top-right, paste the token
3. `POST /vehicles` to create Van-05, `POST /drivers` to create Alex
4. `GET /vehicles/available` / `GET /drivers/available` should show them

## Next up (Hour 2, 1:00–2:15)

Trip endpoints: create, dispatch, complete, cancel — with the three validation
rules (capacity, availability, license expiry) and automatic status flips on
Vehicle + Driver. Say the word and I'll build that next.

## Coming after that

- Maintenance endpoints (auto flips vehicle to In Shop / back to Available)
- Fuel & Expense logging
- `/dashboard/kpis`
- CORS is already wide-open (`allow_origins=["*"]`) so Person B can hit this
  from `localhost:5173` with zero extra config
