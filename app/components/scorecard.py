"""Render the three-pillar investment scorecard as prominent cards.

Maps the persisted pillar scores (0/1/2) + the window-level evidence onto a
compact, color-cued layout so the three screening criteria are the first thing
a user sees for a company.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

_SCORE_LABEL = {2: "🟢 Strong", 1: "🟡 Mixed", 0: "🔴 Weak", None: "⚪ N/A"}


def score_label(score: object) -> str:
    if score is None or pd.isna(score):
        return _SCORE_LABEL[None]
    return _SCORE_LABEL.get(int(score), "⚪ N/A")


def _pct(v: object, points: bool = False) -> str:
    if v is None or pd.isna(v):
        return "n/a"
    return f"{v:+.1%}{'p' if points else ''}"


def render_company_scorecard(row: pd.Series) -> None:
    """Render the overall score + 3 pillar cards for a company's latest-year row."""
    overall = row.get("score_overall")
    overall_txt = f"{int(overall)}/6" if overall is not None and not pd.isna(overall) else "n/a"
    st.markdown(f"#### Investment Scorecard &nbsp; · &nbsp; ★ Overall **{overall_txt}**")

    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.markdown("**① Margin & Growth**")
        st.markdown(f"### {score_label(row.get('score_margin_growth'))}")
        st.caption(
            f"Gross margin Δ5y **{_pct(row.get('gross_margin_change_5y'), points=True)}** · "
            f"Op margin Δ5y **{_pct(row.get('operating_margin_change_5y'), points=True)}**\n\n"
            f"Revenue CAGR **{_pct(row.get('revenue_cagr_5y'))}** · "
            f"Op income CAGR **{_pct(row.get('operating_income_cagr_5y'))}**"
        )
    with c2.container(border=True):
        st.markdown("**② Low Dilution**")
        st.markdown(f"### {score_label(row.get('score_low_dilution'))}")
        convertible = "Yes ⚠️" if bool(row.get("has_convertible_instruments")) else "No"
        st.caption(
            f"Shares Δ5y **{_pct(row.get('share_count_change_5y'))}** "
            f"(↑ = dilution)\n\nConvertible instruments: **{convertible}**"
        )
    with c3.container(border=True):
        st.markdown("**③ Capital Efficiency**")
        st.markdown(f"### {score_label(row.get('score_capital_efficiency'))}")
        fcf = row.get("free_cash_flow")
        fcf_txt = "positive" if (fcf is not None and not pd.isna(fcf) and fcf > 0) else "negative/none"
        st.caption(
            f"Total debt Δ5y **{_pct(row.get('total_debt_change_5y'))}** "
            f"(↓ = better)\n\nFree cash flow: **{fcf_txt}**"
        )
