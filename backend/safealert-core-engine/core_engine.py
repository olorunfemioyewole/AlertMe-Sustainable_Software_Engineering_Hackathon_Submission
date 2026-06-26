import json
import os
import random
import string
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from math import atan2, cos, radians, sin, sqrt
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Float, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./safealert.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# ── Models ────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    phone_or_user_id: Mapped[str] = mapped_column(String)
    incident_type: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String)
    is_verified_reporter: Mapped[bool] = mapped_column(Boolean, default=False)
    is_authority_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    tier: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="pending")
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class DispatchLog(Base):
    __tablename__ = "dispatch_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_ref: Mapped[str] = mapped_column(String(7), index=True)
    tier: Mapped[int] = mapped_column(Integer)
    action_taken: Mapped[str] = mapped_column(String)
    score_breakdown: Mapped[str] = mapped_column(String)  # serialised JSON
    dispatched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReporterProfile(Base):
    """Credibility state for each phone/user ID. Created on first false-alarm."""
    __tablename__ = "reporter_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_or_user_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    credibility_weight: Mapped[float] = mapped_column(Float, default=1.0)
    false_alarm_count: Mapped[int] = mapped_column(Integer, default=0)
    last_penalized_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# ── In-memory config ──────────────────────────────────────────────────────────

KNOWN_HIGH_RISK_AREAS: list[str] = [
    "Zamfara", "Kaduna North", "Borno", "Sokoto", "Katsina"
]

TIER_LABELS = {
    1: "Monitoring",
    2: "Elevated Alert",
    3: "Critical — Public Alert",
}

# ── Utilities ─────────────────────────────────────────────────────────────────

_REF_CHARS = string.ascii_uppercase + string.digits


async def _gen_ref(db: AsyncSession) -> str:
    while True:
        ref = "SA" + "".join(random.choices(_REF_CHARS, k=5))
        clash = (
            await db.execute(select(Incident).where(Incident.ref == ref))
        ).scalar_one_or_none()
        if clash is None:
            return ref


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _geo_or_string_match(a: Incident, b: Incident, radius_km: float = 0.5) -> bool:
    """True if a and b are within radius_km of each other, or share a location substring."""
    if (
        a.latitude is not None and a.longitude is not None
        and b.latitude is not None and b.longitude is not None
    ):
        return _haversine_km(a.latitude, a.longitude, b.latitude, b.longitude) <= radius_km
    al = a.location.lower().strip()
    bl = b.location.lower().strip()
    return al == bl or al in bl or bl in al


def _incident_dict(inc: Incident) -> dict:
    return {
        "ref": inc.ref,
        "phone_or_user_id": inc.phone_or_user_id,
        "incident_type": inc.incident_type,
        "location": inc.location,
        "latitude": inc.latitude,
        "longitude": inc.longitude,
        "source": inc.source,
        "is_verified_reporter": inc.is_verified_reporter,
        "is_authority_confirmed": inc.is_authority_confirmed,
        "confidence_score": inc.confidence_score,
        "tier": inc.tier,
        "tier_label": TIER_LABELS.get(inc.tier, "Unknown"),
        "status": inc.status,
        "reported_at": inc.reported_at.isoformat(),
        "dispatched_at": inc.dispatched_at.isoformat() if inc.dispatched_at else None,
    }


# ── Confidence scoring ────────────────────────────────────────────────────────

_BASE_SEVERITY: dict[str, int] = {
    "banditry/terrorism": 50,
    "kidnapping": 45,
    "armed robbery": 35,
    "suspicious activity": 20,
    "vandalism": 15,
    # anything else falls through to 10
}


