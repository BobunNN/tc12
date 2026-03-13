from sqlmodel import Session
from src.app.core.users.user_service import UserService
from src.app.schemas.training_sessions import (
    TrainingSessionUpdate,
    TrainingSessions,
)
from src.app.core.training_sessions.crud_training_sessions import CRUDTrainingSessions
from src.app.core.training_sessions.exceptions import (
    TrainingSessionNotFound,
    TrainingSessionOverlap,
    TrainingSessionInvalidTrainer,
)
import pytest
from src.app.core.training_sessions.training_session_service import (
    TrainingSessionService,
)
from src.app.core.users.crud_users import CRUDUsers
from src.app.core.session_trainees_assignment.crud_session_trainees import (
    CRUDSessionTraineeAssignment,
)

from src.app.schemas.training_sessions import SessionTraineeAssignment
from src.app.schemas.user import User

crud_training_sessions = CRUDTrainingSessions(TrainingSessions)
crud_users = CRUDUsers(User)
crud_session_trainees_link = CRUDSessionTraineeAssignment(SessionTraineeAssignment)
user_service = UserService(crud_users)
training_session_service = TrainingSessionService(crud_training_sessions, user_service)


def test_create_training_session(
    session: Session,
    training_session_invalid_trainer,
    training_session_data2,
):

    with pytest.raises(TrainingSessionInvalidTrainer):
        training_session_service.create_training_session(
            session, training_session_invalid_trainer
        )

    session_obj2 = training_session_service.create_training_session(
        session, training_session_data2
    )

    assert session_obj2.id is not None
    assert session_obj2.location == "Alain Mimoun"


def test_get_training_session(session: Session, training_session_data):
    session_obj = training_session_service.create_training_session(
        session, training_session_data
    )
    found = training_session_service.get_training_session(session, session_obj.id)
    assert found.id == session_obj.id


def test_get_training_session_not_found(session: Session):
    with pytest.raises(TrainingSessionNotFound):
        training_session_service.get_training_session(session, 9999)


def test_update_training_session(session: Session, training_session_data):
    session_obj = training_session_service.create_training_session(
        session, training_session_data
    )
    update_data = TrainingSessionUpdate(location="Alain Mimoun")
    updated = training_session_service.update_training_session(
        session, session_obj.id, update_data
    )
    assert updated.location == "Alain Mimoun"

    with pytest.raises(TrainingSessionInvalidTrainer):
        update_data = TrainingSessionUpdate(trainer_id=2)
        updated = training_session_service.update_training_session(
            session, session_obj.id, update_data
        )


def test_update_training_session_not_found(session: Session):
    update = TrainingSessionUpdate(location="Alain Mimoun")
    with pytest.raises(TrainingSessionNotFound):
        training_session_service.update_training_session(session, 9999, update)


def test_update_training_session_overlap(
    session: Session,
    training_session_data,
    training_session_data2,
    training_session_update_overlap,
):
    training_session_service.create_training_session(session, training_session_data)
    training_session_service.create_training_session(session, training_session_data2)

    with pytest.raises(TrainingSessionOverlap):
        training_session_service.update_training_session(
            session, 2, training_session_update_overlap
        )


def test_get_all_training_session(session: Session, training_session_data):
    training_session_service.create_training_session(session, training_session_data)
    sessions = training_session_service.get_all_training_session(session, 0, 100)
    assert isinstance(sessions, list)
    assert any(s.location == "Leo Lagrange" for s in sessions)


def test_create_sessions_overlap(
    session: Session, training_session_data, training_session_overlap
):
    training_session_service.create_training_session(
        session=session, session_create=training_session_data
    )
    with pytest.raises(TrainingSessionOverlap):
        training_session_service.create_training_session(
            session=session, session_create=training_session_overlap
        )
