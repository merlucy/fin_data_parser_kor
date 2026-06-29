from calculations.statement_parser import get_convertible_instruments, get_metric, to_dataframe


def test_samsung_core_metrics(samsung_2023):
    df = to_dataframe(samsung_2023["list"])
    assert get_metric(df, "revenue") == 258935494000000.0
    assert get_metric(df, "gross_profit") == 78546914000000.0
    assert get_metric(df, "operating_income") == 6566976000000.0
    assert get_metric(df, "net_income") == 15487100000000.0
    assert get_metric(df, "total_assets") == 455905980000000.0
    assert get_metric(df, "total_equity") == 363677865000000.0


def test_samsung_net_income_excludes_attribution_breakdown(samsung_2023):
    # IS section has 3 lines containing "당기순이익": total, NCI-attributable, owners-attributable.
    # get_metric must return the plain total, not one of the attribution breakdowns.
    df = to_dataframe(samsung_2023["list"])
    assert get_metric(df, "net_income") == 15487100000000.0


def test_samsung_capex_sums_tangible_and_intangible(samsung_2023):
    df = to_dataframe(samsung_2023["list"])
    # 유형자산의 취득 (57,611,292,000,000) + 무형자산의 취득 (2,922,875,000,000)
    assert get_metric(df, "capex") == 57611292000000.0 + 2922875000000.0


def test_samsung_has_no_convertible_instruments(samsung_2023):
    df = to_dataframe(samsung_2023["list"])
    has_cb, value = get_convertible_instruments(df)
    assert has_cb is False
    assert value == 0.0


def test_shinla_gen_has_convertible_bonds(shinla_gen_2023):
    df = to_dataframe(shinla_gen_2023["list"])
    has_cb, value = get_convertible_instruments(df)
    assert has_cb is True
    assert value == 8135849666.0


def test_empty_statement_returns_none():
    df = to_dataframe([])
    assert get_metric(df, "revenue") is None
    assert get_convertible_instruments(df) == (False, 0.0)
