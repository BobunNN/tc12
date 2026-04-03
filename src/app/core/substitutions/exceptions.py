class SubstitutionRequestAlreadyExists(Exception):
    """Raised when attempting to create a substitution request that already exists."""

    ...


class SubstitutionRequestNotFound(Exception):
    """Raised when a substitution request cannot be found in the database."""

    ...


class TrainerDoesNotManageSubstitutionSession(Exception):
    """Raised when the trainer does not manage the training session linked to the substitution request."""

    ...


class SubstitutionRequestAlreadyReviewed(Exception):
    """Raised when attempting to approve or reject a substitution request that has already been reviewed."""

    ...
