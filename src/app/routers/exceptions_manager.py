from fastapi import FastAPI, HTTPException, Request, status

from src.app.core.users.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    SuperUserSelfDeleteForbidden,
    SelfDeleteNotAllowedHere,
)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(UserAlreadyExists, handle_user_already_exists)
    app.add_exception_handler(UserNotFound, handle_user_not_found)
    app.add_exception_handler(
        SuperUserSelfDeleteForbidden, handle_super_user_self_delete
    )
    app.add_exception_handler(SelfDeleteNotAllowedHere, handle_self_delete_not_allowed)


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
