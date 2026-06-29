"""Keyword/alias tables for matching DART account_nm values.

account_id (the XBRL taxonomy tag) is inconsistent or missing across many
filers, so matching is done on account_nm (the Korean label as filed)
instead, scoped to the correct sj_div (statement) to avoid cross-statement
false positives (e.g. "취득" appears in both BS notes and CF investing lines).
"""

from __future__ import annotations

ACCOUNT_ALIASES: dict[str, list[str]] = {
    "revenue": ["매출액", "수익(매출액)", "영업수익", "매출"],
    "gross_profit": ["매출총이익"],
    "operating_income": ["영업이익", "영업이익(손실)"],
    "net_income": ["당기순이익", "당기순이익(손실)", "분기순이익", "반기순이익"],
    "total_assets": ["자산총계"],
    "total_liabilities": ["부채총계"],
    "total_equity": ["자본총계"],
    "operating_cash_flow": [
        "영업활동현금흐름",
        "영업활동으로인한현금흐름",
        "영업활동으로 인한 현금흐름",
        "영업활동순현금흐름",
    ],
    "capex": ["유형자산의취득", "유형자산의 취득", "무형자산의취득", "무형자산의 취득", "유무형자산의취득"],
    "depreciation": ["감가상각비"],
    "amortization": ["무형자산상각비"],
    "short_term_borrowings": ["단기차입금", "유동성장기차입금", "유동성장기부채"],
    "long_term_borrowings": ["장기차입금"],
    "bonds": ["사채", "회사채"],
    "convertible_bonds": ["전환사채", "유동성전환사채"],
    "bonds_with_warrants": ["신주인수권부사채", "유동성신주인수권부사채"],
    "exchangeable_bonds": ["교환사채", "유동성교환사채"],
}

# Restrict matching for each metric to the statement section(s) it can legitimately appear in.
# Income-statement-line metrics can appear under "IS" (separate income statement) or "CIS"
# (combined comprehensive income statement) depending on filer presentation choice - some
# companies file only a single combined CIS with no standalone IS.
SJ_DIV_SCOPE: dict[str, tuple[str, ...]] = {
    "revenue": ("IS", "CIS"),
    "gross_profit": ("IS", "CIS"),
    "operating_income": ("IS", "CIS"),
    "net_income": ("IS", "CIS"),
    "total_assets": ("BS",),
    "total_liabilities": ("BS",),
    "total_equity": ("BS",),
    "operating_cash_flow": ("CF",),
    "capex": ("CF",),
    "depreciation": ("CF",),
    "amortization": ("CF",),
    "short_term_borrowings": ("BS",),
    "long_term_borrowings": ("BS",),
    "bonds": ("BS",),
    "convertible_bonds": ("BS",),
    "bonds_with_warrants": ("BS",),
    "exchangeable_bonds": ("BS",),
}


# Metrics where multiple line items can legitimately co-exist and should be summed
# (e.g. 유형자산의취득 + 무형자산의취득 both count toward capex). All other metrics
# are treated as "pick one" subtotal lines (e.g. 자산총계).
SUM_METRICS = {"capex", "depreciation", "amortization", "short_term_borrowings", "long_term_borrowings", "bonds"}


def normalize(name: str) -> str:
    return name.replace(" ", "").strip()


def matches(account_nm: str, metric: str) -> bool:
    normalized = normalize(account_nm)
    return any(normalize(alias) in normalized for alias in ACCOUNT_ALIASES[metric])


def exact_matches(account_nm: str, metric: str) -> bool:
    normalized = normalize(account_nm)
    return any(normalized == normalize(alias) for alias in ACCOUNT_ALIASES[metric])
