from datetime import datetime
from sqlmodel import Session, select
from src.app.schemas.absences import Absences, AbsenceCreate


def create_absence(session: Session, absence_create: AbsenceCreate) -> Absences:
    db_obj = Absences(
        training_session_id=absence_create.training_session_id,
        trainee_id=absence_create.trainee_id,
        absence_date=absence_create.absence_date,
        status=absence_create.status,
    )
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
        .where(Absences.trainee_id == trainee_id)
        .where(Absences.absence_date == training_date)
    )
    return session.exec(statement).first()


def get_all_absences(
    session: Session, offset: int = 0, limit: int = 100
) -> list[Absences]:
    statement = select(Absences).offset(offset).limit(limit)
    return session.exec(statement).all()


def delete_absence(
    session: Session, trainee_id: int, training_id: int, training_date: datetime
) -> bool:
    db_absence = get_unique_absence_by_ckey(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=training_date,
    )
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
        filters (dict): Dictionary of filters where keys are column names of Absences
            and values are the values to filter by.
            Example: {"trainee_id": 123, "status": "pending"}
        offset (int): Pagination offset.
        limit (int): Pagination limit.

    Returns:
        list[Absences]: List of filtered absences.
    """
    statement = select(Absences)
    for key, value in filters.items():
        column = getattr(Absences, key, None)
        if column is not None:
            statement = statement.where(column == value)
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()
