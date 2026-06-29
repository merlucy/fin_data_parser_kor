from calculations.scoring import attach_scores


def _ideal_company():
    """5 years of expanding margins, strong growth, no dilution, falling debt, positive FCF."""
    rows = []
    for i, yr in enumerate(range(2019, 2024)):
        rows.append(
            {
                "fiscal_year": yr,
                "gross_margin": 0.30 + 0.02 * i,
                "operating_margin": 0.10 + 0.02 * i,
                "net_margin": 0.08 + 0.015 * i,
                "shares_outstanding": 1000.0,
                "total_debt": 500.0 - 50 * i,
                "free_cash_flow": 100.0,
                "capex": 40.0,
                "has_convertible_instruments": False,
                "revenue_cagr_5y": 0.15,
                "operating_income_cagr_5y": 0.20,
            }
        )
    return rows


def test_ideal_company_scores_top_marks():
    out = attach_scores(_ideal_company())
    r = out[-1]
    assert r["score_margin_growth"] == 2  # both margins expanded + revenue & profit grew
    assert r["score_low_dilution"] == 2  # flat shares + no convertibles
    assert r["score_capital_efficiency"] == 2  # debt down + FCF+ + growth + capex
    assert r["score_overall"] == 6
    assert round(r["gross_margin_change_5y"], 2) == 0.08
    assert r["share_count_change_5y"] == 0.0
    assert round(r["total_debt_change_5y"], 2) == -0.40


def test_dilution_and_convertibles_hurt_pillar_two():
    rows = _ideal_company()
    for i, row in enumerate(rows):
        row["shares_outstanding"] = 1000.0 + 100 * i  # heavy dilution over the window
    rows[-1]["has_convertible_instruments"] = True
    out = attach_scores(rows)
    assert out[-1]["score_low_dilution"] == 0  # diluting AND convertibles outstanding


def test_rising_debt_demotes_capital_efficiency_from_strong():
    rows = _ideal_company()
    for row in rows:
        row["total_debt"] = 500.0  # flat... then make latest-vs-first rise
    rows[-1]["total_debt"] = 1500.0  # debt tripled over the window
    for row in rows:
        row["free_cash_flow"] = -50.0  # burning cash
    out = attach_scores(rows)
    # still reinvesting + growing op income, so "mixed" (1), but no longer strong (2)
    assert out[-1]["score_capital_efficiency"] == 1


def test_debt_burn_and_no_growth_fails_capital_efficiency():
    rows = _ideal_company()
    rows[-1]["total_debt"] = 1500.0  # debt up
    for row in rows:
        row["free_cash_flow"] = -50.0  # cash burn
        row["capex"] = 0.0  # not reinvesting
    for row in rows:
        row["operating_income_cagr_5y"] = -0.1  # shrinking
    out = attach_scores(rows)
    assert out[-1]["score_capital_efficiency"] == 0


def test_missing_data_yields_none_scores_not_crash():
    rows = [
        {"fiscal_year": 2022, "has_convertible_instruments": False},
        {"fiscal_year": 2023, "has_convertible_instruments": False},
    ]
    out = attach_scores(rows)
    assert out[-1]["score_margin_growth"] is None
    assert out[-1]["score_capital_efficiency"] is None
    # pillar 2 can still assess the convertible leg even with no share data
    assert out[-1]["score_low_dilution"] == 1
