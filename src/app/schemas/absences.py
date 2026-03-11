from datetime import datetime
from typing import Literal

from sqlmodel import AutoString, Field, SQLModel


class AbsenceBase(SQLModel):
    training_session_id: int = Field(
        primary_key=True, foreign_key="training_sessions.id"
    )
    trainee_id: int = Field(primary_key=True, foreign_key="user_accounts.id")
    absence_date: datetime = Field(
        primary_key=True, description="Date for the absence, e.g. 2026-01-10"
    )
    status: Literal["pending", "confirmed"] = Field(
        default="pending", sa_type=AutoString
    )
    created_at: datetime = Field(default_factory=datetime.now)


class Absences(AbsenceBase, table=True): ...


class AbsenceCreate(AbsenceBase):
    absence_date: datetime | None = None  # Defaults to next upcoming session day


class AbsenceUpdate(SQLModel):
    status: Literal["pending", "confirmed"] | None = None
