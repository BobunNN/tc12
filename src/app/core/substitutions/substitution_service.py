from sqlmodel import Session
from fastapi import HTTPException
from src.app.core.substitutions.exceptions import (
    SubstitutionRequestAlreadyExists,
    SubstitutionRequestNotFound,
)
from src.app.core.substitutions import crud_substitutions
from src.app.schemas.training_sessions import SubstitutionRequests


def create_substitution_request(
    session: Session, request_create: SubstitutionRequests
) -> SubstitutionRequests:
    existing = crud_substitutions.get_substitution_request_by_id(
        session, request_create.id
    )
    if existing:
        raise SubstitutionRequestAlreadyExists
    return crud_substitutions.create_substitution_request(session, request_create)


def get_substitution_request(session: Session, request_id: int) -> SubstitutionRequests:
    request_obj = crud_substitutions.get_substitution_request_by_id(session, request_id)
    if not request_obj:
        raise SubstitutionRequestNotFound
    return request_obj


def update_substitution_request(
    session: Session, db_request: SubstitutionRequests, request_update: dict
) -> SubstitutionRequests:
    return crud_substitutions.update_substitution_request(
        session, db_request, request_update
    )


def delete_substitution_request(session: Session, request_id: int) -> bool:
    return crud_substitutions.delete_substitution_request(session, request_id)
