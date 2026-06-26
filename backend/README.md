# SafeAlert — Community Security Alert System

A multi-channel incident reporting and dispatch platform built for the hackathon. Citizens report security incidents via USSD (*384*1#) or a Flutter mobile app. Reports are scored, tiered, and dispatched automatically by a central core engine.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      REPORTERS                          │
│                                                         │
│  Feature phone           Flutter mobile app             │
│  (dials *384*1#)         (Android / iOS / Web)          │
└──────────┬───────────────────────┬──────────────────────┘
           │                       │
           ▼                       ▼
┌──────────────────┐   ┌───────────────────────┐
│  USSD Service    │   │   Mobile API          │
│  ussd_service.py │   │   mobile_api.py        │
│  :8000           │   │   :8001                │
│                  │   │                        │
│  Africa's Talking│   │  JWT auth, rate limit  │
│  → Supabase DB   │   │  → SQLite (users)      │
└────────┬─────────┘   └──────────┬─────────────┘
         │                        │
         │   POST /incidents/create│
         └──────────┬─────────────┘
                    ▼
         ┌─────────────────────┐
         │   Core Engine       │
         │   core_engine.py    │
         │   :8002             │
         │                     │
         │  Confidence scoring │
         │  Tier assignment    │
         │  Dispatch logic     │
         │  → SQLite (engine)  │
         └─────────────────────┘
```

---

## Services

### 1. USSD Service — `services/ussd_service.py` (port 8000)

Receives USSD callbacks from **Africa's Talking** and writes incident reports to **Supabase (PostgreSQL)**.

| Menu path | Action |
|---|---|
| Dial `*384*1#` | Main menu |
| `1` | Report incident |
| `1 → 1-6` | Choose incident type |
| `1 → type → 1` | Use registered address (looked up from Supabase `users` table) |
| `1 → type → 2` | Enter LGA manually |
| `2` | Check area safety (submits a safety-check report) |
| `3` | Exit |

**Ref codes** are formatted `A` + 4 random alphanumeric chars (e.g. `AK9M2`).

---

### 2. Mobile API — `services/mobile_api.py` (port 8001)

Flutter-facing REST API with JWT authentication. All routes except `/auth/*` require a `Bearer` token.

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| POST | `/auth/register` | — | Returns JWT + user fields |
| POST | `/auth/login` | — | Returns JWT + credibility_weight |
| POST | `/auth/device-token` | Bearer | Stores FCM push token |
| POST | `/incidents/report` | Bearer | Rate-limited 5/hr per user |
| GET | `/incidents/nearby?lat=&lng=&radius_km=` | Bearer | Proxied to core engine |
| GET | `/alerts/active` | Bearer | Proxied to core engine |

**Credibility weight** starts at 1.0 and grows with account age and report count (capped at 5.0). It is forwarded to the core engine on every report.

**Rate limiting** is per authenticated user ID, not per IP (important for Flutter apps behind mobile NAT).

---

### 3. Core Engine — `services/core_engine.py` (port 8002)

The brain of the system. Scores every incoming report and assigns a dispatch tier.

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/incidents/create` | Intake from USSD or mobile |
| GET | `/incidents/nearby` | Coordinate or string-based search |
| GET | `/incidents/area-safety?location=` | Returns LOW/MODERATE/HIGH/CRITICAL |
| GET | `/alerts/active` | Tier 3 active incidents only |
| GET | `/incidents/confirm/{ref}` | Authority confirmation — re-runs scoring |
| POST | `/admin/set-high-risk-areas` | Live-update risk zone list |

**Confidence scoring breakdown:**

| Component | Points |
|---|---|
| Base severity (by incident type) | 10–50 |
| High-risk area name match OR prior tier 2+ in last 7 days | +15 |
| 3+ distinct reporters, same type, same location, last 60 min | +20 |
| Verified reporter | +10 |
| Active incident cluster within 500m / same location | +15 |
| Authority confirmed | +20 |
| **Cap** | **100** |

**Tier assignment:**

| Score | Tier | Status | Action |
|---|---|---|---|
| 0–39 | 1 — Monitoring | pending | Dashboard only |
| 40–79 | 2 — Elevated Alert | active | Patrol unit notified (console mock) |
| 80–100 | 3 — Critical Public Alert | active | Public alert + drone note (console mock) |

---

## Prerequisites

### Python
- **Python 3.11+** is required (uses `X | Y` union syntax and `match` patterns).
- Install it from [python.org](https://python.org) or via `winget install Python.Python.3.11`.

### pip packages (install per service)
```bash
# Core Engine
pip install -r requirements/engine.txt

# Mobile API
pip install -r requirements/mobile.txt

# USSD Service
pip install -r requirements/ussd.txt
```

### External accounts / SDKs you need

| What | Where | Used by |
|---|---|---|
| **Africa's Talking** sandbox account | [africastalking.com](https://africastalking.com) | USSD service |
| **Supabase** project | [supabase.com](https://supabase.com) | USSD service |
| **ngrok** (or similar tunnel) | [ngrok.com](https://ngrok.com) | USSD callback (AT can't reach localhost) |
| **Flutter SDK** | [flutter.dev](https://flutter.dev) | Mobile app (separate repo) |

---

## Setup

### Step 1 — Copy and fill the env file

```bash
cp .env.example .env
# Open .env and fill in every value — see comments inside the file
```

The three services share one `.env` file. Each service only reads the keys it needs.

### Step 2 — Set up Supabase (for the USSD service)

1. Create a new Supabase project at [app.supabase.com](https://app.supabase.com).
2. Go to **Project Settings → Database** and copy the **Connection string** (URI format).
3. Replace `postgresql://` with `postgresql+asyncpg://` and paste it as `SUPABASE_DB_URL` in `.env`.
4. The USSD service will auto-create the `users` and `incident_reports` tables on first run.

> **Tip:** To pre-populate a test user with a registered address, run in the Supabase SQL editor:
> ```sql
> INSERT INTO users (id, phone_number, registered_address, lga)
> VALUES (gen_random_uuid(), '+2348012345678', '12 Adeola St, Ikeja', 'Ikeja');
> ```

### Step 3 — Set up Africa's Talking sandbox

1. Log in at [account.africastalking.com](https://account.africastalking.com).
2. Go to **Sandbox → USSD → Create Channel** — use shortcode `*384*1#`.
3. Set the **callback URL** to your tunnel URL + `/ussd`:
   ```
   https://your-ngrok-url.ngrok-free.app/ussd
   ```
4. Copy your **API key** and set `AT_API_KEY` in `.env`. Leave `AT_USERNAME=sandbox`.

### Step 4 — Start ngrok (needed for AT to reach your machine)

```bash
ngrok http 8000
# Copy the https:// URL and paste it into the AT sandbox callback field
```

---

## Running the Services

Open **three separate terminals** and run one service per terminal. Start them in this order:

```bash
# Terminal 1 — Core Engine (must start first; others depend on it)
cd services
uvicorn core_engine:app --host 0.0.0.0 --port 8002 --reload

# Terminal 2 — Mobile API
cd services
uvicorn mobile_api:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3 — USSD Service
cd services
uvicorn ussd_service:app --host 0.0.0.0 --port 8000 --reload
```

All services auto-reload on file save when `--reload` is set.

---

## Interactive API Docs

FastAPI generates live docs at:

| Service | Docs URL |
|---|---|
| Core Engine | http://localhost:8002/docs |
| Mobile API | http://localhost:8001/docs |
| USSD Service | http://localhost:8000/docs |

---

## Quick Smoke Tests (curl)

### Register a user (mobile API)
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","phone_number":"+2348012345678","password":"password123"}'
```

### Submit an incident (core engine directly)
```bash
curl -X POST http://localhost:8002/incidents/create \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_user_id": "+2348012345678",
    "incident_type": "Armed Robbery",
    "location": "Kaduna North Market",
    "latitude": 10.5105,
    "longitude": 7.4165,
    "source": "app",
    "is_verified_reporter": false
  }'
```

### Authority-confirm an incident (bumps score by +20, may escalate tier)
```bash
curl http://localhost:8002/incidents/confirm/SA3K9M2
```

### Live-update high-risk areas (for demo)
```bash
curl -X POST http://localhost:8002/admin/set-high-risk-areas \
  -H "Content-Type: application/json" \
  -d '{"areas": ["Zamfara", "Kaduna North", "Borno", "Sokoto", "Katsina", "Plateau"]}'
```

### Simulate USSD callback (Africa's Talking format)
```bash
curl -X POST http://localhost:8000/ussd \
  -d "sessionId=sess_001&serviceCode=*384*1%23&phoneNumber=%2B2348012345678&text="
```

---

## Project Layout

```
safealert/
├── services/
│   ├── ussd_service.py   # USSD handler + Supabase models (single file)
│   ├── mobile_api.py     # Flutter backend — auth, rate limiting, proxy
│   └── core_engine.py    # Scoring, tiering, dispatch, SQLite persistence
├── requirements/
│   ├── ussd.txt          # asyncpg + SQLAlchemy + FastAPI
│   ├── mobile.txt        # jose + passlib + slowapi + httpx
│   └── engine.txt        # aiosqlite + SQLAlchemy + FastAPI
├── .env.example          # Template — copy to .env and fill in secrets
├── .gitignore
└── README.md
```

---

## Environment Variables Reference

| Variable | Service | Description |
|---|---|---|
| `SUPABASE_DB_URL` | USSD | `postgresql+asyncpg://...` connection string |
| `AT_API_KEY` | USSD | Africa's Talking API key |
| `AT_USERNAME` | USSD | `sandbox` for testing |
| `ENGINE_URL` | Mobile | URL of core engine, default `http://localhost:8002` |
| `JWT_SECRET` | Mobile | Long random string used to sign tokens |
| `JWT_EXPIRE_MINUTES` | Mobile | Token lifetime, default `60` |
| `DB_PATH` | Mobile | SQLite file for user accounts, default `safealert_users.db` |
| `DATABASE_URL` | Engine | SQLite path, default `sqlite+aiosqlite:///./safealert.db` |

---

## Notes for Teammates

- **Do not commit `.env`** — it is in `.gitignore`. Share secrets out-of-band (WhatsApp/DM).
- The **core engine must be running** before the mobile API or USSD service, because both forward reports to it.
- The **USSD service needs ngrok** running and the AT sandbox callback URL updated any time ngrok restarts (free tier gives a new URL each restart — pay tier or use `--domain` to fix it).
- SQLite `.db` files are also gitignored — they are generated at runtime in whatever directory you run uvicorn from. Run from inside `services/` so the files land there consistently.
- Swagger UI at `/docs` on each port is the fastest way to test endpoints without curl.
