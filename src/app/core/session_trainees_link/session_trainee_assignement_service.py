from sqlmodel import Session
from src.app.core.session_trainees_link.crud_session_trainees import (
    CRUDSessionTraineeAssignment,
)
from src.app.core.session_trainees_link.exceptions import (
    SessionTraineesLinkAlreadyExists,
    SessionTraineesLinkNotFound,
)
from src.app.core.training_sessions.exceptions import TraineesHasOverlappingSessions
from src.app.schemas.training_sessions import (
    SessionTraineeAssignement,
    TrainingSessions,
)
from src.app.core.training_sessions.training_session_service import (
    TrainingSessionService,
)


class SessionTraineeAssignementService:
    def __init__(
        self,
        crud_session_trainees_link: CRUDSessionTraineeAssignment,
        training_session_service: TrainingSessionService,
    ) -> None:
        self.crud_session_trainees_link = crud_session_trainees_link
        self.training_session_service = training_session_service

    def create_session_trainees_link(
        self, session: Session, session_id: int, trainee_id: int
    ) -> SessionTraineeAssignement:
        session_trainees_link = SessionTraineeAssignement(
            training_session_id=session_id, trainee_id=trainee_id
        )
        existing = self.crud_session_trainees_link.get_by_composite_key(
            session=session, training_session_id=session_id, trainee_id=trainee_id
        )
        if existing:
            raise SessionTraineesLinkAlreadyExists

        if self.check_trainee_session_overlap(
            session, trainee_id, session_trainees_link
        ):
            raise TraineesHasOverlappingSessions

        return self.crud_session_trainees_link.create(
            session=session, obj_in=session_trainees_link
        )

    def get_session_trainees_link(
        self, session: Session, session_id: int
    ) -> list[SessionTraineeAssignement]:
        return self.crud_session_trainees_link.get_with_filters(
            session=session, filters={"training_session_id": session_id}
        )

    def get_trainee_session_links(
        self, session: Session, trainee_id: int
    ) -> list[SessionTraineeAssignement]:
        return self.crud_session_trainees_link.get_with_filters(
            session=session, filters={"trainee_id": trainee_id}
        )

    def delete_session_trainees_link(
        self, session: Session, session_id: int, trainee_id: int
    ) -> None:
        success = self.crud_session_trainees_link.delete_by_composite_key(
            session=session, training_session_id=session_id, trainee_id=trainee_id
        )
        if not success:
            raise SessionTraineesLinkNotFound

    def check_trainee_session_overlap(
        self, session: Session, trainee_id: int, session_to_assign: TrainingSessions
    ):
        """
        Checks is trainees has any overlapping training session e.g. session occuring at the same time

        Args:
            session (Session): _description_
            trainee_id (int): _description_
            session_to_assign (TrainingSessions): _description_

        Returns:
            _type_: _description_
        """
        trainee_sessions = self.get_trainee_session_links(session, trainee_id)

        for trainee_session in trainee_sessions:
            existing_session = self.training_session_service.get_training_session(
                session=session, session_id=trainee_session.training_session_id
            )

            if not existing_session:
                continue

            if existing_session.day == session_to_assign.day:
                if existing_session.overlaps_with(session_to_assign):
                    return True

        return False

    # def get_self_training_session(
    #     self, session: Session, user: User
    # ) -> list[TrainingSessions]:
    #     if user.is_trainer:
    #         search_filters = {"trainer_id": user.id}
    #         return self.crud_training_sessions.get_with_filters(
    #             session=session, filters=search_filters
    #         )
    #     else:
    #         user_sessions: list[SessionTraineesLink] = (
    #             self.session_trainee_link_service.get_trainee_session_links(
    #                 session=session, trainee_id=user.id
    #             )
    #         )
    #         sessions = []
    #         for user_session in user_sessions:
    #             training_session_search_filters = {
    #                 "id": user_session.training_session_id
    #             }
    #             sessions.extend(
    #                 self.crud_training_sessions.get_with_filters(
    #                     session=session, filters=training_session_search_filters
    #                 )
    #             )

    #         return sessions
