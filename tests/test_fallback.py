from unittest.mock import patch

from calculations.fallback import resolve_statement


def _resp(status: str, data: list[dict] | None = None) -> dict:
    return {"status": status, "message": "", "list": data or []}


def test_uses_cfs_when_available():
    with patch("calculations.fallback.get_financial_statements") as mock_get:
        mock_get.return_value = _resp("000", [{"sj_div": "BS"}])
        bundle = resolve_statement("00000001", "2023")
        assert bundle.fs_div_used == "CFS"
        assert bundle.data == [{"sj_div": "BS"}]
        mock_get.assert_called_once()  # OFS should never be fetched once CFS succeeds


def test_falls_back_to_ofs_when_cfs_empty():
    with patch("calculations.fallback.get_financial_statements") as mock_get:
        mock_get.side_effect = [_resp("013", []), _resp("000", [{"sj_div": "BS"}])]
        bundle = resolve_statement("00000001", "2023")
        assert bundle.fs_div_used == "OFS"
        assert mock_get.call_count == 2


def test_returns_empty_bundle_when_both_unavailable():
    with patch("calculations.fallback.get_financial_statements") as mock_get:
        mock_get.side_effect = [_resp("013", []), _resp("013", [])]
        bundle = resolve_statement("00000001", "2023")
        assert bundle.fs_div_used is None
        assert bundle.data == []
