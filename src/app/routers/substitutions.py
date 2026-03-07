from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from src.app.dependencies import SessionDep
from src.app.schemas.training_sessions import SubstitutionRequests
from src.app.core.substitutions import substitution_service, crud_substitutions

router = APIRouter(tags=["substitutions"])

@router.post("/v1/substitutions")
def create_substitution(session: SessionDep, request: SubstitutionRequests):
    return substitution_service.create_substitution_request(session, request)

@router.get("/v1/substitutions/{request_id}")
def get_substitution(session: SessionDep, request_id: int):
    return substitution_service.get_substitution_request(session, request_id)

@router.get("/v1/substitutions")
def get_all_substitutions(session: SessionDep, offset: int = 0, limit: int = 100):
    return crud_substitutions.get_all_substitution_requests(session, offset, limit)

@router.patch("/v1/substitutions/{request_id}")
def update_substitution(session: SessionDep, request_id: int, request_update: dict):
    db_request = substitution_service.get_substitution_request(session, request_id)
    return substitution_service.update_substitution_request(session, db_request, request_update)

@router.delete("/v1/substitutions/{request_id}")
def delete_substitution(session: SessionDep, request_id: int):
    success = crud_substitutions.delete_substitution_request(session, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Substitution request not found")
    return {"detail": "Deleted successfully"}
