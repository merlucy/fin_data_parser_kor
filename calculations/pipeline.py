from __future__ import annotations

from calculations import capital_structure, cashflow_quality, growth
from calculations.fallback import resolve_statement
from calculations.statement_parser import get_metric, to_dataframe


def compute_year_metrics(corp_code: str, fiscal_year: int, reprt_code: str = "11011") -> dict:
    bundle = resolve_statement(corp_code, str(fiscal_year), reprt_code)
    row = {
        "corp_code": corp_code,
        "fiscal_year": fiscal_year,
        "reprt_code": reprt_code,
        "fs_div_used": bundle.fs_div_used,
    }

    if not bundle.data:
        return row

    df = to_dataframe(bundle.data)
    row["revenue"] = get_metric(df, "revenue")
    row["gross_profit"] = get_metric(df, "gross_profit")
    row["operating_income"] = get_metric(df, "operating_income")
    row["net_income"] = get_metric(df, "net_income")
    row.update(cashflow_quality.compute(df))
    row.update(capital_structure.compute(df))
    return row


def run_for_company(corp_code: str, years: list[int], reprt_code: str = "11011") -> list[dict]:
    rows = [compute_year_metrics(corp_code, year, reprt_code) for year in years]
    return growth.attach_growth_metrics(rows)
