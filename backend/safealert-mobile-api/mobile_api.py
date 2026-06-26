import os
import uuid
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

ENGINE_URL = os.getenv("ENGINE_URL", "http://localhost:8002").rstrip("/")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-set-in-env")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
JWT_ALGORITHM = "HS256"
DB_PATH = os.getenv("DB_PATH", "safealert_users.db")

# ── Password hashing ──────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── Rate limiter (per authenticated user, falls back to IP for unauthed) ──────

def _user_or_ip_key(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = jwt.decode(
                auth[7:], JWT_SECRET, algorithms=[JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=_user_or_ip_key)

# ── SQLite helpers ────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id                 TEXT PRIMARY KEY,
                email              TEXT UNIQUE NOT NULL,
                phone_number       TEXT,
                hashed_password    TEXT NOT NULL,
                credibility_weight REAL    DEFAULT 1.0,
                report_count       INTEGER DEFAULT 0,
                fcm_token          TEXT,
                created_at         TEXT NOT NULL
            )
        """)
        c.commit()


def _row_to_dict(row) -> Optional[dict]:
    return dict(row) if row else None


def db_get_user_by_email(email: str) -> Optional[dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return _row_to_dict(row)


def db_get_user_by_id(user_id: str) -> Optional[dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def db_create_user(email: str, phone_number: str, hashed_password: str) -> dict:
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            "INSERT INTO users (id, email, phone_number, hashed_password, created_at) VALUES (?,?,?,?,?)",
            (user_id, email, phone_number, hashed_password, created_at),
        )
        c.commit()
    return db_get_user_by_id(user_id)


def db_set_fcm_token(user_id: str, token: str) -> None:
    with _conn() as c:
        c.execute("UPDATE users SET fcm_token = ? WHERE id = ?", (token, user_id))
        c.commit()


def db_increment_report_and_recalculate(user_id: str) -> None:
    with _conn() as c:
        c.execute(
            "UPDATE users SET report_count = report_count + 1 WHERE id = ?", (user_id,)
        )
        row = c.execute(
            "SELECT report_count, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row:
            report_count, created_at_str = row["report_count"], row["created_at"]
            months_old = (datetime.utcnow() - datetime.fromisoformat(created_at_str)).days / 30
            # Credibility grows with account age and verified report history, capped at 5.0
            weight = round(min(1.0 + (months_old * 0.05) + (report_count * 0.1), 5.0), 3)
            c.execute(
                "UPDATE users SET credibility_weight = ? WHERE id = ?", (weight, user_id)
            )
        c.commit()

# ── Auth dependency ───────────────────────────────────────────────────────────

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    user_id = _decode_token(credentials.credentials)
    user = db_get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User account not found")
    return user

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    phone_number: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class IncidentReportRequest(BaseModel):
    incident_type: str
    latitude: float
    longitude: float
    description: str
    photo_url: Optional[str] = None


class DeviceTokenRequest(BaseModel):
    fcm_token: str

# ── App setup ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="SafeAlert Mobile API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Flutter web + emulator both need this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        status_code=429,
        content={"detail": "Too many incident reports. Limit is 5 per hour."},
    )
    # Explicitly add CORS headers to prevent the browser from masking the error
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    # Print the real error to your backend terminal terminal so you can read what failed!
    print(f"CRITICAL BACKEND EXCEPTION: {str(exc)}")
    
    response = JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# ── Auth routes ───────────────────────────────────────────────────────────────

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    if db_get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(body.password)
    user = db_create_user(body.email, body.phone_number, hashed)
    return {
        "token": create_access_token(user["id"]),
        "user_id": user["id"],
        "email": user["email"],
        "phone_number": user["phone_number"],
    }


@app.post("/auth/login")
async def login(body: LoginRequest):
    user = db_get_user_by_email(body.email)
    if not user or not pwd_context.verify(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "token": create_access_token(user["id"]),
        "user_id": user["id"],
        "email": user["email"],
        "phone_number": user["phone_number"],
        "credibility_weight": user["credibility_weight"],
    }


@app.post("/auth/device-token")
async def store_device_token(
    body: DeviceTokenRequest,
    current_user: dict = Depends(get_current_user),
):
    db_set_fcm_token(current_user["id"], body.fcm_token)
    return {"status": "ok"}

# ── Incident routes ───────────────────────────────────────────────────────────

@app.post("/incidents/report")
@limiter.limit("5/hour")
async def report_incident(
    request: Request,
    body: IncidentReportRequest,
    current_user: dict = Depends(get_current_user),
):
    # Map fields explicitly to satisfy what the core engine schema expects
    engine_payload = {
        **body.model_dump(),
        "user_id": current_user["id"],
        "phone_number": current_user.get("phone_number"),
        "credibility_weight": current_user["credibility_weight"],
        
        # ── Fixes for the Core Engine Validation Errors ──
        "phone_or_user_id": current_user["id"],  # Satisfies 'phone_or_user_id' requirement
        "location": f"GPS: {body.latitude}, {body.longitude}",  # Satisfies 'location' requirement
        "source": "mobile"  # Satisfies 'source' requirement
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{ENGINE_URL}/incidents/create",
                json=engine_payload,
                timeout=10.0,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Engine rejected the report: {exc.response.text}",
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Core engine is unavailable")

    db_increment_report_and_recalculate(current_user["id"])

    data = resp.json()
    return {
        "ref_code": data.get("ref_code"),
        "status": data.get("status", "pending"),
    }


@app.get("/incidents/nearby")
async def nearby_incidents(
    lat: float,
    lng: float,
    radius_km: float = 5.0,
    current_user: dict = Depends(get_current_user),
):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{ENGINE_URL}/incidents/nearby",
                params={"lat": lat, "lng": lng, "radius_km": radius_km},
                timeout=10.0,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail="Engine error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Core engine is unavailable")

    return resp.json()

# ── Alert routes ──────────────────────────────────────────────────────────────

@app.get("/alerts/active")
async def active_alerts(current_user: dict = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{ENGINE_URL}/alerts/active", timeout=10.0)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail="Engine error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Core engine is unavailable")

    return resp.json()

# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("mobile_api:app", host="0.0.0.0", port=8001, reload=True)
