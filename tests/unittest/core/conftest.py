import pytest
from sqlmodel import SQLModel, Session, create_engine

from src.app.schemas.training_sessions import (
    TrainingSessions,
    time,
)
from src.app.schemas.user import User


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for user in users_init():
            session.add(user)

        session.commit()
        yield session


def users_init():
    users = [
        User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=True,
            id=1,
        ),
        User(
            first_name="Gael",
            last_name="Monfils",
            email="gael@monfils.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=False,
            id=2,
        ),
        User(
            first_name="Maxime",
            last_name="Daban",
            email="maxime@daban.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=True,
            id=3,
        ),
        User(
            first_name="Emmanuel",
            last_name="Macron",
            email="emmanuel@macron.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=False,
            id=4,
        ),
        User(
            first_name="Son",
            last_name="Goku",
            email="son@goku.com",
            hashed_password="...",
            is_superuser=False,
            is_trainer=False,
            id=5,
        ),
    ]

    for user in users:
        yield user


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
def session_training_assignment(
    session,
):
    for se in training_session_init():
        session.add(se)
    session.commit()
    yield session


def training_session_init():
    sessions = [
        TrainingSessions(  # id=1
            day=1,
            trainer_id=1,
            session_start=time(10),
            session_duration=60,
            location="Carnot",
            court_number=1,
        ),
        TrainingSessions(  # id=2
            day=1,
            trainer_id=1,
            session_start=time(13),
            session_duration=60,
            location="Carnot",
            court_number=2,
        ),
        TrainingSessions(  # id=3
            day=1,
            trainer_id=5,
            session_start=time(10),
            session_duration=60,
            location="Leo Lagrange",
            court_number=1,
        ),
        TrainingSessions(  # id=4
            day=2,
            trainer_id=5,
            session_start=time(10),
            session_duration=60,
            location="Leo Lagrange",
            court_number=1,
        ),
    ]

    for se in sessions:
        yield se
