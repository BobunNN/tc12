from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from src.app.schemas.training_sessions import Absences
from src.app.core.absences.absence_service import (
    create_absence_service,
    get_all_absences_service,
    delete_absence_service,
    search_unique_absence,
)

router = APIRouter(tags=["absences"])


@router.post("/v1/absences")
def create_absence(session: SessionDep, absence: Absences, current_user: CurrentUser):
    return create_absence_service(session, absence, current_user)


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
    absence_id: int,
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


@router.delete("/v1/absences/{absence_id}", dependencies=[Depends(get_current_user)])
def delete_absence(session: SessionDep, absence_id: int):
    success = delete_absence_service(session, absence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Absence not found")
    return {"detail": "Deleted successfully"}
