from src.app.core.crud.crud_base import CRUDBase
from src.app.schemas.training_sessions import (
    SessionTraineesLink,
)


class CRUDSessionTraineesLink(
    CRUDBase[SessionTraineesLink, SessionTraineesLink, SessionTraineesLink]
): ...