async def compute_score(incident: Incident, db: AsyncSession) -> dict:
    bd: dict[str, int] = {
        "base_severity": 0,
        "high_risk_area": 0,
        "nearby_reports": 0,
        "verified_reporter": 0,
        "cluster_match": 0,
        "authority_confirmed": 0,
        "reporter_credibility": 0,   # penalty for serial false alarmers
        "total": 0,
    }

    # ── Step 1: base severity ─────────────────────────────────────────────────
    bd["base_severity"] = _BASE_SEVERITY.get(incident.incident_type.lower(), 10)

    # ── Step 2a: high-risk area ───────────────────────────────────────────────
    loc_lower = incident.location.lower()
    is_high_risk = any(area.lower() in loc_lower for area in KNOWN_HIGH_RISK_AREAS)

    if not is_high_risk:
        # fallback: prior tier 2+ incident at same location in last 7 days
        seven_ago = datetime.utcnow() - timedelta(days=7)
        prior_escalated = (
            await db.execute(
                select(Incident).where(
                    Incident.ref != incident.ref,
                    Incident.tier >= 2,
                    Incident.reported_at >= seven_ago,
                )
            )
        ).scalars().all()
        is_high_risk = any(_geo_or_string_match(p, incident) for p in prior_escalated)

    if is_high_risk:
        bd["high_risk_area"] = 15

    # ── Step 2b: 3+ distinct reporters, same type, same location, last 60 min ─
    sixty_ago = datetime.utcnow() - timedelta(minutes=60)
    same_type_recent = (
        await db.execute(
            select(Incident).where(
                Incident.ref != incident.ref,
                Incident.incident_type == incident.incident_type,
                Incident.reported_at >= sixty_ago,
            )
        )
    ).scalars().all()

    # collect distinct reporters for incidents that are geographically/string matched
    corroborating_reporters = {
        r.phone_or_user_id
        for r in same_type_recent
        if _geo_or_string_match(r, incident)
    }
    corroborating_reporters.add(incident.phone_or_user_id)  # include self

    if len(corroborating_reporters) >= 3:
        bd["nearby_reports"] = 20

    # ── Step 2c: verified reporter ────────────────────────────────────────────
    if incident.is_verified_reporter:
        bd["verified_reporter"] = 10

    # ── Step 2d: active cluster match (any active incident nearby, any type) ──
    active_others = (
        await db.execute(
            select(Incident).where(
                Incident.ref != incident.ref,
                Incident.status == "active",
            )
        )
    ).scalars().all()

    if any(_geo_or_string_match(a, incident) for a in active_others):
        bd["cluster_match"] = 15

    # ── Step 3: authority confirmation ────────────────────────────────────────
    if incident.is_authority_confirmed:
        bd["authority_confirmed"] = 20

    # ── Step 4: reporter credibility penalty ──────────────────────────────────
    profile = (
        await db.execute(
            select(ReporterProfile).where(
                ReporterProfile.phone_or_user_id == incident.phone_or_user_id
            )
        )
    ).scalar_one_or_none()

    if profile is not None:
        w = profile.credibility_weight
        if w < 0.5:
            bd["reporter_credibility"] = -15  # chronic false alarmer
        elif w < 0.8:
            bd["reporter_credibility"] = -5   # below-average credibility

    # ── Step 5: cap at 100, floor at 0 ───────────────────────────────────────
    raw = sum(v for k, v in bd.items() if k != "total")
    bd["total"] = max(0, min(raw, 100))

    return bd


# ── Dispatch ──────────────────────────────────────────────────────────────────

async def run_dispatch(incident: Incident, breakdown: dict, db: AsyncSession) -> str:
    score = breakdown["total"]
    tier = 3 if score >= 80 else (2 if score >= 40 else 1)

    incident.tier = tier
    incident.confidence_score = float(score)
    incident.dispatched_at = datetime.utcnow()

    if tier == 1:
        incident.status = "pending"
        action = "Incident visible on operator dashboard. Monitoring."

    elif tier == 2:
        incident.status = "active"
        action = "Nearest patrol unit notified. High confidence incident."
        print(
            f"\n╔═ DISPATCH [TIER 2] ════════════════════════════════"
            f"\n║  Ref      : {incident.ref}"
            f"\n║  Type     : {incident.incident_type}"
            f"\n║  Location : {incident.location}"
            f"\n║  Score    : {score}"
            f"\n╚═ ► Notifying nearest patrol unit ══════════════════\n"
        )

    else:  # tier 3
        incident.status = "active"
        action = "PUBLIC ALERT ISSUED. Emergency response triggered."
        print(
            f"\n╔═ ⚠  PUBLIC ALERT [TIER 3] ══════════════════════════"
            f"\n║  Ref      : {incident.ref}"
            f"\n║  Type     : {incident.incident_type}"
            f"\n║  Location : {incident.location}"
            f"\n║  Score    : {score}"
            f"\n║  ► Emergency response triggered"
            f"\n║  ► Drone surveillance optional asset — deploy if available."
            f"\n╚════════════════════════════════════════════════════\n"
        )

    log_entry = DispatchLog(
        incident_ref=incident.ref,
        tier=tier,
        action_taken=action,
        score_breakdown=json.dumps(breakdown),
        dispatched_at=datetime.utcnow(),
    )
    db.add(log_entry)
    await db.flush()
    return action


# ── Community broadcast ───────────────────────────────────────────────────────

