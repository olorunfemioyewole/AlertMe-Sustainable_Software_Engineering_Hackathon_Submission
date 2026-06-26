"""
SafeAlert USSD Service
Handles *384*1# via Africa's Talking sandbox.
Persists incident reports to Supabase (PostgreSQL) via SQLAlchemy async.

Run:
    cd services
    uvicorn ussd_service:app --host 0.0.0.0 --port 8000 --reload
"""
import os
import random
import string
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy import String, Float, DateTime
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

load_dotenv()

# ── Database ──────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    registered_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lga: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ref_code: Mapped[str] = mapped_column(String, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String, index=True)
    incident_type: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    location_method: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── Report service ────────────────────────────────────────────────────────────

INCIDENT_TYPES: dict[str, str] = {
    "1": "Armed Robbery",
    "2": "Kidnapping",
    "3": "Suspicious Activity",
    "4": "Vandalism",
    "5": "Banditry/Terrorism",
    "6": "Other",
}

_CHARS = string.ascii_uppercase + string.digits


async def _generate_ref_code(db: AsyncSession) -> str:
    while True:
        code = "A" + "".join(random.choices(_CHARS, k=4))
        result = await db.execute(
            select(IncidentReport).where(IncidentReport.ref_code == code)
        )
        if result.scalar_one_or_none() is None:
            return code


async def _get_user_by_phone(phone_number: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    return result.scalar_one_or_none()


async def _create_incident_report(
    session_id: str,
    phone_number: str,
    incident_type: str,
    location: str,
    location_method: str,
    db: AsyncSession,
) -> str:
    ref_code = await _generate_ref_code(db)
    report = IncidentReport(
        session_id=session_id,
        phone_number=phone_number,
        incident_type=incident_type,
        location=location,
        location_method=location_method,
        ref_code=ref_code,
    )
    db.add(report)
    await db.commit()
    return ref_code


# ── USSD session state + handler ──────────────────────────────────────────────

# In-memory store keyed by Africa's Talking sessionId
_sessions: dict[str, dict] = {}

_MAIN_MENU = (
    "CON Welcome to SafeAlert\n"
    "1. Report Incident\n"
    "2. Check Area Safety\n"
    "3. Exit"
)
_INCIDENT_MENU = (
    "CON Incident type:\n"
    "1. Armed Robbery\n"
    "2. Kidnapping\n"
    "3. Suspicious Activity\n"
    "4. Vandalism\n"
    "5. Banditry/Terrorism\n"
    "6. Other"
)
_LOCATION_METHOD_MENU = (
    "CON Confirm your location:\n"
    "1. Use registered address\n"
    "2. Enter LGA manually"
)
_ERR_INVALID = "END Invalid input. Please dial in again."
_ERR_DB      = "END Something went wrong. Please try again shortly."


def _end_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


async def handle_ussd(
    session_id: str, phone_number: str, text: str, db: AsyncSession
) -> str:
    parts = text.split("*") if text else []

    # ── Initial dial ──────────────────────────────────────────────────────────
    if not parts:
        _sessions[session_id] = {
            "step": "main",
            "phone_number": phone_number,
            "incident_type": None,
            "location_method": None,
        }
        return _MAIN_MENU

    first = parts[0]

    # ── Option 3: Exit ────────────────────────────────────────────────────────
    if first == "3":
        _end_session(session_id)
        return "END Thank you for using SafeAlert. Stay safe."

    # ── Option 1: Report Incident ─────────────────────────────────────────────
    if first == "1":
        if len(parts) == 1:
            _sessions.setdefault(session_id, {})["step"] = "incident_type"
            return _INCIDENT_MENU

        incident_option = parts[1]
        if incident_option not in INCIDENT_TYPES:
            _end_session(session_id)
            return _ERR_INVALID

        incident_type = INCIDENT_TYPES[incident_option]

        if len(parts) == 2:
            _sessions.setdefault(session_id, {}).update(
                {"step": "location_method", "incident_type": incident_type}
            )
            return _LOCATION_METHOD_MENU

        location_choice = parts[2]

        # 1 → registered address
        if location_choice == "1":
            user = await _get_user_by_phone(phone_number, db)
            address = (user.registered_address or user.lga) if user else None

            if not address:
                if len(parts) == 3:
                    _sessions.setdefault(session_id, {}).update(
                        {"step": "manual_lga_fallback", "incident_type": incident_type}
                    )
                    return "CON No registered address found. Enter your LGA and nearest landmark:"
                lga_input = "*".join(parts[3:])
                try:
                    ref_code = await _create_incident_report(
                        session_id, phone_number, incident_type, lga_input, "manual", db
                    )
                    _end_session(session_id)
                    return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
                except Exception:
                    _end_session(session_id)
                    return _ERR_DB

            if len(parts) == 3:
                try:
                    ref_code = await _create_incident_report(
                        session_id, phone_number, incident_type, address, "registered", db
                    )
                    _end_session(session_id)
                    return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
                except Exception:
                    _end_session(session_id)
                    return _ERR_DB

        # 2 → manual LGA
        elif location_choice == "2":
            if len(parts) == 3:
                _sessions.setdefault(session_id, {}).update(
                    {"step": "enter_lga", "location_method": "manual", "incident_type": incident_type}
                )
                return "CON Enter your LGA and nearest landmark:"

            lga_input = "*".join(parts[3:])
            try:
                ref_code = await _create_incident_report(
                    session_id, phone_number, incident_type, lga_input, "manual", db
                )
                _end_session(session_id)
                return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
            except Exception:
                _end_session(session_id)
                return _ERR_DB

        _end_session(session_id)
        return _ERR_INVALID

    # ── Option 2: Check Area Safety ───────────────────────────────────────────
    if first == "2":
        if len(parts) == 1:
            _sessions.setdefault(session_id, {})["step"] = "area_location"
            return "CON Enter your location and nearest landmark:"

        location_input = "*".join(parts[1:])
        try:
            ref_code = await _create_incident_report(
                session_id, phone_number, "Area Safety Check", location_input, "manual", db
            )
            _end_session(session_id)
            return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
        except Exception:
            _end_session(session_id)
            return _ERR_DB

    _end_session(session_id)
    return _ERR_INVALID


# ── FastAPI app ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="SafeAlert USSD Service", lifespan=lifespan)


@app.post("/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
    db: AsyncSession = Depends(get_db),
) -> str:
    return await handle_ussd(
        session_id=sessionId,
        phone_number=phoneNumber,
        text=text,
        db=db,
    )


if __name__ == "__main__":
    uvicorn.run("ussd_service:app", host="0.0.0.0", port=8000, reload=True)
