class UserAlreadyExists(Exception):
    """Raised when attempting to create a user that already exists."""

    ...


class UserNotFound(Exception):
    """Raised when a user cannot be found in the database."""

    ...


class SuperUserSelfDeleteForbidden(Exception):
    """Raised when a superuser attempts to delete their own account, which is forbidden."""

    ...


class SelfDeleteNotAllowedHere(Exception):
    """Raised when self-deletion is not allowed in the current context."""

    ...


class IncorrectPassword(Exception):
    """Raised when the provided password is incorrect."""

    ...


class NewPasswordCannotBeTheSameAsTheCurrentOne(Exception):
    """Raised when the new password is the same as the current one."""

    ...
