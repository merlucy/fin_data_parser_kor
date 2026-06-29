from __future__ import annotations

from dataclasses import dataclass

from dart_client.client import get_financial_statements
from dart_client.endpoints import FS_DIV_CONSOLIDATED, FS_DIV_SEPARATE


@dataclass
class StatementBundle:
    data: list[dict]
    fs_div_used: str | None  # 'CFS' / 'OFS' / None


def resolve_statement(corp_code: str, bsns_year: str, reprt_code: str = "11011") -> StatementBundle:
    """Try 연결(CFS) first; if unavailable/empty, fall back to 별도(OFS)."""
    cfs = get_financial_statements(corp_code, bsns_year, FS_DIV_CONSOLIDATED, reprt_code)
    if cfs["status"] == "000" and cfs["list"]:
        return StatementBundle(data=cfs["list"], fs_div_used=FS_DIV_CONSOLIDATED)

    ofs = get_financial_statements(corp_code, bsns_year, FS_DIV_SEPARATE, reprt_code)
    if ofs["status"] == "000" and ofs["list"]:
        return StatementBundle(data=ofs["list"], fs_div_used=FS_DIV_SEPARATE)

    return StatementBundle(data=[], fs_div_used=None)
