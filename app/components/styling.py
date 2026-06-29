"""Visual emphasis for the dashboard tables and KPI cards.

Two concerns live here:
  1. `style_financial_table` — turns a plain DataFrame into a pandas Styler that
     color-codes the *important* indicators so they pop at a glance: directional
     metrics (growth, margin change, FCF) get green/red text by sign, margins get
     a graded green background, leverage and risk flags get amber/red warning tints.
  2. `human_won` — compact KRW formatter for st.metric cards (조 = trillion,
     억 = hundred million), since raw comma-grouped won is unreadable in a small card.

Color coding here is intentionally semantic (good = green, risk = red/amber), not a
raw numeric gradient, so the colors carry meaning for screening decisions.
"""

from __future__ import annotations

import pandas as pd
from pandas.io.formats.style import Styler

# Text colors for directional (signed) metrics
_POS_TEXT = "color: #1a7f37; font-weight: 600;"  # green — improving
_NEG_TEXT = "color: #cf222e; font-weight: 600;"  # red — deteriorating

# Background tints for level / risk emphasis
_MARGIN_STRONG_BG = "background-color: #d7f0df;"  # >= 20%
_MARGIN_OK_BG = "background-color: #eaf7ee;"  # > 0%
_MARGIN_NEG_BG = "background-color: #fde7e7;"  # <= 0% (loss-making)
_LEV_WARN_BG = "background-color: #fff4e5;"  # elevated leverage
_LEV_ALERT_BG = "background-color: #ffe3e3;"  # high leverage
_RISK_BG = "background-color: #fff4e5; color: #9a6700; font-weight: 600;"  # risk flag is True
_SCORE_STRONG_BG = "background-color: #c9ead4; color: #0f5132; font-weight: 700;"  # 2
_SCORE_MIXED_BG = "background-color: #fff3cd; color: #7a5b00; font-weight: 700;"  # 1
_SCORE_FAIL_BG = "background-color: #f8d4d4; color: #842029; font-weight: 700;"  # 0

# Column groups -> styling treatment. Only columns present in the table are styled.
# Directional, higher = better (green if > 0, red if < 0):
_SIGNED_COLS = {
    "revenue_growth_yoy",
    "operating_income_growth_yoy",
    "net_income_growth_yoy",
    "gross_profit_growth_yoy",
    "revenue_cagr_5y",
    "operating_income_cagr_5y",
    "net_income_cagr_5y",
    "gross_profit_cagr_5y",
    "gross_margin_change_yoy",
    "operating_margin_change_yoy",
    "net_margin_change_yoy",
    "gross_margin_change_5y",
    "operating_margin_change_5y",
    "net_margin_change_5y",
    "free_cash_flow",
}
# Directional, lower = better (green if <= 0, red if > 0) — dilution & rising debt:
_INVERSE_SIGNED_COLS = {"share_count_change_yoy", "share_count_change_5y", "total_debt_change_5y"}
_MARGIN_COLS = {"gross_margin", "operating_margin", "net_margin"}
_LEVERAGE_COLS = {"debt_to_equity"}
_RISK_BOOL_COLS = {"has_convertible_instruments", "equity_impaired"}
_SCORE_COLS = {"score_margin_growth", "score_low_dilution", "score_capital_efficiency", "score_overall"}


def _signed(v: object) -> str:
    if v is None or pd.isna(v):
        return ""
    if v > 0:
        return _POS_TEXT
    if v < 0:
        return _NEG_TEXT
    return ""


def _margin(v: object) -> str:
    if v is None or pd.isna(v):
        return ""
    if v >= 0.20:
        return _MARGIN_STRONG_BG
    if v > 0:
        return _MARGIN_OK_BG
    return _MARGIN_NEG_BG


def _leverage(v: object) -> str:
    if v is None or pd.isna(v):
        return ""
    if v >= 2.0:
        return _LEV_ALERT_BG
    if v >= 1.0:
        return _LEV_WARN_BG
    return ""


def _inverse_signed(v: object) -> str:
    if v is None or pd.isna(v):
        return ""
    if v > 0:  # shares/debt increased -> bad
        return _NEG_TEXT
    return _POS_TEXT  # flat or down -> good


def _risk_bool(v: object) -> str:
    return _RISK_BG if bool(v) else ""


def _score(v: object) -> str:
    if v is None or pd.isna(v):
        return ""
    # pillar scores are 0-2; overall is 0-6. Bucket by thirds so both map cleanly.
    hi = 6 if v > 2 else 2
    if v >= hi * 0.75:
        return _SCORE_STRONG_BG
    if v >= hi * 0.5:
        return _SCORE_MIXED_BG
    return _SCORE_FAIL_BG


def style_financial_table(df: pd.DataFrame) -> Styler:
    """Return a Styler that color-codes the important indicator columns present in `df`."""
    styler = df.style
    for col in df.columns:
        if col in _SCORE_COLS:
            styler = styler.map(_score, subset=[col])
        elif col in _SIGNED_COLS:
            styler = styler.map(_signed, subset=[col])
        elif col in _INVERSE_SIGNED_COLS:
            styler = styler.map(_inverse_signed, subset=[col])
        elif col in _MARGIN_COLS:
            styler = styler.map(_margin, subset=[col])
        elif col in _LEVERAGE_COLS:
            styler = styler.map(_leverage, subset=[col])
        elif col in _RISK_BOOL_COLS:
            styler = styler.map(_risk_bool, subset=[col])
    return styler


_STATUS_EMOJI = {
    "completed": "🟢 completed",
    "partial": "🟡 partial",
    "running": "🔵 running",
    "pending": "⚪ pending",
    "failed": "🔴 failed",
}


def decorate_run_status(runs_df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of a screening-runs DataFrame with the status column emoji-prefixed."""
    out = runs_df.copy()
    if "status" in out.columns:
        out["status"] = out["status"].map(lambda s: _STATUS_EMOJI.get(s, s))
    return out


def human_won(value: object) -> str:
    """Compact KRW for metric cards, e.g. 258_935_494_000_000 -> '258.9조'."""
    if value is None or pd.isna(value):
        return "—"
    v = float(value)
    sign = "-" if v < 0 else ""
    a = abs(v)
    jo = 1_0000_0000_0000  # 조 (trillion)
    eok = 1_0000_0000  # 억 (hundred million)
    man = 1_0000  # 만
    if a >= jo:
        return f"{sign}{a / jo:,.1f}조"
    if a >= eok:
        return f"{sign}{a / eok:,.1f}억"
    if a >= man:
        return f"{sign}{a / man:,.0f}만"
    return f"{sign}{a:,.0f}"
