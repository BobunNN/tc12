from typing_extensions import Literal
from datetime import time, datetime
from sqlmodel import AutoString, Field, SQLModel
from typing import Optional


class TrainingSessions(SQLModel, table=True):
    __tablename__ = "training_sessions"
    id: int | None = Field(default=None, primary_key=True, index=True, nullable=False)
    day: Literal[1, 2, 3, 4, 5, 6, 7] = Field(default=None, sa_type=AutoString)
    trainer_id: int | None = Field(default=None, foreign_key="user_accounts.id")
    session_start: time = Field(default=time(hour=10), description="e.g., 19:15")
    session_duration: int = Field(default=60, description="Session duration in MINUTES")
    location: Literal["Leo Lagrange", "Alain Mimoun", "La Faluère", "Carnot"] = Field(
        default=None, sa_type=AutoString
    )
    court_number: int


class TrainingSessionsUpdate(SQLModel):
    day: Optional[Literal[1, 2, 3, 4, 5, 6, 7]] = None
    trainer_id: Optional[int] = None
    session_start: Optional[time] = None
    session_duration: Optional[int] = None
    location: Optional[
        Literal["Leo Lagrange", "Alain Mimoun", "La Faluère", "Carnot"]
    ] = None
    court_number: Optional[int] = None


class TrainingSessionTrainees(SQLModel, table=True):
    __tablename__ = "training_session_trainees"
    training_session_id: int = Field(
        foreign_key="training_sessions.id", primary_key=True
    )
    trainee_id: int = Field(foreign_key="user_accounts.id", primary_key=True)


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
