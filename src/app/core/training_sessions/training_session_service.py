from datetime import datetime, time, timedelta
from typing import Any

from sqlmodel import Session
from src.app.core.training_sessions.exceptions import (
    TrainingSessionAlreadyExists,
    TrainingSessionInvalidTrainer,
    TrainingSessionNotFound,
    TrainingSessionOverlap,
)

from src.app.core.training_sessions.crud_training_sessions import (
    get_all_training_sessions,
    get_session_trainees_with_filters,
    get_training_session_by_id,
    get_training_sessions_with_filters,
    write_training_session,
    patch_training_session,
    delete_training_session,
)
from src.app.core.users.user_service import check_is_trainer
from src.app.schemas.training_sessions import (
    TrainingSessionTrainees,
    TrainingSessions,
    TrainingSessionsUpdate,
)
from src.app.schemas.user import User


def create_training_session(
    session: Session, session_create: TrainingSessions
) -> TrainingSessions:
    existing = get_training_session_by_id(session, session_create.id)
    if existing:
        raise TrainingSessionAlreadyExists

    if check_sessions_overlap(session, session_create):
        raise TrainingSessionOverlap

    if not check_is_trainer(session, session_create.trainer_id):
        raise TrainingSessionInvalidTrainer

    return write_training_session(session, session_create)


def check_sessions_overlap(
    session: Session,
    session_create: TrainingSessions,
) -> bool:
    filters = {
        "location": session_create.location,
        "court_number": session_create.court_number,
        "day": session_create.day,
    }

    potential_overlaps: list[TrainingSessions] = get_training_sessions_with_filters(
        session, filters
    )

    if isinstance(session_create.session_start, str):
        new_start = datetime.strptime(session_create.session_start, "%H:%M:%S").time()
    elif isinstance(session_create.session_start, time):
        new_start = session_create.session_start

    new_end = (
        datetime.combine(datetime.today(), new_start)
        + timedelta(minutes=session_create.session_duration)
    ).time()

    for s in potential_overlaps:
        existing_start = s.session_start
        existing_end = (
            datetime.combine(datetime.today(), existing_start)
            + timedelta(minutes=s.session_duration)
        ).time()
        if new_start < existing_end and new_end > existing_start:
            return True

    return False


def get_training_session(session: Session, session_id: int) -> TrainingSessions:
    session_obj = get_training_session_by_id(session, session_id)
    if not session_obj:
        raise TrainingSessionNotFound
    return session_obj


def get_self_training_session(session: Session, user: User) -> list[TrainingSessions]:
    if user.is_trainer:
        search_filters = {"trainer_id": user.id}
        return get_training_sessions_with_filters(
            session=session, filters=search_filters
        )
    else:
        trainees_search_filter = {"trainee_id": user.id}
        user_sessions: list[TrainingSessionTrainees] = (
            get_session_trainees_with_filters(
                session=session, filters=trainees_search_filter
            )
        )
        sessions = []
        for user_session in user_sessions:
            training_session_search_filters = {"id": user_session.training_session_id}
            sessions.extend(
                get_training_sessions_with_filters(
                    session=session, filters=training_session_search_filters
                )
            )

        return sessions


def get_all_training_session(session: Session) -> list[TrainingSessions]:
    sessions = get_all_training_sessions(session=session)
    return sessions


def update_training_session(
    session: Session,
    session_id: int,
    session_update: TrainingSessionsUpdate,
) -> TrainingSessions:
    db_session = get_training_session_by_id(session, session_id)
    if not db_session:
        raise TrainingSessionNotFound

    update_data = db_session.model_dump()
    update_fields = session_update.model_dump(exclude_unset=True)
    update_data.update(update_fields)
    merged_session = TrainingSessions(**update_data)

    if check_sessions_overlap(session, merged_session):
        raise TrainingSessionOverlap

    return patch_training_session(session, db_session, session_update)


def remove_training_session(
    session: Session,
    session_id: int,
) -> Any:
    success = delete_training_session(session, session_id)
    if not success:
        raise TrainingSessionNotFound
    return {"detail": "Deleted successfully"}


def search_training_session(session: Session, session_id: int) -> TrainingSessions:
    search_filter = {"id": session_id}
    return get_training_sessions_with_filters(session=session, filters=search_filter)


def search_session_trainees(
    session: Session, session_id: int
) -> list[TrainingSessionTrainees]:
    search_filter = {"training_session_id": session_id}
    return get_session_trainees_with_filters(session=session, filters=search_filter)


def bulk_load_training_sessions(session: Session, records: list[dict]) -> Any:
    loaded = []
    errors = []
    for record in records:
        try:
            session_obj = TrainingSessions.model_validate(record)
            existing = get_training_session_by_id(session, session_obj.id)
            if existing:
                continue
            create_training_session(session, session_obj)
            loaded.append(session_obj)
        except Exception as e:
            errors.append({"record": record, "error": str(e)})
    return {"loaded_count": len(loaded), "errors": errors}