async def _broadcast_alert(incident: Incident, db: AsyncSession) -> None:
    """Print + log a community notification for a Tier 3 incident."""
    print(
        f"\n╔═ 📢  COMMUNITY BROADCAST [TIER 3] ══════════════════════"
        f"\n║  Ref      : {incident.ref}"
        f"\n║  Type     : {incident.incident_type}"
        f"\n║  Location : {incident.location}"
        f"\n║  Score    : {incident.confidence_score}"
        f"\n║  ► Notifying all registered community members."
        f"\n║  [TODO] FCM push notification → registered devices"
        f"\n║  [TODO] Africa's Talking SMS blast → community contacts"
        f"\n╚════════════════════════════════════════════════════════\n"
    )
    log_entry = DispatchLog(
        incident_ref=incident.ref,
        tier=3,
        action_taken="COMMUNITY BROADCAST SENT",
        score_breakdown=json.dumps(
            {"note": "public broadcast triggered", "score": incident.confidence_score}
        ),
        dispatched_at=datetime.utcnow(),
    )
    db.add(log_entry)
    await db.flush()


# ── DB session dependency ─────────────────────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class IncidentCreateRequest(BaseModel):
    phone_or_user_id: str
    incident_type: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str  # "ussd" | "app"
    is_verified_reporter: bool = False


class HighRiskAreasRequest(BaseModel):
    areas: list[str]


class BroadcastRequest(BaseModel):
    ref: str


class OfficerActionRequest(BaseModel):
    officer_id: str


class DowngradeRequest(BaseModel):
    officer_id: str
    target_tier: int


_TERMINAL_STATUSES = {"resolved", "false_alarm"}

# ── App setup ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="SafeAlert Core Engine", version="1.0.0", lifespan=lifespan)


# ── POST /incidents/create ────────────────────────────────────────────────────

@app.post("/incidents/create")
async def create_incident(body: IncidentCreateRequest, db: AsyncSession = Depends(get_db)):
    ref = await _gen_ref(db)

    incident = Incident(
        ref=ref,
        phone_or_user_id=body.phone_or_user_id,
        incident_type=body.incident_type,
        location=body.location,
        latitude=body.latitude,
        longitude=body.longitude,
        source=body.source,
        is_verified_reporter=body.is_verified_reporter,
    )
    db.add(incident)
    await db.flush()  # write row so scoring queries can see peer incidents

    breakdown = await compute_score(incident, db)
    action = await run_dispatch(incident, breakdown, db)
    await db.commit()
    await db.refresh(incident)

    return {
        "ref": incident.ref,
        "confidence_score": incident.confidence_score,
        "tier": incident.tier,
        "tier_label": TIER_LABELS[incident.tier],
        "score_breakdown": breakdown,
        "status": incident.status,
        "action_taken": action,
    }


# ── GET /incidents/nearby ─────────────────────────────────────────────────────

@app.get("/incidents/nearby")
async def nearby_incidents(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: float = 5.0,
    location: Optional[str] = None,   # used for string match when lat/lng absent
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(Incident).where(Incident.status.in_(["active", "pending"]))
        )
    ).scalars().all()

    if lat is not None and lng is not None:
        results = [
            inc for inc in rows
            if inc.latitude is not None
            and inc.longitude is not None
            and _haversine_km(lat, lng, inc.latitude, inc.longitude) <= radius_km
        ]
    elif location:
        loc_lower = location.lower().strip()
        results = [
            inc for inc in rows
            if loc_lower in inc.location.lower() or inc.location.lower() in loc_lower
        ]
    else:
        results = rows

    return {"count": len(results), "incidents": [_incident_dict(i) for i in results]}


# ── GET /incidents/area-safety ────────────────────────────────────────────────

@app.get("/incidents/area-safety")
async def area_safety(location: str, db: AsyncSession = Depends(get_db)):
    loc_lower = location.lower().strip()
    active = (
        await db.execute(select(Incident).where(Incident.status == "active"))
    ).scalars().all()

    matches = [
        inc for inc in active
        if loc_lower in inc.location.lower() or inc.location.lower() in loc_lower
    ]
    max_score = max((inc.confidence_score for inc in matches), default=0.0)

    # spec: 0-39=LOW, 40-79=MODERATE, 80-99=HIGH, 100=CRITICAL
    if max_score >= 100:
        level = "CRITICAL"
    elif max_score >= 80:
        level = "HIGH"
    elif max_score >= 40:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "location": location,
        "active_incidents": len(matches),
        "confidence_level": level,
        "max_confidence_score": max_score,
    }


