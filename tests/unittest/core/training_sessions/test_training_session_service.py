from sqlmodel import Session
from src.app.schemas.training_sessions import (
    TrainingSessionUpdate,
)
from src.app.core.training_sessions import training_session_service
from src.app.core.training_sessions.exceptions import (
    TrainingSessionNotFound,
    TrainingSessionOverlap,
    TrainingSessionInvalidTrainer,
)
import pytest


def test_create_training_session(
    session: Session,
    training_session_data,
    training_session_invalid_trainer,
    training_session_data2,
):
    session_obj = training_session_service.create_training_session(
        session, training_session_data
    )
    assert session_obj.id is not None
    assert session_obj.location == "Leo Lagrange"

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
    sessions = training_session_service.get_all_training_session(session)
    assert isinstance(sessions, list)
    assert any(s.location == "Leo Lagrange" for s in sessions)


def test_check_sessions_overlap(
    session: Session, training_session_data, training_session_overlap
):
    training_session_service.create_training_session(session, training_session_data)
    with pytest.raises(TrainingSessionOverlap):
        training_session_service.create_training_session(
            session, training_session_overlap
        )
    with pytest.raises(TrainingSessionOverlap):
        training_session_service.create_training_session(
            session, training_session_overlap
        )


def test_get_self_training_session_trainer(
    session: Session, training_session_data, trainer_user
):
    training_session_service.create_training_session(session, training_session_data)
    sessions = training_session_service.get_self_training_session(session, trainer_user)
    assert isinstance(sessions, list)
    assert any(s.trainer_id == trainer_user.id for s in sessions)


def test_get_self_training_session_trainee(
    session: Session, training_session_data, trainee_user, trainee_session_link
):
    training_session_service.create_training_session(session, training_session_data)
    session.add(trainee_session_link)
    session.commit()
    sessions = training_session_service.get_self_training_session(session, trainee_user)
    assert isinstance(sessions, list)
    assert any(s.id == trainee_session_link.training_session_id for s in sessions)
