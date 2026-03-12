from typing import Any

from sqlmodel import Session

from src.app.core.training_sessions.exceptions import (
    TrainingSessionInvalidTrainer,
    TrainingSessionNotFound,
    TrainingSessionOverlap,
)

from src.app.core.training_sessions.crud_training_sessions import CRUDTrainingSessions
from src.app.core.users.user_service import UserService
from src.app.schemas.training_sessions import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessions,
)

TRAINING_SESSION_MAX_CAPACITY = 4


class TrainingSessionService:
    def __init__(
        self,
        crud_training_sessions: CRUDTrainingSessions,
        user_service: UserService,
    ) -> None:
        self.crud_training_sessions = crud_training_sessions
        self.user_service = user_service

    def create_training_session(
        self, session: Session, session_create: TrainingSessionCreate
    ) -> TrainingSessions:

        if self.check_sessions_overlap(session, session_create):
            raise TrainingSessionOverlap

        if not self.user_service.check_is_trainer(session, session_create.trainer_id):
            raise TrainingSessionInvalidTrainer

        return self.crud_training_sessions.create(
            session=session, obj_in=session_create
        )

    def check_sessions_overlap(
        self,
        session: Session,
        session_create: TrainingSessionCreate,
    ) -> bool:
        """
        Checks is the training session passed is overlapping with existing training session, which includes time, location and court number

        Args:
            session (Session): _description_
            training_session (TrainingSessions): _description_

        Returns:
            bool: _description_
        """
        filters = {
            "location": session_create.location,
            "court_number": session_create.court_number,
            "day": session_create.day,
        }

        potential_overlaps: list[TrainingSessions] = (
            self.crud_training_sessions.get_with_filters(
                session=session, filters=filters
            )
        )

        for s in potential_overlaps:
            if s.overlaps_with(session_create):
                return True

        return False

    def get_training_session(
        self, session: Session, session_id: int
    ) -> TrainingSessions:
        training_session = self.crud_training_sessions.get_by_id(
            session=session, record_id=session_id
        )
        if not training_session:
            raise TrainingSessionNotFound
        return training_session

    def get_all_training_session(
        self, session: Session, offset: int, limit: int
    ) -> list[TrainingSessions]:
        sessions = self.crud_training_sessions.get_all(
            session=session, offset=offset, limit=limit
        )
        return sessions

    def update_training_session(
        self,
        session: Session,
        session_id: int,
        session_update: TrainingSessionUpdate,
    ) -> TrainingSessions:
        training_session = self.crud_training_sessions.get_by_id(
            session=session, record_id=session_id
        )

        if not training_session:
            raise TrainingSessionNotFound

        if session_update.trainer_id:
            if not self.user_service.check_is_trainer(
                session=session, id=session_update.trainer_id
            ):
                raise TrainingSessionInvalidTrainer

        update_data = training_session.model_dump()
        update_fields = session_update.model_dump(exclude_unset=True)
        update_data.update(update_fields)
        merged_session = TrainingSessions(**update_data)

        if self.check_sessions_overlap(session, merged_session):
            raise TrainingSessionOverlap

        return self.crud_training_sessions.update(
            session=session, db_obj=training_session, obj_in=session_update
        )

    def remove_training_session(
        self,
        session: Session,
        session_id: int,
    ) -> Any:
        success = self.crud_training_sessions.delete_by_id(
            session=session, record_id=session_id
        )
        if not success:
            raise TrainingSessionNotFound
        return {"detail": "Deleted successfully"}

    def search_training_session(
        self, session: Session, filters: dict
    ) -> list[TrainingSessions]:
        return self.crud_training_sessions.get_with_filters(
            session=session, filters=filters
        )

    def bulk_load_training_sessions(self, session: Session, records: list[dict]) -> Any:
        loaded = []
        errors = []
        for record in records:
            try:
                session_obj = TrainingSessions.model_validate(record)
                existing = self.crud_training_sessions.get_by_id(
                    session=session, record_id=session_obj.id
                )
                if existing:
                    continue
                self.create_training_session(session, session_obj)
                loaded.append(session_obj)
            except Exception as e:
                errors.append({"record": record, "error": str(e)})
        return {"loaded_count": len(loaded), "errors": errors}
