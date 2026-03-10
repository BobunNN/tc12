from datetime import datetime

from sqlmodel import Session
from src.app.core.absences.exceptions import AbsenceNotFound
from src.app.core.training_sessions.training_session_service import (
    search_training_session,
    search_session_trainees,
)
from src.app.schemas.training_sessions import Absences
from src.app.schemas.user import User

from .crud_absences import (
    create_absence,
    get_unique_absence_by_ckey,
    get_all_absences,
    delete_absence,
    get_absences_with_filters,
)


def create_absence_service(
    session: Session, absence_create: Absences, user: User
) -> Absences:
    if user.is_trainer:
        ...
    else:
        session_filters = {"trainee_id": user.id}
        user_session = search_session_trainees(session=session, filters=session_filters)
    return create_absence(session, absence_create)


def search_unique_absence(
    session: Session, trainee_id: int, training_id: int, training_date: datetime
) -> Absences:
    absence = get_unique_absence_by_ckey(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=training_date,
    )
    if not absence:
        raise AbsenceNotFound
    return absence


def get_all_absences_service(session: Session) -> list[Absences]:
    return get_all_absences(session)


def delete_absence_service(session: Session, absence_id: int) -> bool:
    return delete_absence(session, absence_id)


def get_self_absences(session: Session, current_user: User):
    if current_user.is_trainer:
        ...
    else:
        filters = {"traineed_id": current_user.id}
        return get_absences_with_filters(session=session, filters=filters)
