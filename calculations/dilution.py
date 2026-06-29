"""Share-count / dilution metrics from DART's 주식의 총수 현황 (stockTotqySttus).

Total issued common shares (istc_totqy for se == '보통주') is the cleanest
dilution signal: it rises with new issuance (rights offerings, CB/BW
conversions, stock options exercised) and falls when buybacks are cancelled.
Tracking its year-over-year change tells us how much existing holders are
being diluted (criterion 2: good investments dilute shareholders less).
"""

from __future__ import annotations

from dart_client.client import get_shares_outstanding


def _to_number(raw: object) -> float | None:
    if raw is None:
        return None
    s = str(raw).replace(",", "").strip()
    if s in ("", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def extract_common_shares(shares_body: dict) -> float | None:
    """Pull total issued common shares (보통주 발행주식의 총수) from a stockTotqySttus body."""
    if shares_body.get("status") != "000":
        return None
    for item in shares_body.get("list", []):
        if item.get("se") == "보통주":
            return _to_number(item.get("istc_totqy"))
    return None


def get_shares_for_year(corp_code: str, fiscal_year: int, reprt_code: str = "11011") -> float | None:
    body = get_shares_outstanding(corp_code, str(fiscal_year), reprt_code)
    return extract_common_shares(body)


def attach_share_changes(rows: list[dict]) -> list[dict]:
    """Given rows sorted ascending by fiscal_year, attach `share_count_change_yoy`
    (relative change in issued common shares vs prior year) in place.
    """
    rows_sorted = sorted(rows, key=lambda r: r["fiscal_year"])
    for i, row in enumerate(rows_sorted):
        curr = row.get("shares_outstanding")
        prev = rows_sorted[i - 1].get("shares_outstanding") if i > 0 else None
        if i > 0 and curr is not None and prev not in (None, 0):
            row["share_count_change_yoy"] = (curr - prev) / prev
        else:
            row["share_count_change_yoy"] = None
    return rows_sorted
