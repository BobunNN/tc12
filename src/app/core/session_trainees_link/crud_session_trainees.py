from src.app.core.crud.crud_base import CRUDBase
from src.app.schemas.training_sessions import (
    SessionTraineeAssignement,
)


class CRUDSessionTraineeAssignment(
    CRUDBase[
        SessionTraineeAssignement, SessionTraineeAssignement, SessionTraineeAssignement
    ]
): ...
