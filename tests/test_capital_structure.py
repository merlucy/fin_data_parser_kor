from calculations import capital_structure
from calculations.statement_parser import to_dataframe


def test_samsung_debt_structure(samsung_2023):
    df = to_dataframe(samsung_2023["list"])
    result = capital_structure.compute(df)

    assert result["short_term_borrowings"] == 8423476000000.0
    assert result["long_term_borrowings"] == 3724850000000.0
    assert result["has_convertible_instruments"] is False
    assert result["equity_impaired"] is False
    assert result["debt_to_equity"] == result["total_debt"] / result["total_equity"]


def test_shinla_gen_includes_convertible_bonds_in_total_debt(shinla_gen_2023):
    df = to_dataframe(shinla_gen_2023["list"])
    result = capital_structure.compute(df)

    assert result["has_convertible_instruments"] is True
    assert result["convertible_instruments_value"] == 8135849666.0
    # total_debt must include the convertible bond carrying value, not just plain borrowings
    assert result["total_debt"] >= 8135849666.0


def test_equity_impaired_flag_when_equity_non_positive():
    rows = [
        {"sj_div": "BS", "account_nm": "자본총계", "thstrm_amount": "-500", "ord": "1"},
        {"sj_div": "BS", "account_nm": "단기차입금", "thstrm_amount": "1000", "ord": "2"},
    ]
    df = to_dataframe(rows)
    result = capital_structure.compute(df)
    assert result["equity_impaired"] is True
    assert result["debt_to_equity"] is None
