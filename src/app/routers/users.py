from typing import Any

from fastapi import APIRouter, Depends
from pydantic import EmailStr

from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    UserServiceDep,
    get_current_active_superuser,
)

from src.app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)


router = APIRouter(tags=["users"])


@router.get("/v1/users", dependencies=[Depends(get_current_active_superuser)])
async def read_users(
    session: SessionDep,
    user_service: UserServiceDep,
    limit: int = 100,
    offset: int = 0,
):
    """
    Retrieve a list of users with pagination. Requires superuser privileges.
    """
    return user_service.get_all_users(session=session, limit=limit, offset=offset)


@router.get(
    "/v1/users/me",
)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/v1/users/{email}", dependencies=[Depends(get_current_active_superuser)])
def fetch_user(
    session: SessionDep,
    email: EmailStr,
    user_service: UserServiceDep,
):
    """
    Retrieve a user by email. Requires superuser privileges.
    """
    return user_service.get_user_by_email(session=session, email=email)


@router.post("/v1/users", dependencies=[Depends(get_current_active_superuser)])
def create_user(
    session: SessionDep,
    user_create: UserCreate,
    user_service: UserServiceDep,
):
    """
    Create a new user. Requires superuser privileges.
    """
    return user_service.create_user(session=session, user_create=user_create)


@router.patch("/v1/users/me")
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> Any:
    """
    Update own user.
    """
    return user_service.update_user_me(
        session=session, user_in=user_in, current_user=current_user
    )


@router.patch("/v1/users/{email}", dependencies=[Depends(get_current_active_superuser)])
def patch_user(
    session: SessionDep,
    user_patch: UserUpdate,
    email: EmailStr,
    user_service: UserServiceDep,
):
    """
    Update a user by email. Requires superuser privileges.
    """
    return user_service.patch_user(session=session, user_patch=user_patch, email=email)


@router.delete(
    "/v1/users/me",
)
def delete_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> Any:
    """
    Delete own user.
    """
    user_service.delete_me(session=session, current_user=current_user)
    return "User deleted successfully"


@router.delete(
    "/v1/users/{email}", dependencies=[Depends(get_current_active_superuser)]
)
def delete_user(
    session: SessionDep,
    email: EmailStr,
    current_user: CurrentUser,
    user_service: UserServiceDep,
):
    """
    Delete a user by email. Requires superuser privileges.
    """
    return user_service.delete_user(
        session=session, email=email, current_user=current_user
    )


@router.patch("/v1/users/me/password")
def update_password_me(
    *,
    session: SessionDep,
    body: UpdatePassword,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> Any:
    """
    Update own password.
    """
    user_service.update_password_me(
        session=session, body=body, current_user=current_user
    )
    return "Password updated successfully"


@router.post(
    "/v1/users/signup",
)
def register_user(
    session: SessionDep,
    user_in: UserRegister,
    user_service: UserServiceDep,
) -> Any:
    """
    Create new user without the need to be logged in.
    """

    return user_service.register_user(session=session, user_in=user_in)
