from sqlmodel import Session
from src.app.core.session_trainees_assignement.crud_session_trainees import (
    CRUDSessionTraineeAssignment,
)
from src.app.core.session_trainees_assignement.exceptions import (
    SessionTraineeAssignementAlreadyExists,
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
from src.app.schemas.user import User


class SessionTraineeAssignementService:
    def __init__(
        self,
        crud_session_trainees_link: CRUDSessionTraineeAssignment,
        training_session_service: TrainingSessionService,
    ) -> None:
        self.crud_session_trainees_link = crud_session_trainees_link
        self.training_session_service = training_session_service

    def get_all(self, session: Session):
        return self.crud_session_trainees_link.get_all(session=session)

    def create_session_trainees_link(
        self, session: Session, session_id: int, trainee_id: int
    ) -> SessionTraineeAssignement:
        new_assignement = SessionTraineeAssignement(
            training_session_id=session_id, trainee_id=trainee_id
        )
        existing = self.crud_session_trainees_link.get_by_composite_key(
            session=session, training_session_id=session_id, trainee_id=trainee_id
        )

        if existing:
            raise SessionTraineeAssignementAlreadyExists

        if self.check_trainee_session_overlap(session, trainee_id, new_assignement):
            raise TraineesHasOverlappingSessions

        return self.crud_session_trainees_link.create(
            session=session, obj_in=new_assignement
        )

    def get_session_trainees(self, session: Session, session_id: int) -> list[int]:
        """
        Fetches all trainees for a give training session

        Args:
            session (Session): _description_
            session_id (int): _description_

        Returns:
            list[int]: _description_
        """
        res: list[SessionTraineeAssignement] = (
            self.crud_session_trainees_link.get_with_filters(
                session=session, filters={"training_session_id": session_id}
            )
        )
        return [res.trainee_id for res in res]

    def get_user_session(
        self, session: Session, trainee_id: int
    ) -> list[SessionTraineeAssignement]:
        """
        Fetches all training sessions of a give user (trainee and trainer)

        Args:
            session (Session): _description_
            trainee_id (int): _description_

        Returns:
            list[SessionTraineeAssignement]: _description_
        """
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
        self,
        session: Session,
        trainee_id: int,
        session_to_assign: SessionTraineeAssignement,
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
        trainee_sessions_all = self.get_user_session(session, trainee_id)

        training_assignement = self.training_session_service.get_training_session(
            session=session, session_id=session_to_assign.training_session_id
        )

        for trainee_session in trainee_sessions_all:
            existing_session = self.training_session_service.get_training_session(
                session=session, session_id=trainee_session.training_session_id
            )

            if not existing_session:
                continue
            print("DEBUG")
            print(f"training_assignement : {training_assignement}")
            print(f"existing_session : {existing_session}")
            if existing_session.day == training_assignement.day:
                if existing_session.overlaps_with(training_assignement):
                    return True

        return False

    def get_self_training_session(
        self, session: Session, user: User
    ) -> list[TrainingSessions]:
        if user.is_trainer:
            search_filters = {"trainer_id": user.id}
            return self.training_session_service.search_training_session(
                session=session, filters=search_filters
            )
        else:
            user_sessions: list[SessionTraineeAssignement] = (
                self.crud_session_trainees_link.get_with_filters(
                    session=session, filters={"trainee_id": user.id}
                )
            )
            sessions = []
            for user_session in user_sessions:
                sessions.extend(
                    self.training_session_service.get_training_session(
                        session=session, session_id=user_session.training_session_id
                    )
                )

            return sessions
