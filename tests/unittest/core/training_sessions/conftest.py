import pytest
from sqlmodel import SQLModel, Session, create_engine
from src.app.schemas.user import User

from src.app.schemas.training_sessions import (
    SessionTraineeAssignment,
    TrainingSessionCreate,
    TrainingSessionUpdate,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=True,
            id=1,
        )
        session.add(user)

        user = User(
            first_name="Gael",
            last_name="Monfils",
            email="gael@monfils.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=False,
            id=2,
        )
        session.add(user)

        user = User(
            first_name="Maxime",
            last_name="Daban",
            email="maxime@daban.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=True,
            id=3,
        )
        session.add(user)

        session.commit()
        yield session


@pytest.fixture
def training_session_data():
    return TrainingSessionCreate(
        day=1,
        trainer_id=1,
        session_start="10:00:00",
        session_duration=60,
        location="Leo Lagrange",
        court_number=1,
    )


@pytest.fixture
def training_session_data2():
    return TrainingSessionCreate(
        day=1,
        trainer_id=3,
        session_start="10:00:00",
        session_duration=60,
        location="Alain Mimoun",
        court_number=1,
    )


@pytest.fixture
def training_session_overlap():
    return TrainingSessionCreate(
        day=1,
        trainer_id=3,
        session_start="10:30:00",
        session_duration=60,
        location="Leo Lagrange",
        court_number=1,
    )


@pytest.fixture
def training_session_update_overlap():
    return TrainingSessionUpdate(
        location="Leo Lagrange",
    )


@pytest.fixture
def training_session_invalid_trainer():
    return TrainingSessionCreate(
        day=6,
        trainer_id=2,
        session_start="10:00:00",
        session_duration=60,
        location="Leo Lagrange",
        court_number=1,
    )


@pytest.fixture
def trainer_user(session):
    return User(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        hashed_password="...",
        is_superuser=False,
        is_trainer=True,
        id=1,
    )


@pytest.fixture
def trainee_user(session):
    return User(
        first_name="Gael",
        last_name="Monfils",
        email="gael@monfils.com",
        hashed_password="...",
        is_superuser=False,
        is_trainer=False,
        id=2,
    )


@pytest.fixture
def trainee_session_link():
    return SessionTraineeAssignment(
        training_session_id=1,
        trainee_id=2,
    )
