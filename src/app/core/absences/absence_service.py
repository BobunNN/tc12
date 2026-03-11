from datetime import date, datetime, timedelta

from sqlmodel import Session
from src.app.core.absences.exceptions import (
    AbsenceAlreadyExists,
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
from src.app.core.training_sessions.crud_training_sessions import (
    get_training_sessions_with_filters,
)
from src.app.schemas.training_sessions import SessionTraineesLink, TrainingSessions
from src.app.schemas.absences import AbsenceCreate, Absences
from src.app.schemas.user import User

from src.app.core.absences.crud_absences import (
    create_absence,
    get_unique_absence_by_ckey,
    get_all_absences,
    delete_absence,
    get_absences_with_filters,
)


def _next_upcoming_date_for_weekday(weekday: int) -> datetime:
    """Return the next upcoming date (midnight) that falls on the given weekday (0=Mon, 6=Sun)."""
    today = date.today()
    today_weekday = today.weekday()
    days_ahead = (weekday - today_weekday) % 7
    if days_ahead == 0:
        days_ahead = 7  # validation requires date > today_midnight, so use next week
    next_date = today + timedelta(days=days_ahead)
    return datetime.combine(next_date, datetime.min.time())


def open_absence_slot(
    session: Session, absence_create: AbsenceCreate, user: User
) -> Absences:
    training_session = get_training_session(
        session=session, session_id=absence_create.training_session_id
    )
    if absence_create.absence_date is None:
        absence_create.absence_date = _next_upcoming_date_for_weekday(
            int(training_session.day)
        )
    if not session_absence_date_validation(session, absence_create):
        raise AbsenceDateMismatchSessionDay

    if user.is_trainer:
        training_session: TrainingSessions = get_training_session(
            session=session, session_id=absence_create.training_session_id
        )
        if training_session.trainer_id != user.id:
            raise TrainerDoesNotManageTrainingSession

        session_trainees: list[SessionTraineesLink] = search_session_trainees(
            session=session, session_id=absence_create.training_session_id
        )
        registered_trainee_ids = [st.trainee_id for st in session_trainees]
        if absence_create.trainee_id not in registered_trainee_ids:
            raise TraineeNotRegisteredForSession

    else:
        if absence_create.trainee_id != user.id:
            raise AbsenceTraineeIdMismatch

        session_trainees: list[SessionTraineesLink] = search_session_trainees(
            session=session, session_id=absence_create.training_session_id
        )
        registered_trainee_ids = [st.trainee_id for st in session_trainees]
        if user.id not in registered_trainee_ids:
            raise TraineeNotRegisteredForSession

    existing = get_unique_absence_by_ckey(
        session,
        trainee_id=absence_create.trainee_id,
        training_id=absence_create.training_session_id,
        training_date=absence_create.absence_date,
    )
    if existing:
        raise AbsenceAlreadyExists

    return create_absence(session, absence_create)


def session_absence_date_validation(session: Session, absence_create: AbsenceCreate):
    training_session = get_training_session(
        session=session, session_id=absence_create.training_session_id
    )

    today_midnight = datetime.combine(datetime.today(), datetime.min.time())
    return (
        absence_create.absence_date.weekday() == int(training_session.day)
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


def delete_absence_service(
    session: Session,
    trainee_id: int,
    training_id: int,
    training_date: datetime,
    current_user: User,
) -> None:
    absence = get_unique_absence_by_ckey(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=training_date,
    )
    if not absence:
        raise AbsenceNotFound
    if absence.trainee_id != current_user.id and not current_user.is_superuser:
        raise AbsenceTraineeIdMismatch
    delete_absence(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=training_date,
    )


def get_self_absences(session: Session, current_user: User) -> list[Absences]:
    if current_user.is_trainer:
        trainer_sessions = get_training_sessions_with_filters(
            session=session, filters={"trainer_id": current_user.id}
        )
        all_absences: list[Absences] = []
        for ts in trainer_sessions:
            session_absences = get_absences_with_filters(
                session=session, filters={"training_session_id": ts.id}
            )
            all_absences.extend(session_absences)
        return all_absences
    else:
        return get_absences_with_filters(
            session=session, filters={"trainee_id": current_user.id}
        )
