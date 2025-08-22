class AuthorizationFailedExcepion(Exception):
    """Exception raised when authorization fails."""


class BadRequestException(Exception):
    """Exception raised for bad requests."""


class UpdateFailed(Exception):
    """Exception raised when updating the lock fails."""
