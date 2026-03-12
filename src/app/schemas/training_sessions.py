from typing import Optional

from typing_extensions import Literal
from datetime import datetime, time, timedelta
from sqlmodel import AutoString, Field, SQLModel


class TrainingSessionBase(SQLModel):
    day: Literal[0, 1, 2, 3, 4, 5, 6] = Field(default=None, sa_type=AutoString)
    trainer_id: int | None = Field(default=None, foreign_key="user_accounts.id")
    session_start: time = Field(default=time(hour=10), description="e.g., 19:15")
    session_duration: int = Field(default=60, description="Session duration in MINUTES")
    location: Literal["Leo Lagrange", "Alain Mimoun", "La Faluère", "Carnot"] = Field(
        default=None, sa_type=AutoString
    )
    court_number: int

    @property
    def end_time(self) -> time:
        """Calculates the end time based on start time and duration."""
        start_dt = datetime.combine(datetime.today(), self.session_start)
        end_dt = start_dt + timedelta(minutes=self.session_duration)
        return end_dt.time()

    def overlaps_with(self, other: "TrainingSessions") -> bool:
        """Method to check if this session overlaps with another."""

        return (
            self.end_time > other.session_start and self.session_start < other.end_time
        )


class TrainingSessions(TrainingSessionBase, table=True):
    __tablename__ = "training_sessions"
    id: int | None = Field(default=None, primary_key=True, index=True, nullable=False)


class TrainingSessionUpdate(TrainingSessionBase):
    day: Literal[0, 1, 2, 3, 4, 5, 6, None] = Field(default=None, sa_type=AutoString)
    trainer_id: Optional[int] | None = None
    session_start: Optional[time] | None = time(hour=10)
    session_duration: Optional[int] | None = 60
    location: Literal["Leo Lagrange", "Alain Mimoun", "La Faluère", "Carnot", None] = (
        Field(default=None, sa_type=AutoString)
    )
    court_number: Optional[int] | None = None


class TrainingSessionCreate(TrainingSessionBase):
    pass


class SessionTraineesLink(SQLModel, table=True):
    __tablename__ = "training_session_trainees"
    training_session_id: int = Field(
        foreign_key="training_sessions.id", primary_key=True
    )
    trainee_id: int = Field(foreign_key="user_accounts.id", primary_key=True)
