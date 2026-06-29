class DartApiError(Exception):
    """Base class for all DART API errors. Carries the DART status/message."""

    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message
        super().__init__(f"DART status {status}: {message}")


class DartFieldError(DartApiError):
    """status 100 - bad request params. Indicates a bug in our request, do not retry."""


class DartAuthError(DartApiError):
    """status 800 - invalid/unregistered API key. Fatal, abort."""


class DartTransientError(DartApiError):
    """status 900/901 - undefined/transient server-side error. Safe to retry with backoff."""


class DartRateLimitError(DartApiError):
    """status 020 - daily call quota exceeded on DART's side.

    This should never happen in normal operation since DartDailyLimitReached
    is raised by our own rate_limiter before the call is even made; seeing this
    means our local counter and DART's actual quota have drifted.
    """


class DartDailyLimitReached(Exception):
    """Raised by rate_limiter before issuing a live call once our configured daily cap is hit."""
