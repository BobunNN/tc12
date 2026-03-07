from fastapi import APIRouter, HTTPException
from src.app.dependencies import SessionDep, TrainerScope
from src.app.schemas.training_sessions import TrainingSessions
from src.app.core.training_sessions import (
    training_session_service,
    crud_training_sessions,
)

router = APIRouter(tags=["training_sessions"])


@router.post("/v1/training_sessions", dependencies=[TrainerScope])
def create_training_session(
    session: SessionDep,
    session_create: TrainingSessions,
):
    return training_session_service.create_training_session(session, session_create)


@router.get("/v1/training_sessions/{session_id}")
def get_training_session(session: SessionDep, session_id: int):
    return training_session_service.get_training_session(session, session_id)


@router.get("/v1/training_sessions")
def get_all_training_sessions(session: SessionDep, offset: int = 0, limit: int = 100):
    return crud_training_sessions.get_all_training_sessions(session, offset, limit)


@router.patch("/v1/training_sessions/{session_id}")
def update_training_session(session: SessionDep, session_id: int, session_update: dict):
    db_session = training_session_service.get_training_session(session, session_id)
    return crud_training_sessions.update_training_session(
        session, db_session, session_update
    )


@router.delete("/v1/training_sessions/{session_id}")
def delete_training_session(session: SessionDep, session_id: int):
    success = crud_training_sessions.delete_training_session(session, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Training session not found")
    return {"detail": "Deleted successfully"}
