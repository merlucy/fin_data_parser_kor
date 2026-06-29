"""Three-pillar investment scorecard, mapping directly to the screening criteria:

  Pillar 1 — Margin & Growth: 5-year gross AND operating margin expansion,
             coinciding with meaningful revenue and profit growth.
  Pillar 2 — Low Dilution: little/no increase in issued shares over 5 years and
             no outstanding convertible instruments.
  Pillar 3 — Capital Efficiency: reinvesting (capex) and generating free cash
             flow with profit growth, WITHOUT increasing debt.

Each pillar scores 0 (fail) / 1 (partial) / 2 (strong), or None when the
underlying data is entirely missing. Window-level deltas used by the pillars
are also attached so the UI can show the evidence behind each score.
Scores are attached to every year row (repeated), like the *_cagr_5y fields.
"""

from __future__ import annotations

REVENUE_GROWTH_THRESHOLD = 0.05  # >5% CAGR counts as "meaningful" revenue growth
PROFIT_GROWTH_THRESHOLD = 0.05  # >5% CAGR counts as "meaningful" profit growth
DILUTION_TOLERANCE = 0.02  # <=2% share-count increase over the window is "not dilutive"
DEBT_INCREASE_TOLERANCE = 0.05  # <=5% debt increase over the window is "not rising"


def _first_last(rows: list[dict], field: str) -> tuple[float | None, float | None]:
    vals = [(r["fiscal_year"], r.get(field)) for r in rows if r.get(field) is not None]
    if not vals:
        return None, None
    vals.sort(key=lambda x: x[0])
    return vals[0][1], vals[-1][1]


def _rel_change(first: float | None, last: float | None) -> float | None:
    if first is None or last is None or first == 0:
        return None
    return (last - first) / abs(first)


def _abs_change(first: float | None, last: float | None) -> float | None:
    if first is None or last is None:
        return None
    return last - first


def _score_groups(groups: list[bool]) -> int:
    """2 = every condition group satisfied, 1 = some, 0 = none."""
    if all(groups):
        return 2
    if any(groups):
        return 1
    return 0


def attach_scores(rows: list[dict]) -> list[dict]:
    rows_sorted = sorted(rows, key=lambda r: r["fiscal_year"])
    latest = rows_sorted[-1]

    # --- window-level evidence ---
    gm_first, gm_last = _first_last(rows_sorted, "gross_margin")
    om_first, om_last = _first_last(rows_sorted, "operating_margin")
    nm_first, nm_last = _first_last(rows_sorted, "net_margin")
    sh_first, sh_last = _first_last(rows_sorted, "shares_outstanding")
    debt_first, debt_last = _first_last(rows_sorted, "total_debt")

    gross_margin_change_5y = _abs_change(gm_first, gm_last)
    operating_margin_change_5y = _abs_change(om_first, om_last)
    net_margin_change_5y = _abs_change(nm_first, nm_last)
    share_count_change_5y = _rel_change(sh_first, sh_last)
    total_debt_change_5y = _rel_change(debt_first, debt_last)

    revenue_cagr = latest.get("revenue_cagr_5y")
    op_income_cagr = latest.get("operating_income_cagr_5y")

    # --- Pillar 1: Margin & Growth ---
    # Two condition groups: (a) margins expanded (operating AND gross where available),
    # (b) revenue AND profit grew meaningfully.
    p1_inputs = [gross_margin_change_5y, operating_margin_change_5y, revenue_cagr, op_income_cagr]
    if all(v is None for v in p1_inputs):
        score_margin_growth = None
    else:
        avail_margin_changes = [c for c in (gross_margin_change_5y, operating_margin_change_5y) if c is not None]
        margins_expanded = (
            operating_margin_change_5y is not None
            and len(avail_margin_changes) > 0
            and all(c > 0 for c in avail_margin_changes)
        )
        grew_meaningfully = (
            revenue_cagr is not None
            and revenue_cagr > REVENUE_GROWTH_THRESHOLD
            and op_income_cagr is not None
            and op_income_cagr > PROFIT_GROWTH_THRESHOLD
        )
        score_margin_growth = _score_groups([margins_expanded, grew_meaningfully])

    # --- Pillar 2: Low Dilution ---
    no_convertible = not bool(latest.get("has_convertible_instruments"))
    if share_count_change_5y is None:
        score_low_dilution = 1 if no_convertible else 0  # can only assess the convertible leg
    else:
        not_diluting = share_count_change_5y <= DILUTION_TOLERANCE
        score_low_dilution = _score_groups([not_diluting, no_convertible])

    # --- Pillar 3: Capital Efficiency without Leverage ---
    # Three groups: (a) debt did not rise, (b) self-funding (positive FCF),
    # (c) reinvesting productively (capex deployed AND operating income grew).
    fcf = latest.get("free_cash_flow")
    capex = latest.get("capex")
    p3_inputs = [total_debt_change_5y, fcf, op_income_cagr, capex]
    if all(v is None for v in p3_inputs):
        score_capital_efficiency = None
    else:
        not_leveraging = total_debt_change_5y is not None and total_debt_change_5y <= DEBT_INCREASE_TOLERANCE
        self_funding = fcf is not None and fcf > 0
        reinvesting_productively = (capex is not None and capex > 0) and (op_income_cagr is not None and op_income_cagr > 0)
        score_capital_efficiency = _score_groups([not_leveraging, self_funding, reinvesting_productively])

    pillars = [score_margin_growth, score_low_dilution, score_capital_efficiency]
    score_overall = sum(s for s in pillars if s is not None)

    window = {
        "gross_margin_change_5y": gross_margin_change_5y,
        "operating_margin_change_5y": operating_margin_change_5y,
        "net_margin_change_5y": net_margin_change_5y,
        "share_count_change_5y": share_count_change_5y,
        "total_debt_change_5y": total_debt_change_5y,
        "score_margin_growth": score_margin_growth,
        "score_low_dilution": score_low_dilution,
        "score_capital_efficiency": score_capital_efficiency,
        "score_overall": score_overall,
    }
    for row in rows_sorted:
        row.update(window)
    return rows_sorted
