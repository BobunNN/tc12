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


def update_training_session(
    session: Session,
    session_id: int,
    session_update: dict,
) -> TrainingSessions:
    db_session = crud_training_sessions.get_training_session_by_id(session, session_id)
    if not db_session:
        raise TrainingSessionNotFound
    return crud_training_sessions.update_training_session(
        session, db_session, session_update
    )


def delete_training_session(
    session: Session,
    session_id: int,
) -> dict:
    success = crud_training_sessions.delete_training_session(session, session_id)
    if not success:
        raise TrainingSessionNotFound
    return {"detail": "Deleted successfully"}


def bulk_load_training_sessions(session: Session, records: list[dict]) -> dict:
    loaded = []
    errors = []
    for record in records:
        try:
            session_obj = TrainingSessions.model_validate(record)
            existing = crud_training_sessions.get_training_session_by_id(
                session, session_obj.id
            )
            if existing:
                continue
            crud_training_sessions.create_training_session(session, session_obj)
            loaded.append(session_obj)
        except Exception as e:
            errors.append({"record": record, "error": str(e)})
    return {"loaded_count": len(loaded), "errors": errors}
