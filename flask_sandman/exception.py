"""JSON-based Exception classes which generate proper HTTP Status Codes."""


class EndpointException(Exception):
    """Base class for all Exceptions."""

    def __init__(self, message=None, payload=None):
        super(EndpointException, self).__init__(message)
        self.message = message
        self.payload = payload

    def to_dict(self):
        """Return a dictionary representation of the exception."""
        as_dict = dict(self.payload or ())
        as_dict['message'] = self.message
        return as_dict


class BadRequestException(EndpointException):
    """Raised when a request contains illegal arguments, is missing arguments,
    can't be decoded properly, or the request is trying to do something that
    doesn't make sense."""

    code = 400


class ForbiddenException(EndpointException):
    """Raised when a request asks us to do something that we won't do because it
    violates the application logic.
    *Does not refer to an authentication failure.* Rather, it means the action
    requested is forbidden by the application."""

    code = 403


class NotFoundException(EndpointException):
    """Raised when the endpoint (or a resource it refers to) is not found. Can
    also be used if a resource referred to in a request (e.g. a specific job in
    a /job_status request) can not be found."""

    code = 404


class NotAcceptableException(EndpointException):
    """Raised when the client does not Accept any of the Content-Types we are
    capable of generating."""

    code = 406


class ConflictException(EndpointException):
    """Similar to a ServerErrorException (HTTP 500) but there is some action the
    client may take to resolve the conflict, after which the request can be
    resubmitted. A request to reprocess a job not marked for reprocessing, for
    example, could cause this exception to be raised."""

    code = 409


class ServerErrorException(EndpointException):
    """Raised when the application itself encounters an error not related to the
    request itself (for example, a database error)."""

    code = 500


class NotImplementedException(EndpointException):
    """Raised when the application does not implement the functionality being
    requested. Note that this doesn't refer to an HTTP method not being
    implemented for a given endpoint (which would be a 405 error)."""

    code = 501


class ServiceUnavailableException(EndpointException):
    """Raised when a resource is temporarily unavailable (e.g. not being able to
    get a database connection). Setting the *Retry-After* header gives the
    length of the delay, if it is known. Otherwise, this is treated as a 500
    error."""

    code = 503
