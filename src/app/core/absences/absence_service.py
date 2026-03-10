from datetime import datetime

from sqlmodel import Session
from src.app.core.absences.exceptions import (
    AbsenceDateMismatchSessionDay,
    AbsenceNotFound,
    AbsenceTraineeIdMismatch,
    TraineeNotRegisteredForSession,
    TrainerDoesNotManageTrainingSession,
)
from src.app.core.training_sessions.training_session_service import (
    get_training_session,
    search_session_trainees,
)
from src.app.schemas.training_sessions import (
    SessionTraineesLink,
    TrainingSessions,
)
from src.app.schemas.absences import Absences
from src.app.schemas.user import User

from src.app.core.absences.crud_absences import (
    create_absence,
    get_unique_absence_by_ckey,
    get_all_absences,
    delete_absence,
    get_absences_with_filters,
)


def open_absence_slot(
    session: Session, absence_create: Absences, user: User
) -> Absences:
    print("COUCOU")
    print(type(absence_create.absence_date))
    if not session_absence_date_validation(session, absence_create):
        raise AbsenceDateMismatchSessionDay

    if user.is_trainer:
        training_session: TrainingSessions = get_training_session(
            session=session, session_id=absence_create.training_session_id
        )
        if training_session.trainer_id != user.id:
            raise TrainerDoesNotManageTrainingSession

        session_filters = {"trainee_id": user.id}
        user_sessions: list[SessionTraineesLink] = search_session_trainees(
            session=session, filters=session_filters
        )
        user_training_ids = [ts.training_session_id for ts in user_sessions]
        if absence_create.training_session_id not in user_training_ids:
            raise TraineeNotRegisteredForSession

    else:
        if not (absence_create.trainee_id == user.id):
            raise AbsenceTraineeIdMismatch

        session_filters = {"trainee_id": user.id}
        user_sessions: list[SessionTraineesLink] = search_session_trainees(
            session=session, filters=session_filters
        )
        user_training_ids = [ts.training_session_id for ts in user_sessions]
        if absence_create.training_session_id not in user_training_ids:
            raise TraineeNotRegisteredForSession

    return create_absence(session, absence_create)


def session_absence_date_validation(session: Session, absence_create: Absences):
    training_session = get_training_session(
        session=session, session_id=absence_create.training_session_id
    )

    today_midnight = datetime.combine(datetime.today(), datetime.min.time())
    print("DEBUG")
    print(absence_create.absence_date)
    print(type(absence_create.absence_date))
    return (
        absence_create.absence_date.weekday() == training_session.day
        and absence_create.absence_date > today_midnight
    )


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
