from datetime import datetime
from typing import Literal

from sqlalchemy import UniqueConstraint
from sqlmodel import AutoString, Field, SQLModel


class SubstitutionRequestsBase(SQLModel):
    session_id: int = Field(foreign_key="training_sessions.id")
    absence_date: datetime = Field(description="Date for the absence, e.g. 2026-01-10")
    requester_id: int = Field(foreign_key="user_accounts.id")
    status: Literal["pending", "approved", "rejected"] = Field(
        default="pending", sa_type=AutoString
    )
    reviewed_at: datetime = Field(default_factory=datetime.now)


class SubstitutionRequests(SubstitutionRequestsBase, table=True):
    __tablename__ = "substition_requests"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "absence_date",
            "requester_id",
            name="uq_substitution_request",
        ),
    )
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class SubstitutionRequestCreate(SQLModel):
    session_id: int
    absence_date: datetime
    requester_id: int
    status: Literal["pending", "approved", "rejected"] = "pending"
    created_at: datetime | None = Field(default_factory=datetime.now)
    reviewed_at: datetime | None = Field(default_factory=datetime.now)


class SubstitutionRequestUpdate(SQLModel):
    status: Literal["pending", "approved", "rejected"] | None = None
    reviewed_at: datetime | None = None


class SubstitutionRequestsPublic(SubstitutionRequestsBase): ...
