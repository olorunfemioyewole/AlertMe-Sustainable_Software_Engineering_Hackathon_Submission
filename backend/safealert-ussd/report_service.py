import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, IncidentReport

INCIDENT_TYPES: dict[str, str] = {
    "1": "Armed Robbery",
    "2": "Kidnapping",
    "3": "Suspicious Activity",
    "4": "Vandalism",
    "5": "Banditry/Terrorism",
    "6": "Other",
}

_CHARS = string.ascii_uppercase + string.digits


async def generate_ref_code(db: AsyncSession) -> str:
    while True:
        code = "A" + "".join(random.choices(_CHARS, k=4))
        result = await db.execute(
            select(IncidentReport).where(IncidentReport.ref_code == code)
        )
        if result.scalar_one_or_none() is None:
            return code


async def get_user_by_phone(phone_number: str, db: AsyncSession) -> User | None:
    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )
    return result.scalar_one_or_none()


async def create_incident_report(
    session_id: str,
    phone_number: str,
    incident_type: str,
    location: str,
    location_method: str,
    db: AsyncSession,
) -> str:
    ref_code = await generate_ref_code(db)
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
