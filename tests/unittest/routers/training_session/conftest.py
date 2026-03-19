import pytest
from sqlmodel import Session
from src.app.core.security import get_password_hash

from src.app.schemas.user import User


@pytest.fixture(autouse=True)
def setup_trainer(session: Session):
    """
    Automatically runs for all tests in this directory.
    It grabs the parent 'session' fixture and injects a specific user.
    """
    nested_user = User(
        first_name="Nested",
        last_name="User",
        email="nested@example.com",
        hashed_password=get_password_hash("nestedpass"),
        is_superuser=False,
        is_trainer=True,
        id=3,
    )
    session.add(nested_user)
    session.commit()


@pytest.fixture
def training_session_payload():
    return {
        "day": "1",
        "trainer_id": 3,
        "session_start": "10:00:00",
        "session_duration": 60,
        "location": "Leo Lagrange",
        "court_number": 1,
    }


@pytest.fixture
def training_session_payload2():
    return {
        "day": "1",
        "trainer_id": 3,
        "session_start": "10:00:00",
        "session_duration": 60,
        "location": "Alain Mimoun",
        "court_number": 1,
    }
