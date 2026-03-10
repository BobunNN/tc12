from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from src.app.schemas.absences import Absences
from src.app.core.absences.absence_service import (
    open_absence_slot,
    get_all_absences_service,
    delete_absence_service,
    search_unique_absence,
)

router = APIRouter(tags=["absences"])


@router.post("/v1/absences")
def create_absence(session: SessionDep, absence: Absences, current_user: CurrentUser):
    print("YES")
    print(type(absence))
    print(type(absence.absence_date))
    return open_absence_slot(session, absence, current_user)


@router.get(
    "/v1/absences/me",
)
def get_self_absences(
    session: SessionDep,
    absence_id: int,
    current_user: CurrentUser,
):
    """
    If current user is trainee, returns his own absences, if current user is trainer returns
    the absences of the training session he is managing

    Args:
        session (SessionDep): _description_
        absence_id (int): _description_
        current_user (CurrentUser): _description_
    """
    ...  # TODO


@router.get(
    "/v1/absences/{training_id}/{traineed_id}/{absence_date}",
    dependencies=[Depends(get_current_active_superuser)],
)
def get_absence(
    session: SessionDep,
    trainee_id: int,
    training_id: int,
    training_date: datetime,
):
    return search_unique_absence(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=training_date,
    )


@router.get("/v1/absences", dependencies=[Depends(get_current_active_superuser)])
def get_all_absences(session: SessionDep):
    return get_all_absences_service(session)


@router.delete(
    "/v1/absences/{absence_id}",
)
def delete_absence(session: SessionDep, absence_id: int, current_user: CurrentUser):
    """
    Deletes an absence if the current user owens it

    Args:
        session (SessionDep): _description_
        absence_id (int): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    success = delete_absence_service(session, absence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Absence not found")
    return {"detail": "Deleted successfully"}
