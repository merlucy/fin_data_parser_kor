from calculations import cashflow_quality
from calculations.statement_parser import to_dataframe


def test_samsung_fcf_and_missing_depreciation(samsung_2023):
    df = to_dataframe(samsung_2023["list"])
    result = cashflow_quality.compute(df)

    assert result["operating_cash_flow"] == 44137427000000.0
    assert result["capex"] == 60534167000000.0
    assert result["free_cash_flow"] == 44137427000000.0 - 60534167000000.0
    # Samsung's consolidated CF face statement doesn't break out 감가상각비 separately
    # (bundled into "조정"), so this is the expected real-world limitation, not a bug.
    assert result["depreciation_amortization"] is None
    assert result["depreciation_source"] == "missing"
    assert result["reinvestment_ratio_capex_da"] is None
    assert result["reinvestment_ratio_capex_ocf"] is not None


def test_negative_ocf_does_not_produce_capex_ocf_ratio():
    rows = [
        {"sj_div": "CF", "account_nm": "영업활동현금흐름", "thstrm_amount": "-1000", "ord": "1"},
        {"sj_div": "CF", "account_nm": "유형자산의 취득", "thstrm_amount": "500", "ord": "2"},
    ]
    df = to_dataframe(rows)
    result = cashflow_quality.compute(df)
    assert result["operating_cash_flow"] == -1000.0
    assert result["capex"] == 500.0
    assert result["free_cash_flow"] == -1500.0
    assert result["reinvestment_ratio_capex_ocf"] is None


def test_depreciation_present_when_disclosed_on_face():
    rows = [
        {"sj_div": "CF", "account_nm": "영업활동현금흐름", "thstrm_amount": "10000", "ord": "1"},
        {"sj_div": "CF", "account_nm": "유형자산의 취득", "thstrm_amount": "4000", "ord": "2"},
        {"sj_div": "CF", "account_nm": "감가상각비", "thstrm_amount": "2000", "ord": "3"},
        {"sj_div": "CF", "account_nm": "무형자산상각비", "thstrm_amount": "500", "ord": "4"},
    ]
    df = to_dataframe(rows)
    result = cashflow_quality.compute(df)
    assert result["depreciation_amortization"] == 2500.0
    assert result["depreciation_source"] == "CF_addback"
    assert result["reinvestment_ratio_capex_da"] == 4000.0 / 2500.0
