import pytest

from src.app.schemas.training_sessions import SessionTraineeAssignment


@pytest.fixture
def new_training_assignment():
    return SessionTraineeAssignment(
        training_session_id=1,
        trainee_id=2,
    )


@pytest.fixture
def new_training_assignment2():
    return SessionTraineeAssignment(
        training_session_id=2,
        trainee_id=2,
    )


@pytest.fixture
def new_training_assignment_with_trainer():
    return SessionTraineeAssignment(
        training_session_id=1,
        trainee_id=1,  # trainee is a trainer
    )


@pytest.fixture
def new_training_assignment_invalid_session():
    return SessionTraineeAssignment(
        training_session_id=9999,
        trainee_id=1,
    )


@pytest.fixture
def new_assignment_overlap():
    return SessionTraineeAssignment(
        training_session_id=3,  # overlaps with session 1
        trainee_id=2,
    )
