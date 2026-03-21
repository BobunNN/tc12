from fastapi import APIRouter, Depends, Security
from src.app.dependencies import (
    SessionDep,
    TrainingSessionServiceDep,
    get_current_user,
)
from src.app.schemas.training_sessions import (
    TrainingSessionCreate,
    TrainingSessionPublic,
    TrainingSessionUpdate,
)


router = APIRouter(tags=["training_sessions"])


@router.post(
    "/v1/training-sessions",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
    response_model=TrainingSessionPublic,
)
def create_training_session(
    session: SessionDep,
    session_create: TrainingSessionCreate,
    training_session_service: TrainingSessionServiceDep,
):
    return training_session_service.create_training_session(
        session=session, session_create=session_create
    )


@router.get(
    "/v1/training-sessions/{session_id}",
    dependencies=[Depends(get_current_user)],
    response_model=TrainingSessionPublic,
)
def get_training_session(
    session: SessionDep,
    session_id: int,
    training_session_service: TrainingSessionServiceDep,
):
    return training_session_service.get_training_session(session, session_id)


@router.get(
    "/v1/training-sessions",
    dependencies=[Depends(get_current_user)],
    response_model=list[TrainingSessionPublic],
)
def get_all_training_sessions(
    session: SessionDep,
    training_session_service: TrainingSessionServiceDep,
    offset: int = 0,
    limit: int = 100,
):
    return training_session_service.get_all_training_session(session, offset, limit)


@router.patch(
    "/v1/training-sessions/{session_id}",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
    response_model=TrainingSessionPublic,
)
def update_training_session(
    session: SessionDep,
    session_id: int,
    session_update: TrainingSessionUpdate,
    training_session_service: TrainingSessionServiceDep,
):
    return training_session_service.update_training_session(
        session=session, session_id=session_id, session_update=session_update
    )


@router.delete(
    "/v1/training-sessions/{session_id}",
    dependencies=[Security(get_current_user, scopes=["trainer"])],
)
def delete_training_session(
    session: SessionDep,
    session_id: int,
    training_session_service: TrainingSessionServiceDep,
):
    return training_session_service.remove_training_session(session, session_id)
