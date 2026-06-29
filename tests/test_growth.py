from calculations.growth import attach_growth_metrics


def test_yoy_and_cagr_over_window():
    rows = [
        {"fiscal_year": 2019, "operating_income": 100, "gross_profit": 200, "net_income": 50},
        {"fiscal_year": 2020, "operating_income": 110, "gross_profit": 220, "net_income": 55},
        {"fiscal_year": 2021, "operating_income": 121, "gross_profit": 242, "net_income": 60},
        {"fiscal_year": 2022, "operating_income": 133.1, "gross_profit": 266, "net_income": 65},
        {"fiscal_year": 2023, "operating_income": 146.41, "gross_profit": 290, "net_income": 70},
    ]
    out = attach_growth_metrics(rows)

    assert out[0]["operating_income_growth_yoy"] is None  # earliest year has no prior
    assert round(out[1]["operating_income_growth_yoy"], 4) == 0.10
    assert round(out[-1]["operating_income_cagr_5y"], 4) == 0.10  # 100 -> 146.41 over 4 years = 10% CAGR
    # CAGR is attached to every row in the window, not just the last
    assert out[0]["operating_income_cagr_5y"] == out[-1]["operating_income_cagr_5y"]


def test_yoy_none_when_prior_is_zero_or_sign_flips():
    rows = [
        {"fiscal_year": 2022, "operating_income": 0, "gross_profit": -50, "net_income": 10},
        {"fiscal_year": 2023, "operating_income": 100, "gross_profit": 80, "net_income": 20},
    ]
    out = attach_growth_metrics(rows)
    assert out[1]["operating_income_growth_yoy"] is None  # division by zero guarded
    assert out[1]["gross_profit_growth_yoy"] is not None  # sign-flip is still a valid YoY (not CAGR)


def test_cagr_none_when_either_endpoint_non_positive():
    rows = [
        {"fiscal_year": 2019, "operating_income": -10, "gross_profit": 10, "net_income": 10},
        {"fiscal_year": 2023, "operating_income": 50, "gross_profit": 20, "net_income": 5},
    ]
    out = attach_growth_metrics(rows)
    assert out[0]["operating_income_cagr_5y"] is None
    assert out[0]["gross_profit_cagr_5y"] is not None


def test_single_year_window_has_no_growth_metrics():
    rows = [{"fiscal_year": 2023, "operating_income": 100, "gross_profit": 200, "net_income": 50}]
    out = attach_growth_metrics(rows)
    assert out[0]["operating_income_growth_yoy"] is None
    assert out[0]["operating_income_cagr_5y"] is None
