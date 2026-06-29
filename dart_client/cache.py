"""Filesystem cache for raw DART API responses.

One JSON file per (corp_code, bsns_year, fs_div, reprt_code), storing an
envelope around the raw response so an empty/no-data result is distinguishable
from "never fetched" and is never refetched.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from config import settings


def cache_path(corp_code: str, bsns_year: str, fs_div: str, reprt_code: str) -> Path:
    return settings.dart_cache_dir / corp_code / str(bsns_year) / fs_div / f"{reprt_code}.json"


def get_or_fetch(
    corp_code: str,
    bsns_year: str,
    fs_div: str,
    reprt_code: str,
    fetch_fn: Callable[[], dict],
    force_refresh: bool = False,
) -> dict:
    path = cache_path(corp_code, bsns_year, fs_div, reprt_code)
    if path.exists() and not force_refresh:
        return json.loads(path.read_text(encoding="utf-8"))

    result = fetch_fn()
    envelope = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "request": {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "fs_div": fs_div,
            "reprt_code": reprt_code,
        },
        "status": result.get("status"),
        "message": result.get("message"),
        "list": result.get("list", []),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope, ensure_ascii=False), encoding="utf-8")
    return envelope


def is_cached(corp_code: str, bsns_year: str, fs_div: str, reprt_code: str) -> bool:
    return cache_path(corp_code, bsns_year, fs_div, reprt_code).exists()
