import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    registered_address: Mapped[str | None] = mapped_column(String, nullable=True)
    lga: Mapped[str | None] = mapped_column(String, nullable=True)


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
