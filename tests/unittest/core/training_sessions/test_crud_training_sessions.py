from sqlmodel import Session
from src.app.core.training_sessions import crud_training_sessions
from src.app.schemas.training_sessions import TrainingSessionsUpdate


def test_write_training_session(session: Session, training_session_data):
    session_obj = crud_training_sessions.write_training_session(
        session, training_session_data
    )
    assert session_obj.id is not None
    assert session_obj.location == "Leo Lagrange"


def test_get_training_session_by_id(session: Session, training_session_data):
    session_obj = crud_training_sessions.write_training_session(
        session, training_session_data
    )
    found = crud_training_sessions.get_training_session_by_id(session, session_obj.id)
    assert found is not None
    assert found.id == session_obj.id


def test_get_all_training_sessions(session: Session, training_session_data):
    crud_training_sessions.write_training_session(session, training_session_data)
    sessions = crud_training_sessions.get_all_training_sessions(session)
    assert isinstance(sessions, list)
    assert any(s.location == "Leo Lagrange" for s in sessions)


def test_update_training_session(session: Session, training_session_data):
    session_obj = crud_training_sessions.write_training_session(
        session, training_session_data
    )
    update_data = TrainingSessionsUpdate(location="Alain Mimoun")
    updated = crud_training_sessions.patch_training_session(
        session, session_obj, update_data
    )
    assert updated.location == "Alain Mimoun"


def test_delete_training_session(session: Session, training_session_data):
    session_obj = crud_training_sessions.write_training_session(
        session, training_session_data
    )
    deleted = crud_training_sessions.delete_training_session(session, session_obj.id)
    assert deleted is True
    assert (
        crud_training_sessions.get_training_session_by_id(session, session_obj.id)
        is None
    )


def test_get_training_sessions_with_filters(session: Session, training_session_data):
    crud_training_sessions.write_training_session(session, training_session_data)
    filters = {"location": "Leo Lagrange"}
    sessions = crud_training_sessions.get_training_sessions_with_filters(
        session, filters
    )
    assert len(sessions) > 0
    assert sessions[0].location == "Leo Lagrange"
