from src.app.core.crud.crud_base import CRUDBase
from src.app.schemas.substitution_requests import (
    SubstitutionRequestCreate,
    SubstitutionRequestUpdate,
    SubstitutionRequests,
)


class CrudSubstitutions(
    CRUDBase[SubstitutionRequests, SubstitutionRequestCreate, SubstitutionRequestUpdate]
):
    pass
