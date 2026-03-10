from sqlmodel import Session, select
from src.app.schemas.substitution_requests import SubstitutionRequests


def create_substitution_request(
    session: Session, request_create: SubstitutionRequests
) -> SubstitutionRequests:
    db_obj = SubstitutionRequests.model_validate(request_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_substitution_request_by_id(
    session: Session, request_id: int
) -> SubstitutionRequests | None:
    statement = select(SubstitutionRequests).where(
        SubstitutionRequests.id == request_id
    )
    return session.exec(statement).first()


def get_all_substitution_requests(
    session: Session, offset: int = 0, limit: int = 100
) -> list[SubstitutionRequests]:
    statement = select(SubstitutionRequests).offset(offset).limit(limit)
    return session.exec(statement).all()


def update_substitution_request(
    session: Session, db_request: SubstitutionRequests, request_update: dict
) -> SubstitutionRequests:
    db_request.sqlmodel_update(request_update)
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request


def delete_substitution_request(session: Session, request_id: int) -> bool:
    db_request = get_substitution_request_by_id(session, request_id)
    if db_request:
        session.delete(db_request)
        session.commit()
        return True
    return False


def get_substitution_requests_with_filters(
    session: Session,
    filters: dict,
    offset: int = 0,
    limit: int = 100
) -> list[SubstitutionRequests]:
    """
    Fetch substitution requests with filters.

    Args:
        session (Session): SQLModel session.
        filters (dict): Dictionary of filters where keys are column names of SubstitutionRequests and values are the values to filter by.
            Example: {"user_id": 123, "status": "pending"}
        offset (int): Pagination offset.
        limit (int): Pagination limit.

    Returns:
        list[SubstitutionRequests]: List of filtered substitution requests.

    Note:
        Only exact matches are supported. Keys must correspond to valid SubstitutionRequests attributes.
    """
    statement = select(SubstitutionRequests)
    for key, value in filters.items():
        column = getattr(SubstitutionRequests, key, None)
        if column is not None:
            statement = statement.where(column == value)
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()
