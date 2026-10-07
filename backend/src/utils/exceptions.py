class LibraryError(Exception):
    """Base class for domain errors raised by the services."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(LibraryError):
    """Resource does not exist -> HTTP 404."""


class ConflictError(LibraryError):
    """Resource already exists / is in use -> HTTP 409."""


class BusinessRuleError(LibraryError):
    """A library rule prevents the action -> HTTP 400."""
