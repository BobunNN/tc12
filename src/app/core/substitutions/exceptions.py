class SubstitutionRequestAlreadyExists(Exception):
    """Raised when attempting to create a substitution request that already exists."""
    ...

class SubstitutionRequestNotFound(Exception):
    """Raised when a substitution request cannot be found in the database."""
    ...