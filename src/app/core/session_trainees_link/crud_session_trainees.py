from src.app.core.crud.crud_base import CRUDBase
from src.app.schemas.training_sessions import (
    SessionTraineeAssignment,
)


class CRUDSessionTraineeAssignment(
    CRUDBase[
        SessionTraineeAssignment, SessionTraineeAssignment, SessionTraineeAssignment
    ]
): ...
