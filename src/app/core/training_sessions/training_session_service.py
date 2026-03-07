from sqlmodel import Session
from src.app.core.training_sessions.exceptions import (
    TrainingSessionAlreadyExists,
    TrainingSessionNotFound,
    AbsenceAlreadyExists,
    AbsenceNotFound,
)
from src.app.core.training_sessions import crud_training_sessions
from src.app.schemas.training_sessions import TrainingSessions, Absences


def create_training_session(
    session: Session, session_create: TrainingSessions
) -> TrainingSessions:
    existing = crud_training_sessions.get_training_session_by_id(
        session, session_create.id
    )
    if existing:
        raise TrainingSessionAlreadyExists
    return crud_training_sessions.create_training_session(session, session_create)


def get_training_session(session: Session, session_id: int) -> TrainingSessions:
    session_obj = crud_training_sessions.get_training_session_by_id(session, session_id)
    if not session_obj:
        raise TrainingSessionNotFound
    return session_obj


def create_absence(session: Session, absence_create: Absences) -> Absences:
    existing = crud_training_sessions.get_absence_by_id(session, absence_create.id)
    if existing:
        raise AbsenceAlreadyExists
    return crud_training_sessions.create_absence(session, absence_create)


def get_absence(session: Session, absence_id: int) -> Absences:
    absence_obj = crud_training_sessions.get_absence_by_id(session, absence_id)
    if not absence_obj:
        raise AbsenceNotFound
    return absence_obj
