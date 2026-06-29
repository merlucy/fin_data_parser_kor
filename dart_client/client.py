from __future__ import annotations

import requests

from config import settings
from dart_client import cache, rate_limiter
from dart_client.endpoints import (
    FNLTT_SINGL_ACNT_ALL_URL,
    STATUS_AUTH_ERROR,
    STATUS_FIELD_ERROR,
    STATUS_NO_DATA,
    STATUS_OK,
    STATUS_TRANSIENT,
)
from dart_client.errors import DartAuthError, DartFieldError, DartTransientError
from dart_client.retry import dart_retry


@dart_retry
def _raw_get_financial_statements(corp_code: str, bsns_year: str, fs_div: str, reprt_code: str) -> dict:
    rate_limiter.throttle()
    resp = requests.get(
        FNLTT_SINGL_ACNT_ALL_URL,
        params={
            "crtfc_key": settings.dart_api_key,
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "fs_div": fs_div,
        },
        timeout=30,
    )
    resp.raise_for_status()
    rate_limiter.record_call()
    body = resp.json()
    status = body.get("status")

    if status == STATUS_OK or status == STATUS_NO_DATA:
        return body
    if status == STATUS_FIELD_ERROR:
        raise DartFieldError(status, body.get("message", ""))
    if status == STATUS_AUTH_ERROR:
        raise DartAuthError(status, body.get("message", ""))
    if status in STATUS_TRANSIENT:
        raise DartTransientError(status, body.get("message", ""))
    # Anything else (including 020 rate-limit) surfaces as a generic transient
    # error so callers see it clearly rather than silently treating it as no-data.
    raise DartTransientError(status, body.get("message", ""))


def get_financial_statements(
    corp_code: str, bsns_year: str, fs_div: str, reprt_code: str, force_refresh: bool = False
) -> dict:
    """Fetch (or read from cache) the full financial statements for one company-year-basis.

    Checks the daily call limit before any potential live call, but a cache
    hit never counts against the limit or triggers the check.
    """
    if force_refresh or not cache.is_cached(corp_code, bsns_year, fs_div, reprt_code):
        rate_limiter.check_daily_limit()

    return cache.get_or_fetch(
        corp_code,
        bsns_year,
        fs_div,
        reprt_code,
        fetch_fn=lambda: _raw_get_financial_statements(corp_code, bsns_year, fs_div, reprt_code),
        force_refresh=force_refresh,
    )
