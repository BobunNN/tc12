import pytest

from src.app.core.session_trainees_assignment.exceptions import (
    SessionTraineeAssignementAlreadyExists,
    TraineeIsTrainer,
    TraineesHasOverlappingSessions,
)
from src.app.core.session_trainees_assignment.session_trainee_assignment_service import (
    CRUDSessionTraineeAssignment,
    SessionTraineeAssignmentService,
)
from src.app.core.training_sessions.exceptions import TrainingSessionNotFound
from src.app.core.training_sessions.training_session_service import (
    CRUDTrainingSessions,
    TrainingSessionService,
)
from src.app.core.users.user_service import UserService

from src.app.core.users.crud_users import CRUDUsers

from src.app.schemas.training_sessions import SessionTraineeAssignment, TrainingSessions
from src.app.schemas.user import User

crud_users = CRUDUsers(User)
crud_session_trainees_link = CRUDSessionTraineeAssignment(SessionTraineeAssignment)
crud_training_sessions = CRUDTrainingSessions(TrainingSessions)

user_service = UserService(crud_users)
crud_assignment = CRUDSessionTraineeAssignment(SessionTraineeAssignment)
training_session_service = TrainingSessionService(
    crud_training_sessions,
    user_service,
)
training_assignment_service = SessionTraineeAssignmentService(
    crud_assignment,
    training_session_service,
    user_service,
)


def test_create_assignment(session_training_assignment, new_training_assignment):
    new_assignment = training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )
    assert new_assignment is not None
    assert new_assignment.trainee_id == new_training_assignment.trainee_id
    assert (
        new_assignment.training_session_id
        == new_training_assignment.training_session_id
    )


def test_create_assignment_with_trainer(
    session_training_assignment, new_training_assignment_with_trainer
):
    with pytest.raises(TraineeIsTrainer):
        training_assignment_service.create_session_trainees_link(
            session_training_assignment,
            new_training_assignment_with_trainer.training_session_id,
            new_training_assignment_with_trainer.trainee_id,
        )


def test_create_assignment_invalid_session(
    session_training_assignment, new_training_assignment_invalid_session
):
    with pytest.raises(TrainingSessionNotFound):
        training_assignment_service.create_session_trainees_link(
            session_training_assignment,
            new_training_assignment_invalid_session.training_session_id,
            new_training_assignment_invalid_session.trainee_id,
        )


def test_create_duplicate(session_training_assignment, new_training_assignment):
    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )

    with pytest.raises(SessionTraineeAssignementAlreadyExists):
        training_assignment_service.create_session_trainees_link(
            session_training_assignment,
            new_training_assignment.training_session_id,
            new_training_assignment.trainee_id,
        )


def test_get_user_sessions(
    session_training_assignment, new_training_assignment, new_training_assignment2
):
    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )
    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment2.training_session_id,
        new_training_assignment2.trainee_id,
    )

    user_sessions = training_assignment_service.get_user_session(
        session_training_assignment, new_training_assignment.trainee_id
    )
    assert len(user_sessions) == 2


def test_delete_session(session_training_assignment, new_training_assignment):
    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )
    training_assignment_service.delete_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )

    user_sessions = training_assignment_service.get_user_session(
        session_training_assignment, new_training_assignment.trainee_id
    )
    assert len(user_sessions) == 0


def test_assignment_overlap(
    session_training_assignment, new_training_assignment, new_assignment_overlap
):
    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )

    with pytest.raises(TraineesHasOverlappingSessions):
        training_assignment_service.create_session_trainees_link(
            session_training_assignment,
            new_assignment_overlap.training_session_id,
            new_assignment_overlap.trainee_id,
        )


def test_get_self_training_session(
    session_training_assignment,
    new_training_assignment,
    new_training_assignment2,
    new_training_assignment3,
    trainer_user,
    trainee_user,
):
    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment.training_session_id,
        new_training_assignment.trainee_id,
    )

    training_assignment_service.create_session_trainees_link(
        session_training_assignment,
        new_training_assignment3.training_session_id,
        new_training_assignment3.trainee_id,
    )

    trainer_sessions = training_assignment_service.get_self_training_session(
        session_training_assignment, trainer_user
    )
    assert len(trainer_sessions) == 2

    trainee_sessions = training_assignment_service.get_self_training_session(
        session_training_assignment, trainee_user
    )
    assert len(trainee_sessions) == 1