# ── GET /alerts/active ────────────────────────────────────────────────────────

@app.get("/alerts/active")
async def active_alerts(db: AsyncSession = Depends(get_db)):
    results = (
        await db.execute(
            select(Incident).where(
                Incident.tier >= 3,
                Incident.status == "active",
            )
        )
    ).scalars().all()

    return {"count": len(results), "alerts": [_incident_dict(i) for i in results]}


# ── PATCH /incidents/confirm/{ref} ───────────────────────────────────────────

@app.patch("/incidents/confirm/{ref}")
async def confirm_incident(ref: str, db: AsyncSession = Depends(get_db)):
    incident = (
        await db.execute(select(Incident).where(Incident.ref == ref))
    ).scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{ref}' not found")
    if incident.status in _TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Incident '{ref}' is already {incident.status}")

    old_tier = incident.tier
    incident.is_authority_confirmed = True
    await db.flush()

    breakdown = await compute_score(incident, db)
    action = await run_dispatch(incident, breakdown, db)

    incident.status = "confirmed"  # officer physically confirmed on ground

    if incident.tier == 3 and old_tier < 3:
        await _broadcast_alert(incident, db)

    await db.commit()
    await db.refresh(incident)

    return {
        **_incident_dict(incident),
        "score_breakdown": breakdown,
        "action_taken": action,
    }


# ── POST /alerts/broadcast ────────────────────────────────────────────────────

@app.post("/alerts/broadcast")
async def broadcast_alert(body: BroadcastRequest, db: AsyncSession = Depends(get_db)):
    incident = (
        await db.execute(select(Incident).where(Incident.ref == body.ref))
    ).scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{body.ref}' not found")

    if incident.tier < 3:
        raise HTTPException(
            status_code=400,
            detail=f"Broadcast only allowed for Tier 3 incidents (current tier: {incident.tier})",
        )

    await _broadcast_alert(incident, db)
    await db.commit()

    return {
        "ref": incident.ref,
        "status": "broadcast_sent",
        "message": f"Community notification dispatched for incident {incident.ref}",
    }


# ── GET /incidents/dashboard ──────────────────────────────────────────────────

@app.get("/incidents/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    incidents = (
        await db.execute(
            select(Incident).where(Incident.status.in_(["active", "pending", "confirmed"]))
        )
    ).scalars().all()

    incidents_sorted = sorted(incidents, key=lambda i: i.confidence_score, reverse=True)

    results = []
    for inc in incidents_sorted:
        latest_log = (
            await db.execute(
                select(DispatchLog)
                .where(DispatchLog.incident_ref == inc.ref)
                .order_by(DispatchLog.dispatched_at.desc())
            )
        ).scalars().first()

        entry = _incident_dict(inc)
        entry["score_breakdown"] = (
            json.loads(latest_log.score_breakdown) if latest_log else {}
        )
        results.append(entry)

    return {"count": len(results), "incidents": results}


# ── PATCH /incidents/{ref}/resolve ───────────────────────────────────────────

@app.patch("/incidents/{ref}/resolve")
async def resolve_incident(ref: str, body: OfficerActionRequest, db: AsyncSession = Depends(get_db)):
    incident = (
        await db.execute(select(Incident).where(Incident.ref == ref))
    ).scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{ref}' not found")
    if incident.status in _TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Incident '{ref}' is already {incident.status}")

    incident.status = "resolved"

    log_entry = DispatchLog(
        incident_ref=incident.ref,
        tier=incident.tier,
        action_taken=f"RESOLVED by officer {body.officer_id}. Incident cleared.",
        score_breakdown=json.dumps({
            "officer_id": body.officer_id,
            "resolved_at": datetime.utcnow().isoformat(),
            "final_score": incident.confidence_score,
        }),
        dispatched_at=datetime.utcnow(),
    )
    db.add(log_entry)

    await db.commit()
    await db.refresh(incident)

    return {
        **_incident_dict(incident),
        "resolved_by": body.officer_id,
        "resolved_at": log_entry.dispatched_at.isoformat(),
    }


# ── PATCH /incidents/{ref}/false-alarm ───────────────────────────────────────

