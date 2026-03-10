from fastapi import FastAPI, HTTPException, Request, status
from pydantic import ValidationError

from src.app.core.users.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    SuperUserSelfDeleteForbidden,
    SelfDeleteNotAllowedHere,
)
from src.app.core.absences.exceptions import AbsenceNotFound
from src.app.core.training_sessions.exceptions import (
    TrainingSessionAlreadyExists,
    TrainingSessionOverlap,
    TrainingSessionInvalidTrainer,
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

    # Absences
    app.add_exception_handler(AbsenceNotFound, handle_absence_not_found)

    # Training sessions
    app.add_exception_handler(
        TrainingSessionAlreadyExists, handle_training_already_exists
    )
    app.add_exception_handler(TrainingSessionOverlap, handle_training_overlap)
    app.add_exception_handler(TrainingSessionInvalidTrainer, handle_invalid_trainer)


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


async def handle_absence_not_found(request: Request, exc: AbsenceNotFound):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Absence not found",
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
