from datetime import datetime
from typing import Literal

from sqlmodel import AutoString, Field, SQLModel


class Absences(SQLModel, table=True):
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
    created_at: datetime