@app.patch("/incidents/{ref}/false-alarm")
async def mark_false_alarm(ref: str, body: OfficerActionRequest, db: AsyncSession = Depends(get_db)):
    incident = (
        await db.execute(select(Incident).where(Incident.ref == ref))
    ).scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{ref}' not found")
    if incident.status in _TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Incident '{ref}' is already {incident.status}")

    # Collect every reporter who corroborated within 60 min of the original report
    window_start = incident.reported_at - timedelta(minutes=5)   # small backslide for clock skew
    window_end = incident.reported_at + timedelta(minutes=60)
    corroborators = (
        await db.execute(
            select(Incident).where(
                Incident.ref != incident.ref,
                Incident.incident_type == incident.incident_type,
                Incident.reported_at >= window_start,
                Incident.reported_at <= window_end,
            )
        )
    ).scalars().all()

    contributor_ids: set[str] = {
        r.phone_or_user_id
        for r in corroborators
        if _geo_or_string_match(r, incident)
    }
    contributor_ids.add(incident.phone_or_user_id)

    # Apply credibility penalty — farming false alarms becomes self-defeating
    PENALTY = 0.3
    FLOOR = 0.1
    penalized = []

    for uid in contributor_ids:
        profile = (
            await db.execute(
                select(ReporterProfile).where(ReporterProfile.phone_or_user_id == uid)
            )
        ).scalar_one_or_none()

        if profile is None:
            profile = ReporterProfile(phone_or_user_id=uid)
            db.add(profile)
            await db.flush()

        old_weight = profile.credibility_weight
        profile.credibility_weight = round(max(FLOOR, old_weight - PENALTY), 3)
        profile.false_alarm_count += 1
        profile.last_penalized_at = datetime.utcnow()
        penalized.append({
            "phone_or_user_id": uid,
            "old_weight": old_weight,
            "new_weight": profile.credibility_weight,
            "false_alarm_count": profile.false_alarm_count,
        })

    incident.status = "false_alarm"

    log_entry = DispatchLog(
        incident_ref=incident.ref,
        tier=incident.tier,
        action_taken=(
            f"FALSE ALARM — confirmed by officer {body.officer_id}. "
            f"Credibility penalty applied to {len(contributor_ids)} reporter(s)."
        ),
        score_breakdown=json.dumps({
            "officer_id": body.officer_id,
            "penalized_reporters": penalized,
        }),
        dispatched_at=datetime.utcnow(),
    )
    db.add(log_entry)

    await db.commit()
    await db.refresh(incident)

    return {
        **_incident_dict(incident),
        "penalized_reporters": penalized,
        "action_taken": log_entry.action_taken,
    }


# ── PATCH /incidents/{ref}/downgrade ─────────────────────────────────────────

@app.patch("/incidents/{ref}/downgrade")
async def downgrade_incident(ref: str, body: DowngradeRequest, db: AsyncSession = Depends(get_db)):
    incident = (
        await db.execute(select(Incident).where(Incident.ref == ref))
    ).scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{ref}' not found")
    if incident.status in _TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Incident '{ref}' is already {incident.status}")
    if body.target_tier >= incident.tier:
        raise HTTPException(
            status_code=400,
            detail=f"target_tier ({body.target_tier}) must be lower than current tier ({incident.tier})",
        )
    if body.target_tier < 1:
        raise HTTPException(status_code=400, detail="target_tier must be >= 1")

    old_tier = incident.tier
    incident.tier = body.target_tier

    log_entry = DispatchLog(
        incident_ref=incident.ref,
        tier=body.target_tier,
        action_taken=(
            f"DOWNGRADED Tier {old_tier} → Tier {body.target_tier} "
            f"by officer {body.officer_id}. "
            f"{TIER_LABELS.get(body.target_tier, 'Unknown')}."
        ),
        score_breakdown=json.dumps({
            "officer_id": body.officer_id,
            "previous_tier": old_tier,
            "new_tier": body.target_tier,
            "score_at_downgrade": incident.confidence_score,
        }),
        dispatched_at=datetime.utcnow(),
    )
    db.add(log_entry)

    await db.commit()
    await db.refresh(incident)

    return {
        **_incident_dict(incident),
        "previous_tier": old_tier,
        "downgraded_by": body.officer_id,
        "action_taken": log_entry.action_taken,
    }


# ── POST /admin/set-high-risk-areas ──────────────────────────────────────────

@app.post("/admin/set-high-risk-areas")
async def set_high_risk_areas(body: HighRiskAreasRequest):
    global KNOWN_HIGH_RISK_AREAS
    KNOWN_HIGH_RISK_AREAS = body.areas
    return {"status": "updated", "high_risk_areas": KNOWN_HIGH_RISK_AREAS}


# ── Startup ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("core_engine:app", host="0.0.0.0", port=8002, reload=True)
