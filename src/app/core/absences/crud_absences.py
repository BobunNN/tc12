from datetime import datetime
from sqlmodel import Session, select
from src.app.schemas.training_sessions import Absences


def create_absence(session: Session, absence_create: Absences) -> Absences:
    db_obj = Absences.model_validate(absence_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_unique_absence_by_ckey(
    session: Session, trainee_id: int, training_id: int, training_date: datetime
) -> Absences | None:
    statement = (
        select(Absences)
        .where(Absences.training_session_id == training_id)
        .where(trainee_id == trainee_id)
        .where(training_date == training_date)
    )
    return session.exec(statement).first()


def get_all_absences(
    session: Session, offset: int = 0, limit: int = 100
) -> list[Absences]:
    statement = select(Absences).offset(offset).limit(limit)
    return session.exec(statement).all()


def delete_absence(session: Session, absence_id: int) -> bool:
    db_absence = get_unique_absence_by_ckey(session, absence_id)
    if db_absence:
        session.delete(db_absence)
        session.commit()
        return True
    return False


def get_absences_with_filters(
    session: Session, filters: dict, offset: int = 0, limit: int = 100
) -> list[Absences]:
    """
    Fetch absences with filters.

    Args:
        session (Session): SQLModel session.
        filters (dict): Dictionary of filters where keys are column names of SubstitutionRequests and values are the values to filter by.
            Example: {"user_id": 123, "status": "pending"}
        offset (int): Pagination offset.
        limit (int): Pagination limit.

    Returns:
        list[SubstitutionRequests]: List of filtered substitution requests.

    Note:
        Only exact matches are supported. Keys must correspond to valid SubstitutionRequests attributes.
    """
    statement = select(Absences)
    for key, value in filters.items():
        column = getattr(Absences, key, None)
        if column is not None:
            statement = statement.where(column == value)
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()
