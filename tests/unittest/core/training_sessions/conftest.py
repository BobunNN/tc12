import pytest

from src.app.schemas.training_sessions import (
    SessionTraineeAssignment,
    TrainingSessionCreate,
    TrainingSessionUpdate,
)


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
def trainee_session_link():
    return SessionTraineeAssignment(
        training_session_id=1,
        trainee_id=2,
    )
