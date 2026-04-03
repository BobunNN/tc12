from datetime import datetime, date
from typing import Literal

from sqlmodel import AutoString, Field, SQLModel


class AbsenceBase(SQLModel):
    training_session_id: int = Field(
        primary_key=True, foreign_key="training_sessions.id"
    )
    trainee_id: int = Field(primary_key=True, foreign_key="user_accounts.id")
    absence_date: date = Field(
        primary_key=True, description="Date for the absence, e.g. 2026-01-10"
    )
    status: Literal["pending", "confirmed"] = Field(
        default="pending", sa_type=AutoString
    )


class Absences(AbsenceBase, table=True):
    created_at: datetime = Field(default_factory=datetime.now)


class AbsenceCreate(AbsenceBase): ...


class AbsenceUpdate(SQLModel):
    status: Literal["pending", "confirmed"] | None = None


class AbsencePublic(AbsenceBase): ...
