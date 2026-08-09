class AppException(Exception):
    """Base application exception."""


class NotFoundException(AppException):
    """Raised when a record cannot be found."""


class UnauthorizedException(AppException):
    """Raised when a request is unauthorized."""


class ForbiddenException(AppException):
    """Raised when a request is forbidden."""


class ConflictException(AppException):
    """Raised when a resource conflicts with existing state."""


class ValidationException(AppException):
    """Raised when domain validation fails."""


class ExternalServiceException(AppException):
    """Raised when an external dependency fails."""
