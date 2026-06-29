"""Parse a raw DART line-item list into a tidy DataFrame, and look up metrics by alias."""

from __future__ import annotations

import pandas as pd

from calculations.account_lookup import SJ_DIV_SCOPE, SUM_METRICS, exact_matches, matches


def to_dataframe(line_items: list[dict]) -> pd.DataFrame:
    if not line_items:
        return pd.DataFrame(columns=["sj_div", "account_nm", "thstrm_amount", "ord"])

    df = pd.DataFrame(line_items)
    df["thstrm_amount"] = pd.to_numeric(
        df["thstrm_amount"].astype(str).str.replace(",", "").str.strip().replace("", pd.NA),
        errors="coerce",
    )
    df["ord"] = pd.to_numeric(df.get("ord"), errors="coerce")
    return df


def get_metric(df: pd.DataFrame, metric: str) -> float | None:
    """Look up a single metric's value from the parsed statement DataFrame.

    Sum-type metrics (capex, depreciation, borrowings, ...) sum every matching
    line item (absolute value, since CF outflows are often filed negative).
    Subtotal-type metrics (revenue, net_income, total_assets, ...) prefer an
    exact account_nm match over a substring match, to avoid picking up
    "지배기업의 소유주에게 귀속되는 당기순이익" when looking for plain "당기순이익".
    """
    if df.empty:
        return None

    scope = SJ_DIV_SCOPE[metric]
    section = df[df["sj_div"].isin(scope)]
    if section.empty:
        return None

    candidates = section[section["account_nm"].apply(lambda nm: matches(nm, metric))]
    if candidates.empty:
        return None

    if metric in SUM_METRICS:
        values = candidates["thstrm_amount"].dropna()
        if values.empty:
            return None
        return float(values.abs().sum())

    exact = candidates[candidates["account_nm"].apply(lambda nm: exact_matches(nm, metric))]
    pool = exact if not exact.empty else candidates
    pool = pool.dropna(subset=["thstrm_amount"]).sort_values("ord")
    if pool.empty:
        return None
    return float(pool.iloc[0]["thstrm_amount"])


def get_convertible_instruments(df: pd.DataFrame) -> tuple[bool, float]:
    """Sum carrying value of all BS-disclosed convertible-type instruments (CB/BW/EB)."""
    if df.empty:
        return False, 0.0

    section = df[df["sj_div"] == "BS"]
    metrics = ["convertible_bonds", "bonds_with_warrants", "exchangeable_bonds"]
    mask = section["account_nm"].apply(lambda nm: any(matches(nm, m) for m in metrics))
    candidates = section[mask]
    if candidates.empty:
        return False, 0.0

    total = float(candidates["thstrm_amount"].dropna().abs().sum())
    return True, total
