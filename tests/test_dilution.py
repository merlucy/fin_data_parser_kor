from calculations.dilution import attach_share_changes, extract_common_shares


def test_extract_common_shares_parses_istc_totqy():
    body = {
        "status": "000",
        "list": [
            {"se": "보통주", "istc_totqy": "5,969,782,550"},
            {"se": "우선주", "istc_totqy": "822,886,700"},
            {"se": "합계", "istc_totqy": "6,792,669,250"},
        ],
    }
    assert extract_common_shares(body) == 5969782550.0


def test_extract_common_shares_handles_no_data_and_dashes():
    assert extract_common_shares({"status": "013", "list": []}) is None
    assert extract_common_shares({"status": "000", "list": [{"se": "보통주", "istc_totqy": "-"}]}) is None


def test_attach_share_changes_yoy():
    rows = [
        {"fiscal_year": 2021, "shares_outstanding": 1000.0},
        {"fiscal_year": 2022, "shares_outstanding": 1100.0},  # +10% dilution
        {"fiscal_year": 2023, "shares_outstanding": 1100.0},  # flat
    ]
    out = attach_share_changes(rows)
    assert out[0]["share_count_change_yoy"] is None
    assert round(out[1]["share_count_change_yoy"], 4) == 0.10
    assert out[2]["share_count_change_yoy"] == 0.0


def test_attach_share_changes_handles_missing():
    rows = [
        {"fiscal_year": 2022, "shares_outstanding": None},
        {"fiscal_year": 2023, "shares_outstanding": 500.0},
    ]
    out = attach_share_changes(rows)
    assert out[1]["share_count_change_yoy"] is None
