"""Fetch the bulk listed-company directory (with industry classification) from KIND.

data.krx.co.kr's JSON API (which `pykrx` relies on for KRX's WICS-style
업종분류현황) is blocked from this environment's network (verified: returns
HTTP 400 "LOGOUT" regardless of cookies/referer). KIND's bulk corp list
download is reachable and returns the same kind of ticker -> industry
mapping (KSIC-based 업종 names) in a single request, so we use that instead.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import pandas as pd
import requests

KIND_CORP_LIST_URL = "https://kind.krx.co.kr/corpgeneral/corpList.do"

_MARKET_TYPE_MAP = {
    "stockMkt": "KOSPI",
    "kosdaqMkt": "KOSDAQ",
    "konexMkt": "KONEX",
}


@dataclass(frozen=True)
class KrxListing:
    stock_code: str
    corp_name: str
    market: str
    industry: str | None


def _fetch_market(market_type: str) -> pd.DataFrame:
    resp = requests.post(
        KIND_CORP_LIST_URL,
        data={"method": "download", "orderMode": "1", "orderStat": "D", "marketType": market_type},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    resp.raise_for_status()
    resp.encoding = "euc-kr"
    tables = pd.read_html(io.StringIO(resp.text))
    return tables[0]


def fetch_listed_companies() -> list[KrxListing]:
    """Fetch all KOSPI + KOSDAQ listed companies with industry classification."""
    listings: list[KrxListing] = []
    for market_type, market_name in _MARKET_TYPE_MAP.items():
        if market_name == "KONEX":
            continue  # out of scope: KONEX names are mostly illiquid/early-stage, skip for screening
        df = _fetch_market(market_type)
        for _, row in df.iterrows():
            stock_code = str(row["종목코드"]).strip().zfill(6)
            listings.append(
                KrxListing(
                    stock_code=stock_code,
                    corp_name=str(row["회사명"]).strip(),
                    market=market_name,
                    industry=(str(row["업종"]).strip() if pd.notna(row.get("업종")) else None),
                )
            )
    return listings
