from datetime import datetime

from fastapi import APIRouter, Depends
from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from src.app.schemas.absences import AbsenceCreate
from src.app.core.absences.absence_service import (
    open_absence_slot,
    get_all_absences_service,
    delete_absence_service,
    search_unique_absence,
    get_self_absences,
)

router = APIRouter(tags=["absences"])


@router.post("/v1/absences")
def create_absence(
    session: SessionDep, absence: AbsenceCreate, current_user: CurrentUser
):
    return open_absence_slot(session, absence, current_user)


@router.get("/v1/absences/me")
def get_my_absences(
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    If current user is a trainee, returns their own absences.
    If current user is a trainer, returns absences for all sessions they manage.
    """
    return get_self_absences(session, current_user)


@router.get(
    "/v1/absences/{training_id}/{trainee_id}/{absence_date}",
    dependencies=[Depends(get_current_active_superuser)],
)
def get_absence(
    session: SessionDep,
    training_id: int,
    trainee_id: int,
    absence_date: datetime,
):
    return search_unique_absence(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=absence_date,
    )


@router.get("/v1/absences", dependencies=[Depends(get_current_active_superuser)])
def get_all_absences(session: SessionDep):
    return get_all_absences_service(session)


@router.delete("/v1/absences/{training_id}/{trainee_id}/{absence_date}")
def delete_absence(
    session: SessionDep,
    training_id: int,
    trainee_id: int,
    absence_date: datetime,
    current_user: CurrentUser,
):
    """
    Deletes an absence. The current user must be the trainee who owns the absence
    or a superuser.
    """
    delete_absence_service(
        session,
        trainee_id=trainee_id,
        training_id=training_id,
        training_date=absence_date,
        current_user=current_user,
    )
    return {"detail": "Deleted successfully"}
