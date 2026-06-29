from __future__ import annotations

import pandas as pd

from calculations.statement_parser import get_convertible_instruments, get_metric


def compute(df: pd.DataFrame) -> dict:
    short_term_borrowings = get_metric(df, "short_term_borrowings")
    long_term_borrowings = get_metric(df, "long_term_borrowings")
    bonds = get_metric(df, "bonds")
    has_convertible, convertible_value = get_convertible_instruments(df)

    total_equity = get_metric(df, "total_equity")

    debt_parts = [v for v in (short_term_borrowings, long_term_borrowings, bonds, convertible_value) if v]
    total_debt = sum(debt_parts) if debt_parts else None

    equity_impaired = total_equity is not None and total_equity <= 0
    debt_to_equity = (
        total_debt / total_equity if total_debt is not None and not equity_impaired and total_equity else None
    )

    return {
        "short_term_borrowings": short_term_borrowings,
        "long_term_borrowings": long_term_borrowings,
        "total_debt": total_debt,
        "debt_to_equity": debt_to_equity,
        "equity_impaired": equity_impaired,
        "has_convertible_instruments": has_convertible,
        "convertible_instruments_value": convertible_value,
        "total_equity": total_equity,
        "total_assets": get_metric(df, "total_assets"),
        "total_liabilities": get_metric(df, "total_liabilities"),
    }
