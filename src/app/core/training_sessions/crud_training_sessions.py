from src.app.core.crud.crud_base import CRUDBase
from src.app.schemas.training_sessions import (
    TrainingSessionCreate,
    TrainingSessions,
    TrainingSessionUpdate,
)


class CRUDTrainingSessions(
    CRUDBase[TrainingSessions, TrainingSessionCreate, TrainingSessionUpdate]
): ...
