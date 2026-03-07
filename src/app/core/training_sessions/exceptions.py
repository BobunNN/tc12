class TrainingSessionAlreadyExists(Exception):
    """Raised when attempting to create a training session that already exists."""
    ...

class TrainingSessionNotFound(Exception):
    """Raised when a training session cannot be found in the database."""
    ...

class AbsenceAlreadyExists(Exception):
    """Raised when attempting to create an absence that already exists."""
    ...

class AbsenceNotFound(Exception):
    """Raised when an absence cannot be found in the database."""
    ...