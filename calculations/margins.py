"""Margin ratios (operating margin, net margin) and their year-over-year change.

Margin change is an additive delta in percentage points (e.g. 15% -> 18% is
"+3.0pp"), not a relative growth rate - relative growth doesn't make sense
for a ratio that's already a percentage, and it lets us directly answer
"did margins expand or contract alongside revenue/profit growth".
"""

from __future__ import annotations

MARGIN_FIELDS = ["gross_margin", "operating_margin", "net_margin"]


def _margin(numerator: float | None, revenue: float | None) -> float | None:
    if numerator is None or revenue is None or revenue <= 0:
        return None
    return numerator / revenue


def compute(row: dict) -> dict:
    revenue = row.get("revenue")
    return {
        "gross_margin": _margin(row.get("gross_profit"), revenue),
        "operating_margin": _margin(row.get("operating_income"), revenue),
        "net_margin": _margin(row.get("net_income"), revenue),
    }


def attach_margin_changes(rows: list[dict]) -> list[dict]:
    """Given rows sorted ascending by fiscal_year (one dict per year, same corp),
    attach `<field>_change_yoy` (delta in percentage points) in place.
    """
    rows_sorted = sorted(rows, key=lambda r: r["fiscal_year"])

    for field in MARGIN_FIELDS:
        for i, row in enumerate(rows_sorted):
            curr = row.get(field)
            prev = rows_sorted[i - 1].get(field) if i > 0 else None
            row[f"{field}_change_yoy"] = (curr - prev) if (i > 0 and curr is not None and prev is not None) else None

    return rows_sorted
