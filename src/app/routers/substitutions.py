from fastapi import APIRouter, Depends
from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    SubstitutionServiceDep,
    get_current_active_superuser,
    get_current_user,
)
from src.app.schemas.substitution_requests import (
    SubstitutionRequestCreate,
    SubstitutionRequestUpdate,
)

router = APIRouter(tags=["substitutions"])


@router.post("/v1/substitution-requests", dependencies=[Depends(get_current_user)])
def create_substitution_request(
    session: SessionDep,
    request: SubstitutionRequestCreate,
    substitution_service: SubstitutionServiceDep,
):
    return substitution_service.create_substitution_request(session, request)


@router.get(
    "/v1/substitution-requests/me",
    dependencies=[Depends(get_current_user)],
)
def get_self_substitutions_requests(
    session: SessionDep,
    current_user: CurrentUser,
    substitution_service: SubstitutionServiceDep,
):
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
def get_substitution_requests(
    session: SessionDep,
    request_id: int,
    substitution_service: SubstitutionServiceDep,
):
    return substitution_service.get_substitution_request(session, request_id)


@router.get(
    "/v1/substitution-requests",
    dependencies=[Depends(get_current_active_superuser)],
)
def get_all_substitutions(
    session: SessionDep,
    limit: int,
    offset: int,
    substitution_service: SubstitutionServiceDep,
):
    """
    Fetches all substitution requests, only available for superusers
    """
    return substitution_service.get_all_substitution_request(session, limit, offset)


@router.patch(
    "/v1/substitution-requests/{request_id}",
    dependencies=[Depends(get_current_user)],
)
def update_substitution(
    session: SessionDep,
    request_id: int,
    request_update: SubstitutionRequestUpdate,
    # trainer: Annotated[User, Security(get_current_user, scopes=["trainer"])],
    substitution_service: SubstitutionServiceDep,
):
    """Route to approve/decline substitution requests. If one request is approved, all other requests concerning the same available slot may be rejected."""
    return substitution_service.update_substitution_request(
        session, request_id, request_update
    )


@router.delete(
    "/v1/substitution-requests/{request_id}",
    dependencies=[Depends(get_current_user)],
)
def delete_substitution(
    session: SessionDep,
    request_id: int,
    current_user: CurrentUser,
    substitution_service: SubstitutionServiceDep,
):
    substitution_service.delete_substitution_request(session, request_id, current_user)
    return {"detail": "Deleted successfully"}
