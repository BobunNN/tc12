from datetime import datetime
from typing import Literal

from sqlmodel import AutoString, Field, SQLModel


class SubstitutionRequests(SQLModel, table=True):
    __tablename__ = "substition_requests"
    session_id: int = Field(primary_key=True, foreign_key="training_sessions.id")
    absence_date: datetime = Field(
        primary_key=True, description="Date for the absence, e.g. 2026-01-10"
    )
    requester_id: int = Field(primary_key=True, foreign_key="user_accounts.id")
    status: Literal["pending", "approved", "rejected"] = Field(
        default="pending", sa_type=AutoString
    )
    reviewed_at: datetime
    created_at: datetime
