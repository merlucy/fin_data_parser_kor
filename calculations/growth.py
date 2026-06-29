"""YoY and CAGR growth metrics computed across a multi-year series of CompanyYearMetrics-like dicts."""

from __future__ import annotations

GROWTH_FIELDS = ["gross_profit", "operating_income", "net_income"]


def _yoy(curr: float | None, prev: float | None) -> float | None:
    if curr is None or prev is None or prev == 0:
        return None
    return (curr - prev) / abs(prev)


def _cagr(first: float | None, last: float | None, years: int) -> float | None:
    if first is None or last is None or first <= 0 or last <= 0 or years <= 0:
        return None
    return (last / first) ** (1 / years) - 1


def attach_growth_metrics(rows: list[dict]) -> list[dict]:
    """Given rows sorted ascending by fiscal_year (one dict per year, same corp),
    attach `<field>_growth_yoy` and `<field>_cagr_5y` keys in place.
    """
    rows_sorted = sorted(rows, key=lambda r: r["fiscal_year"])
    n_years = len(rows_sorted) - 1

    for field in GROWTH_FIELDS:
        for i, row in enumerate(rows_sorted):
            prev = rows_sorted[i - 1].get(field) if i > 0 else None
            row[f"{field}_growth_yoy"] = _yoy(row.get(field), prev) if i > 0 else None

        if n_years > 0:
            cagr = _cagr(rows_sorted[0].get(field), rows_sorted[-1].get(field), n_years)
        else:
            cagr = None
        for row in rows_sorted:
            row[f"{field}_cagr_5y"] = cagr

    return rows_sorted
