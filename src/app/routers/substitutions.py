from typing import Annotated

from fastapi import APIRouter, Depends, Security
from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from src.app.schemas.training_sessions import SubstitutionRequests
from src.app.core.substitutions import substitution_service
from src.app.schemas.user import User

router = APIRouter(tags=["substitutions"])


@router.post("/v1/substitution-requests", dependencies=[Depends(get_current_user)])
def create_substitution_request(session: SessionDep, request: SubstitutionRequests):
    return substitution_service.create_substitution_request(session, request)


@router.get(
    "/v1/substitution-requests/me",
)
def get_self_substitutions_requests(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve substitution requests relevant to the current user.

    - If the user is a trainer, returns substitution requests for training sessions they manage.
    - If the user is a trainee, returns substitution requests they have submitted themselves.

    Args:
        session (SessionDep): Database session dependency.
        current_user (CurrentUser): The authenticated user (trainer or trainee).

    Returns:
        List of SubstitutionRequests relevant to the user's role.
    """
    return substitution_service.get_self_substitution_requests(
        session=session, current_user=current_user
    )


@router.get(
    "/v1/substitution-requests/{request_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def get_substitution_requests(session: SessionDep, request_id: int):
    return substitution_service.get_substitution_request(session, request_id)


@router.get(
    "/v1/substitution-requests",
    dependencies=[Depends(get_current_active_superuser)],
)
def get_all_substitutions(session: SessionDep, limit: int, offset: int):
    """
    Fetches all substitution requests, only available for superusers
    """
    return substitution_service.get_all_substitution_request(session, limit, offset)


@router.patch(
    "/v1/substitution-requests/{request_id}",
)
async def update_substitution(
    session: SessionDep,
    request_id: int,
    request_update: dict,
    trainer: Annotated[User, Security(get_current_user, scopes=["trainer"])],
):
    """Route to approve/decline substitution requests. If one request is approved, all other requests concerning the same available

    Args:
        session (SessionDep): _description_
        request_id (int): _description_
        request_update (dict): _description_
        trainer (Annotated[User, Security, optional): _description_. Defaults to ["trainer"])].
    """
    ...  # TODO
    # return substitution_service.update_substitution_request(
    #     session, db_request, request_update
    # )


@router.delete("/v1/substitution-requests/{request_id}")
def delete_substitution(
    session: SessionDep, request_id: int, current_user: CurrentUser
):
    ...  # TODO
    # success = crud_substitutions.delete_substitution_request(session, request_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Substitution request not found")
    # return {"detail": "Deleted successfully"}
