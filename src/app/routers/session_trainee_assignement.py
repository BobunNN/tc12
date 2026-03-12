from fastapi import APIRouter, Depends, Security
from src.app.dependencies import (
    CurrentUser,
    SessionDep,
    SessionTraineeLinkServiceDep,
    get_current_user,
)


router = APIRouter(tags=["session_trainee_assignement"])


@router.post(
    "/v1/session-trainee-assignement",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
)
def create_session_trainee_link(
    session: SessionDep,
    session_id: int,
    trainee_id: int,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
):
    return session_trainee_link_service.create_session_trainees_link(
        session=session, session_id=session_id, trainee_id=trainee_id
    )


@router.get(
    "/v1/session-trainee-assignement/{session_id}",
    dependencies=[Depends(get_current_user)],
)
def get_session_trainees(
    session: SessionDep,
    session_id: int,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
):
    return session_trainee_link_service.get_session_trainees(session, session_id)


@router.get(
    "/v1/session-trainee-assignement/user/me",
)
def get_self_sessions(
    session: SessionDep,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
    current_user: CurrentUser,
):
    return session_trainee_link_service.get_self_training_session(session, current_user)


@router.get(
    "/v1/session-trainee-assignement/user/{trainee_id}",
    dependencies=[Depends(get_current_user)],
)
def get_user_sessions(
    session: SessionDep,
    trainee_id: int,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
):
    return session_trainee_link_service.get_user_session(session, trainee_id)


@router.delete(
    "/v1/session-trainee-assignement/{session_id}/{trainee_id}",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
)
def delete_session_trainee_link(
    session: SessionDep,
    session_id: int,
    trainee_id: int,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
):
    session_trainee_link_service.delete_session_trainees_link(
        session=session, session_id=session_id, trainee_id=trainee_id
    )
    return {"detail": "Deleted successfully"}


@router.get(
    "/v1/session-trainee-assignement",
    dependencies=[Depends(get_current_user)],
)
def get_all_assignements(
    session: SessionDep,
    session_trainee_link_service: SessionTraineeLinkServiceDep,
):
    return session_trainee_link_service.get_all(session)
