from sqlmodel import Session, select
from src.app.schemas.training_sessions import (
    SessionTraineesLink,
    TrainingSessions,
    TrainingSessionUpdate,
)


# CRUD for TrainingSessions
def write_training_session(
    session: Session, session_create: TrainingSessions
) -> TrainingSessions:
    db_obj = TrainingSessions.model_validate(session_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_training_session_by_id(
    session: Session, session_id: int
) -> TrainingSessions | None:
    statement = select(TrainingSessions).where(TrainingSessions.id == session_id)
    return session.exec(statement).first()


def get_all_training_sessions(
    session: Session, offset: int = 0, limit: int = 100
) -> list[TrainingSessions]:
    statement = select(TrainingSessions).offset(offset).limit(limit)
    return session.exec(statement).all()


def patch_training_session(
    session: Session,
    db_session: TrainingSessions,
    session_update: TrainingSessionUpdate,
) -> TrainingSessions:
    training_session_update_data = session_update.model_dump(exclude_unset=True)
    db_session.sqlmodel_update(training_session_update_data)
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


def delete_training_session(session: Session, session_id: int) -> bool:
    db_session = get_training_session_by_id(session, session_id)
    if db_session:
        session.delete(db_session)
        session.commit()
        return True
    return False


def get_training_sessions_with_filters(
    session: Session, filters: dict, offset: int = 0, limit: int = 100
) -> list[TrainingSessions]:
    """
    Fetch absences with filters.

    Args:
        session (Session): SQLModel session.
        filters (dict): Dictionary of filters where keys are column names of TrainingSessions and values are the values to filter by.
            Example: {"user_id": 123, "status": "pending"}
        offset (int): Pagination offset.
        limit (int): Pagination limit.

    Returns:
        list[TrainingSessions]: List of filtered substitution requests.

    Note:
        Only exact matches are supported. Keys must correspond to valid TrainingSessions attributes.
    """
    statement = select(TrainingSessions)
    for key, value in filters.items():
        column = getattr(TrainingSessions, key, None)
        if column is not None:
            statement = statement.where(column == value)
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def get_session_trainees_with_filters(
    session: Session, filters: dict, offset: int = 0, limit: int = 100
) -> list[SessionTraineesLink]:
    """
    Fetch session trainees with filters.

    Args:
        session (Session): SQLModel session.
        filters (dict): Dictionary of filters where keys are column names of TrainingSessionTrainees and values are the values to filter by.
            Example: {"user_id": 123, "status": "pending"}
        offset (int): Pagination offset.
        limit (int): Pagination limit.

    Returns:
        list[TrainingSessionTrainees]: List of filtered substitution requests.

    Note:
        Only exact matches are supported. Keys must correspond to valid TrainingSessionTrainees attributes.
    """
    statement = select(SessionTraineesLink)
    for key, value in filters.items():
        column = getattr(SessionTraineesLink, key, None)
        if column is not None:
            statement = statement.where(column == value)
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()
