import pytest
from src.app.core.absences.absence_service import AbsenceService
from src.app.core.absences.crud_absences import CrudAbsences
from src.app.core.absences.exceptions import (
    AbsenceAlreadyExists,
    AbsenceDateMismatchSessionDay,
    AbsenceNotFound,
    AbsenceTraineeIdMismatch,
    TraineeNotRegisteredForSession,
    TrainerDoesNotManageTrainingSession,
)
from src.app.core.session_trainees_assignment.session_trainee_assignment_service import (
    CRUDSessionTraineeAssignment,
    SessionTraineeAssignmentService,
)
from src.app.core.training_sessions.training_session_service import (
    CRUDTrainingSessions,
    TrainingSessionService,
)
from src.app.core.users.crud_users import CRUDUsers
from src.app.schemas.absences import AbsenceCreate, Absences
from src.app.schemas.training_sessions import SessionTraineeAssignment, TrainingSessions
from src.app.schemas.user import User
from src.app.core.users.user_service import UserService

crud_users = CRUDUsers(User)
crud_session_trainees_link = CRUDSessionTraineeAssignment(SessionTraineeAssignment)
crud_training_sessions = CRUDTrainingSessions(TrainingSessions)
crud_absence = CrudAbsences(Absences)

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

absence_service = AbsenceService(
    training_session_service, training_assignment_service, crud_absence
)


def test_create_absence_slot_valid(session_absences, trainee_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=2,
    )
    absence = absence_service.open_absence_slot(
        session_absences, absence_create, trainee_user
    )
    assert absence.training_session_id == 1
    assert absence.trainee_id == 2


def test_absence_date_mismatch(session_absences, trainee_user):
    incorrect_date = absence_service._next_upcoming_date_for_weekday(
        2
    )  # Testing session 1 that takes place on day 1 and not 2
    absence_create = AbsenceCreate(
        training_session_id=1, trainee_id=2, absence_date=incorrect_date
    )
    with pytest.raises(AbsenceDateMismatchSessionDay):
        absence_service.open_absence_slot(
            session_absences, absence_create, trainee_user
        )


def test_create_absence_slot_not_registered(session_absences, trainee_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=99,
    )
    with pytest.raises(TraineeNotRegisteredForSession):
        absence_service.open_absence_slot(
            session_absences, absence_create, trainee_user
        )


def test_create_absence_slot_trainer_not_manager(session_absences, trainer_user):
    absence_create = AbsenceCreate(
        training_session_id=3,
        trainee_id=5,
    )
    with pytest.raises(TrainerDoesNotManageTrainingSession):
        absence_service.open_absence_slot(
            session_absences, absence_create, trainer_user
        )


def test_create_absence_slot_trainee_id_mismatch(session_absences, trainee_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=4,
    )
    with pytest.raises(AbsenceTraineeIdMismatch):
        absence_service.open_absence_slot(
            session_absences, absence_create, trainee_user
        )


def test_create_absence_slot_already_exists(session_absences, trainee_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=2,
    )
    absence_service.open_absence_slot(session_absences, absence_create, trainee_user)
    with pytest.raises(AbsenceAlreadyExists):
        absence_service.open_absence_slot(
            session_absences, absence_create, trainee_user
        )


def test_delete_absence_valid(session_absences, trainee_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=2,
    )
    new_absence = absence_service.open_absence_slot(
        session_absences, absence_create, trainee_user
    )
    absence_date = new_absence.absence_date
    absence_service.delete_absence_service(
        session_absences,
        trainee_id=2,
        training_session_id=1,
        absence_date=absence_date,
        current_user=trainee_user,
    )
    with pytest.raises(AbsenceNotFound):
        absence_service.search_unique_absence(
            session_absences,
            trainee_id=2,
            training_session_id=1,
            absence_date=absence_date,
        )


def test_delete_absence_invalid_user(session_absences, trainee_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=2,
    )
    new_absence = absence_service.open_absence_slot(
        session_absences, absence_create, trainee_user
    )
    absence_date = new_absence.absence_date
    with pytest.raises(AbsenceTraineeIdMismatch):
        absence_service.delete_absence_service(
            session_absences,
            trainee_id=2,
            training_session_id=1,
            absence_date=absence_date,
            current_user=User(id=99, is_superuser=False, is_trainer=False),
        )


def test_get_all_absences(session_absences):
    absences = absence_service.get_all_absences_service(session_absences)
    assert isinstance(absences, list)


def test_get_self_absences_trainer(session_absences, trainer_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=2,
    )
    absence_service.open_absence_slot(session_absences, absence_create, trainer_user)
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=4,
    )
    absence_service.open_absence_slot(session_absences, absence_create, trainer_user)

    absences = absence_service.get_self_absences(session_absences, trainer_user)
    assert isinstance(absences, list)
    assert len(absences) == 2


def test_get_self_absences_trainee(session_absences, trainee_user, trainer_user):
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=2,
    )
    absence_service.open_absence_slot(session_absences, absence_create, trainer_user)
    absence_create = AbsenceCreate(
        training_session_id=1,
        trainee_id=4,
    )
    absence_service.open_absence_slot(session_absences, absence_create, trainer_user)

    absences = absence_service.get_self_absences(session_absences, trainee_user)
    assert isinstance(absences, list)
    assert len(absences) == 1
