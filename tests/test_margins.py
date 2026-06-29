from calculations.margins import attach_margin_changes, compute


def test_margin_computation():
    row = {"revenue": 1000.0, "gross_profit": 400.0, "operating_income": 150.0, "net_income": 80.0}
    result = compute(row)
    assert result["gross_margin"] == 0.40
    assert result["operating_margin"] == 0.15
    assert result["net_margin"] == 0.08


def test_margin_none_when_revenue_non_positive():
    row = {"revenue": 0, "gross_profit": 400.0, "operating_income": 150.0, "net_income": 80.0}
    assert compute(row) == {"gross_margin": None, "operating_margin": None, "net_margin": None}

    row2 = {"revenue": -100.0, "gross_profit": 40.0, "operating_income": 10.0, "net_income": 5.0}
    assert compute(row2) == {"gross_margin": None, "operating_margin": None, "net_margin": None}


def test_margin_change_is_additive_delta_in_points():
    rows = [
        {"fiscal_year": 2021, "operating_margin": 0.10, "net_margin": 0.05},
        {"fiscal_year": 2022, "operating_margin": 0.12, "net_margin": 0.04},
        {"fiscal_year": 2023, "operating_margin": 0.18, "net_margin": 0.09},
    ]
    out = attach_margin_changes(rows)
    assert out[0]["operating_margin_change_yoy"] is None  # earliest year has no prior
    assert round(out[1]["operating_margin_change_yoy"], 4) == 0.02  # +2pp, expansion
    assert round(out[1]["net_margin_change_yoy"], 4) == -0.01  # -1pp, contraction
    assert round(out[2]["operating_margin_change_yoy"], 4) == 0.06


def test_margin_change_none_when_either_side_missing():
    rows = [
        {"fiscal_year": 2022, "operating_margin": None, "net_margin": 0.05},
        {"fiscal_year": 2023, "operating_margin": 0.10, "net_margin": 0.06},
    ]
    out = attach_margin_changes(rows)
    assert out[1]["operating_margin_change_yoy"] is None
    assert round(out[1]["net_margin_change_yoy"], 4) == 0.01
