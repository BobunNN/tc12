from fastapi import FastAPI, HTTPException, Request, status
from pydantic import ValidationError

from src.app.core.users.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    SuperUserSelfDeleteForbidden,
    SelfDeleteNotAllowedHere,
    IncorrectPassword,
    NewPasswordCannotBeTheSameAsTheCurrentOne,
)
from src.app.core.absences.exceptions import (
    AbsenceNotFound,
    AbsenceDateMismatchSessionDay,
    AbsenceTraineeIdMismatch,
    TrainerDoesNotManageTrainingSession,
    AbsenceAlreadyExists,
    TraineeNotRegisteredForSession,
)
from src.app.core.training_sessions.exceptions import (
    TrainingSessionAlreadyExists,
    TrainingSessionOverlap,
    TrainingSessionInvalidTrainer,
    TrainingSessionNotFound,
    TraineesHasOverlappingSessions,
    TrainingSessionMaxCapacity,
)
from src.app.core.session_trainees_assignement.exceptions import (
    SessionTraineeAssignementAlreadyExists,
)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(ValidationError, validation_exception_handler)
    # Users
    app.add_exception_handler(UserAlreadyExists, handle_user_already_exists)
    app.add_exception_handler(UserNotFound, handle_user_not_found)
    app.add_exception_handler(
        SuperUserSelfDeleteForbidden, handle_super_user_self_delete
    )
    app.add_exception_handler(SelfDeleteNotAllowedHere, handle_self_delete_not_allowed)
    app.add_exception_handler(IncorrectPassword, handle_incorrect_password)
    app.add_exception_handler(
        NewPasswordCannotBeTheSameAsTheCurrentOne,
        handle_new_password_cannot_be_the_same_as_the_current_one,
    )
    # Absences
    app.add_exception_handler(AbsenceNotFound, handle_absence_not_found)
    app.add_exception_handler(
        AbsenceDateMismatchSessionDay, handle_absence_date_mismatch_session_day
    )
    app.add_exception_handler(
        TrainerDoesNotManageTrainingSession,
        handle_trainer_does_not_manage_training_session,
    )
    app.add_exception_handler(AbsenceAlreadyExists, handle_absence_already_exists)
    app.add_exception_handler(
        TraineeNotRegisteredForSession, handle_trainee_not_registered_for_session
    )
    app.add_exception_handler(
        AbsenceTraineeIdMismatch, handle_absence_trainee_id_mismatch
    )

    # Training sessions
    app.add_exception_handler(
        TrainingSessionAlreadyExists, handle_training_already_exists
    )
    app.add_exception_handler(TrainingSessionOverlap, handle_training_overlap)
    app.add_exception_handler(TrainingSessionInvalidTrainer, handle_invalid_trainer)
    app.add_exception_handler(
        TrainingSessionNotFound, handle_training_session_not_found
    )
    app.add_exception_handler(
        TraineesHasOverlappingSessions, handle_trainee_has_overlapping_sessions
    )
    app.add_exception_handler(TrainingSessionMaxCapacity, handle_session_max_capacity)

    # Training assignement
    app.add_exception_handler(
        SessionTraineeAssignementAlreadyExists, handle_assignement_already_exists
    )


async def validation_exception_handler(request, exc: ValidationError):
    raise HTTPException(
        status_code=422,
        detail=exc.errors(),
    )


async def handle_user_already_exists(request: Request, exc: UserAlreadyExists):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="The user with this email already exists in the system.",
    )


async def handle_user_not_found(request: Request, exc: UserNotFound):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )


async def handle_super_user_self_delete(
    request: Request, exc: SuperUserSelfDeleteForbidden
):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Super users are not allowed to delete themselves",
    )


async def handle_self_delete_not_allowed(
    request: Request, exc: SelfDeleteNotAllowedHere
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="To delete your own account, use the endpoint DELETE /v1/users/me",
    )


async def handle_incorrect_password(request: Request, exc: IncorrectPassword):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect password",
    )


async def handle_new_password_cannot_be_the_same_as_the_current_one(
    request: Request, exc: NewPasswordCannotBeTheSameAsTheCurrentOne
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="New password cannot be the same as the current one",
    )


async def handle_absence_not_found(request: Request, exc: AbsenceNotFound):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Absence not found",
    )


async def handle_absence_date_mismatch_session_day(
    request: Request, exc: AbsenceDateMismatchSessionDay
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Absence date does not match session day",
    )


async def handle_trainer_does_not_manage_training_session(
    request: Request, exc: TrainerDoesNotManageTrainingSession
):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Trainer does not manage this training session",
    )


async def handle_absence_already_exists(request: Request, exc: AbsenceAlreadyExists):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Absence already exists",
    )


async def handle_trainee_not_registered_for_session(
    request: Request, exc: TraineeNotRegisteredForSession
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Trainee not registered for this session",
    )


async def handle_absence_trainee_id_mismatch(
    request: Request, exc: AbsenceTraineeIdMismatch
):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Trainee ID mismatch",
    )


async def handle_training_already_exists(
    request: Request, exc: TrainingSessionAlreadyExists
):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Training session with this id already exists",
    )


async def handle_training_overlap(request: Request, exc: TrainingSessionOverlap):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Training session overlaps with an existing session",
    )


async def handle_invalid_trainer(request: Request, exc: TrainingSessionInvalidTrainer):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User id is not a trainer",
    )


async def handle_training_session_not_found(
    request: Request, exc: TrainingSessionNotFound
):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Training session not found",
    )


async def handle_trainee_has_overlapping_sessions(
    request: Request, exc: TraineesHasOverlappingSessions
):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Trainee has overlapping session",
    )


async def handle_session_max_capacity(
    request: Request, exc: TrainingSessionMaxCapacity
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Trainee session max capacity reached",
    )


async def handle_assignement_already_exists(
    request: Request, exc: SessionTraineeAssignementAlreadyExists
):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Assignement already exists",
    )
