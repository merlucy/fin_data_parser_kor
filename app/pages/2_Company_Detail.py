import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.charts import multi_year_line  # noqa: E402
from app.components.column_specs import build_column_config  # noqa: E402
from app.components.data_access import get_recent_runs, get_run_financials_df  # noqa: E402
from app.components.scorecard import render_company_scorecard  # noqa: E402
from app.components.styling import human_won, style_financial_table  # noqa: E402

st.set_page_config(page_title="Company Detail", layout="wide")
st.title("🏢 Company Detail")

runs_df = get_recent_runs(limit=100)
if runs_df.empty:
    st.info("No screening runs yet. Go to Home and run a screen first.")
    st.stop()

industries = sorted(runs_df["industry"].dropna().unique().tolist())
col1, col2 = st.columns(2)
selected_industry = col1.selectbox("Industry", options=industries)

industry_runs = runs_df[runs_df["industry"] == selected_industry].sort_values("requested_at", ascending=False)
run_id = int(industry_runs.iloc[0]["id"])

df = get_run_financials_df(run_id)
if df.empty:
    st.warning("This run has no calculated financials.")
    st.stop()

company_names = sorted(df["corp_name"].unique().tolist())
selected_company = col2.selectbox("Company", options=company_names)

company_df = df[df["corp_name"] == selected_company].sort_values("fiscal_year")

curr = company_df.iloc[-1]
prev = company_df.iloc[-2] if len(company_df) >= 2 else None
fy = int(curr["fiscal_year"])

st.subheader(f"{selected_company} · {curr['stock_code']} · {curr.get('market', '')}")

# ---- Investment scorecard (the three screening criteria, up top) ----
render_company_scorecard(curr)
st.divider()


def _pct_delta(field: str) -> str | None:
    if prev is None:
        return None
    v = curr.get(field)
    return f"{v:+.1%}" if v is not None and not pd.isna(v) else None


def _pp_delta(field: str) -> str | None:
    if prev is None:
        return None
    v = curr.get(field)
    return f"{v:+.1%}p" if v is not None and not pd.isna(v) else None


# ---- Risk / status badges ----
badge_bits = []
if bool(curr.get("has_convertible_instruments")):
    badge_bits.append((":material/warning: Convertible debt — dilution risk", "orange"))
if bool(company_df["equity_impaired"].any()):
    badge_bits.append((":material/error: Equity impaired (some year)", "red"))
fcf = curr.get("free_cash_flow")
if fcf is not None and not pd.isna(fcf):
    badge_bits.append((":material/payments: FCF positive" if fcf > 0 else ":material/payments: FCF negative",
                       "green" if fcf > 0 else "red"))
om_chg = curr.get("operating_margin_change_yoy")
if om_chg is not None and not pd.isna(om_chg):
    badge_bits.append((":material/trending_up: Margin expanding" if om_chg > 0 else ":material/trending_down: Margin contracting",
                       "green" if om_chg > 0 else "red"))
if badge_bits:
    badge_cols = st.columns(len(badge_bits))
    for slot, (text, color) in zip(badge_cols, badge_bits):
        slot.badge(text, color=color)

# ---- Headline KPI cards (latest FY, with YoY deltas) ----
st.markdown(f"##### Headline — FY{fy}")
rev_delta = None
if prev is not None and pd.notna(curr.get("revenue")) and pd.notna(prev.get("revenue")) and prev["revenue"]:
    rev_delta = f"{(curr['revenue'] - prev['revenue']) / abs(prev['revenue']):+.1%}"

k1, k2, k3, k4 = st.columns(4)
k1.metric("Revenue", human_won(curr.get("revenue")), delta=rev_delta)
k2.metric("Operating Income", human_won(curr.get("operating_income")), delta=_pct_delta("operating_income_growth_yoy"))
k3.metric("Net Income", human_won(curr.get("net_income")), delta=_pct_delta("net_income_growth_yoy"))
k4.metric("Free Cash Flow", human_won(curr.get("free_cash_flow")))

q1, q2, q3, q4 = st.columns(4)
q1.metric("Operating Margin", f"{curr['operating_margin']:.1%}" if pd.notna(curr.get("operating_margin")) else "—",
          delta=_pp_delta("operating_margin_change_yoy"))
q2.metric("Net Margin", f"{curr['net_margin']:.1%}" if pd.notna(curr.get("net_margin")) else "—",
          delta=_pp_delta("net_margin_change_yoy"))
de_delta = None
if prev is not None and pd.notna(curr.get("debt_to_equity")) and pd.notna(prev.get("debt_to_equity")):
    de_delta = f"{curr['debt_to_equity'] - prev['debt_to_equity']:+.2f}"
q3.metric("Debt / Equity", f"{curr['debt_to_equity']:.2f}" if pd.notna(curr.get("debt_to_equity")) else "—",
          delta=de_delta, delta_color="inverse")
q4.metric("Basis", curr.get("fs_div_used") or "—", help="CFS = 연결 (consolidated), OFS = 별도 (separate).")

st.divider()

st.plotly_chart(
    multi_year_line(company_df, ["revenue", "gross_profit", "operating_income", "net_income"], "Earnings"),
    width="stretch",
)
st.plotly_chart(
    multi_year_line(
        company_df, ["gross_margin", "operating_margin", "net_margin"], "Margins (Gross / Operating / Net)",
        y_format=".1%",
    ),
    width="stretch",
)
st.caption(
    "Criterion ①: margins expanding alongside rising revenue/operating income means profitability is "
    "improving faster than the top line, not just along with it."
)
st.plotly_chart(
    multi_year_line(company_df, ["operating_cash_flow", "capex", "free_cash_flow"], "Cash Flow Quality"),
    width="stretch",
)
dcol1, dcol2 = st.columns(2)
dcol1.plotly_chart(
    multi_year_line(
        company_df, ["short_term_borrowings", "long_term_borrowings", "total_debt"], "Debt Levels"
    ),
    width="stretch",
)
dcol2.plotly_chart(
    multi_year_line(company_df, ["shares_outstanding"], "Shares Outstanding (dilution)"),
    width="stretch",
)
dcol2.caption("Criterion ②: a rising line = dilution from new issuance / convertible conversions.")

st.subheader("Per-Year Detail — Growth, Margins, Dilution & Leverage")
ratio_cols = [
    "fiscal_year", "revenue_growth_yoy", "operating_income_growth_yoy", "net_income_growth_yoy",
    "gross_margin", "operating_margin", "net_margin",
    "gross_margin_change_yoy", "operating_margin_change_yoy",
    "shares_outstanding", "share_count_change_yoy",
    "free_cash_flow", "reinvestment_ratio_capex_ocf", "total_debt", "debt_to_equity",
    "has_convertible_instruments",
]
st.dataframe(
    style_financial_table(company_df[ratio_cols]),
    width="stretch",
    hide_index=True,
    column_config=build_column_config(ratio_cols),
)
st.caption(
    "🟢 green = improving / healthy · 🔴 red = deteriorating / loss · 🟠 amber = elevated leverage or risk flag. "
    "Hover over a column header for its definition/formula."
)

st.subheader("연결(CFS) / 별도(OFS) basis used per year")
basis_cols = ["fiscal_year", "fs_div_used"]
st.dataframe(
    company_df[basis_cols], width="stretch", hide_index=True, column_config=build_column_config(basis_cols)
)
