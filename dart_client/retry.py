"""Retry/backoff for transient failures only.

Retries on: connection errors, timeouts, HTTP 5xx, DART status 900/901.
Does NOT retry on: 013 (no data - legitimate), 100 (bad params - our bug),
800 (bad key - fatal), 020 (quota - handled by the daily-limit short-circuit
in rate_limiter instead of blind retry).
"""

from __future__ import annotations

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from dart_client.errors import DartTransientError

RETRYABLE_EXCEPTIONS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    DartTransientError,
)

dart_retry = retry(
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    wait=wait_exponential_jitter(initial=1, max=20),
    stop=stop_after_attempt(4),
    reraise=True,
)
