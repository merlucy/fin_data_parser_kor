"""Conservative throttling for live DART API calls.

Two layers:
1. A fixed delay between consecutive live calls (cache hits skip this entirely).
2. A daily call counter persisted in Postgres (dart_api_call_log), checked
   *before* issuing a live call. We deliberately stop ourselves well before
   ever triggering DART's own status=020 "quota exceeded" response.
"""

from __future__ import annotations

import time

from config import settings
from dart_client.errors import DartDailyLimitReached
from db.repository import get_today_call_count, increment_call_count

_last_call_ts: float | None = None


def check_daily_limit() -> None:
    count = get_today_call_count()
    if count >= settings.dart_daily_call_limit:
        raise DartDailyLimitReached(
            f"Daily DART call limit reached ({count}/{settings.dart_daily_call_limit}). Resume tomorrow."
        )


def throttle() -> None:
    """Sleep just enough to respect the configured delay since the last live call."""
    global _last_call_ts
    if _last_call_ts is not None:
        elapsed = time.monotonic() - _last_call_ts
        remaining = settings.dart_request_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
    _last_call_ts = time.monotonic()


def record_call() -> int:
    return increment_call_count()
