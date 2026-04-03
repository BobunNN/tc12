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
from src.app.core.session_trainees_assignment.session_trainee_assignment_service import (
    SessionTraineeAssignmentService,
)

from src.app.schemas.absences import AbsenceCreate, AbsenceUpdate, Absences
from src.app.schemas.user import User

from src.app.core.absences.crud_absences import (
    CrudAbsences,
)
from src.app.core.training_sessions.training_session_service import (
    TrainingSessionService,
)


class AbsenceService:
    def __init__(
        self,
        training_session_service: TrainingSessionService,
        session_trainee_link_service: SessionTraineeAssignmentService,
        crud_absences: CrudAbsences,
    ):
        self.training_session_service = training_session_service
        self.session_trainee_assignment_service = session_trainee_link_service
        self.crud_absences = crud_absences

    def _next_upcoming_date_for_weekday(self, weekday: int) -> date:
        """Return the next upcoming date that falls on the given weekday (0=Mon, 6=Sun)."""
        today = date.today()
        today_weekday = today.weekday()
        days_ahead = (weekday - today_weekday) % 7
        if days_ahead == 0:
            days_ahead = 7  # validation requires date > today, so use next week
        return today + timedelta(days=days_ahead)

    def open_absence_slot(
        self, session: Session, absence_create: AbsenceCreate, user: User
    ) -> Absences:
        training_session = self.training_session_service.get_training_session(
            session=session, session_id=absence_create.training_session_id
        )

        if absence_create.absence_date is None:
            absence_create.absence_date = self._next_upcoming_date_for_weekday(
                int(training_session.day)
            )

        if not self.session_absence_date_validation(session, absence_create):
            raise AbsenceDateMismatchSessionDay

        session_trainees_ids: list[int] = (
            self.session_trainee_assignment_service.get_session_trainees(
                session=session, session_id=absence_create.training_session_id
            )
        )

        if absence_create.trainee_id not in session_trainees_ids:
            raise TraineeNotRegisteredForSession

        if user.is_trainer:
            if training_session.trainer_id != user.id:
                raise TrainerDoesNotManageTrainingSession
        else:
            if absence_create.trainee_id != user.id:
                raise AbsenceTraineeIdMismatch

        existing = self.crud_absences.get_by_composite_key(
            session,
            trainee_id=absence_create.trainee_id,
            training_session_id=absence_create.training_session_id,
            absence_date=absence_create.absence_date,
        )
        if existing:
            raise AbsenceAlreadyExists

        return self.crud_absences.create(session=session, obj_in=absence_create)

    def session_absence_date_validation(
        self, session: Session, absence_create: AbsenceCreate
    ):
        if absence_create.absence_date is None:
            return False

        training_session = self.training_session_service.get_training_session(
            session=session, session_id=absence_create.training_session_id
        )

        return (
            absence_create.absence_date.weekday() == int(training_session.day)
            and absence_create.absence_date > date.today()
        )

    def search_unique_absence(
        self,
        session: Session,
        trainee_id: int,
        training_session_id: int,
        absence_date: date,
    ) -> Absences:
        absence = self.crud_absences.get_by_composite_key(
            session,
            trainee_id=trainee_id,
            training_session_id=training_session_id,
            absence_date=absence_date,
        )
        if not absence:
            raise AbsenceNotFound
        return absence

    def get_all_absences_service(
        self, session: Session, status: str | None = None
    ) -> list[Absences]:
        filters = {}
        if status is not None:
            filters["status"] = status
        return (
            self.crud_absences.get_with_filters(session, filters)
            if filters
            else self.crud_absences.get_all(session)
        )

    def delete_absence_service(
        self,
        session: Session,
        trainee_id: int,
        training_session_id: int,
        absence_date: datetime,
        current_user: User,
    ) -> None:
        absence = self.crud_absences.get_by_composite_key(
            session,
            trainee_id=trainee_id,
            training_session_id=training_session_id,
            absence_date=absence_date,
        )
        if not absence:
            raise AbsenceNotFound

        if absence.trainee_id != current_user.id and not current_user.is_superuser:
            raise AbsenceTraineeIdMismatch

        self.crud_absences.delete_by_composite_key(
            session,
            trainee_id=trainee_id,
            training_session_id=training_session_id,
            absence_date=absence_date,
        )

    def get_self_absences(self, session: Session, current_user: User) -> list[Absences]:
        if current_user.is_trainer:
            trainer_sessions = self.training_session_service.search_training_session(
                session=session, filters={"trainer_id": current_user.id}
            )
            all_absences: list[Absences] = []
            for ts in trainer_sessions:
                session_absences = self.crud_absences.get_with_filters(
                    session=session, filters={"training_session_id": ts.id}
                )
                all_absences.extend(session_absences)
            return all_absences
        else:
            return self.crud_absences.get_with_filters(
                session=session, filters={"trainee_id": current_user.id}
            )

    def get_absences_for_slot(
        self, session: Session, training_session_id: int, absence_date: date
    ) -> list[Absences]:
        return self.crud_absences.get_with_filters(
            session=session,
            filters={
                "training_session_id": training_session_id,
                "absence_date": absence_date,
            },
        )

    def confirm_absence(self, session: Session, absence: Absences) -> Absences:
        return self.crud_absences.update(
            session=session,
            db_obj=absence,
            obj_in=AbsenceUpdate(status="confirmed"),
        )

    def get_count(self, session: Session) -> int:
        return self.crud_absences.get_count(session)
