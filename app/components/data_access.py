"""Streamlit-facing data access layer. Wraps db/repository.py and universe/resolver.py.

Keeps SQL out of the page files and is the natural place for st.cache_data.
"""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from db import repository
from universe.resolver import list_industries


@st.cache_data(ttl=300)
def get_industries() -> list[str]:
    return list_industries()


@st.cache_data(ttl=30)
def get_recent_runs(limit: int = 20) -> pd.DataFrame:
    runs = repository.get_recent_runs(limit)
    return pd.DataFrame(
        [
            {
                "id": r.id,
                "industry": r.industry,
                "sector": r.sector,
                "fiscal_year_end": r.fiscal_year_end,
                "history_years": r.history_years,
                "status": r.status,
                "company_count": r.company_count,
                "requested_at": r.requested_at,
            }
            for r in runs
        ]
    )


@st.cache_data(ttl=30)
def get_run_financials_df(run_id: int) -> pd.DataFrame:
    pairs = repository.get_run_financials(run_id)
    rows = []
    numeric_cols: set[str] = set()
    for financial, company in pairs:
        row = {}
        for c in financial.__table__.columns:
            value = getattr(financial, c.name)
            if isinstance(value, Decimal):
                value = float(value)
                numeric_cols.add(c.name)
            row[c.name] = value
        row["corp_name"] = company.corp_name
        row["stock_code"] = company.stock_code
        row["market"] = company.market
        row["industry"] = company.industry
        rows.append(row)
    df = pd.DataFrame(rows)
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def trigger_run(industry: str, history_years: int = 5) -> int:
    from jobs.run_screen import run_screen

    run_id = run_screen(industry, history_years=history_years)
    get_recent_runs.clear()
    return run_id


def latest_run_id_for_industry(industry: str) -> int | None:
    df = get_recent_runs(limit=100)
    matches = df[(df["industry"] == industry) & (df["status"].isin(["completed", "partial"]))]
    if matches.empty:
        return None
    return int(matches.sort_values("requested_at", ascending=False).iloc[0]["id"])
