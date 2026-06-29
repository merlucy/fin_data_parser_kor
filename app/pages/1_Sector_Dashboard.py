import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.charts import sector_scatter, sector_trend_chart  # noqa: E402
from app.components.column_specs import build_column_config  # noqa: E402
from app.components.data_access import get_industries, get_recent_runs, get_run_financials_df  # noqa: E402
from app.components.styling import style_financial_table  # noqa: E402

st.set_page_config(page_title="Sector Dashboard", layout="wide")
st.title("📊 Sector Dashboard")

runs_df = get_recent_runs(limit=100)
if runs_df.empty:
    st.info("No screening runs yet. Go to Home and run a screen first.")
    st.stop()

industries = sorted(runs_df["industry"].dropna().unique().tolist())
col1, col2 = st.columns([2, 2])
selected_industry = col1.selectbox("Industry", options=industries)

industry_runs = runs_df[runs_df["industry"] == selected_industry].sort_values("requested_at", ascending=False)
run_options = {
    f"#{row.id} — {row.requested_at} ({row.status}, {row.company_count} companies)": row.id
    for row in industry_runs.itertuples()
}
selected_label = col2.selectbox("Screening run", options=list(run_options.keys()))
run_id = run_options[selected_label]

df = get_run_financials_df(run_id)
if df.empty:
    st.warning("This run has no calculated financials (likely failed before fetching any data).")
    st.stop()

latest_year = df["fiscal_year"].max()
latest_df = df[df["fiscal_year"] == latest_year].copy()

st.subheader(f"Sector Overview — FY{latest_year}")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Companies", latest_df["corp_code"].nunique())
m2.metric("Median Op. Income YoY", f"{latest_df['operating_income_growth_yoy'].median():.1%}"
          if latest_df["operating_income_growth_yoy"].notna().any() else "N/A")
m3.metric("Median Operating Margin", f"{latest_df['operating_margin'].median():.1%}"
          if latest_df["operating_margin"].notna().any() else "N/A")
m4.metric("Median Debt/Equity", f"{latest_df['debt_to_equity'].median():.2f}"
          if latest_df["debt_to_equity"].notna().any() else "N/A")
risk_count = int(latest_df["has_convertible_instruments"].sum() + latest_df["equity_impaired"].sum())
m5.metric("⚠️ Risk Flags", risk_count, help="Companies flagged for convertible debt (dilution) or impaired equity.")

# ---- Investment Scorecard (the three screening criteria, ranked) ----
st.subheader("🏆 Investment Scorecard")
st.caption(
    "Ranked by overall score (0–6). **①** 5y gross+operating margin expansion with meaningful revenue & "
    "profit growth · **②** low share dilution + no convertibles · **③** reinvesting with positive FCF "
    "WITHOUT adding debt. Hover any header for the formula."
)
score_cols = [
    "corp_name", "stock_code",
    "score_overall", "score_margin_growth", "score_low_dilution", "score_capital_efficiency",
    "revenue_cagr_5y", "gross_margin_change_5y", "operating_margin_change_5y",
    "share_count_change_5y", "total_debt_change_5y",
]
scorecard = latest_df[score_cols].sort_values("score_overall", ascending=False, na_position="last")
st.dataframe(
    style_financial_table(scorecard),
    width="stretch",
    hide_index=True,
    column_config=build_column_config(score_cols),
)

st.divider()


def _leader(frame, col, fmt, ascending=False):
    """Return (company_name, formatted_value) for the row with the best `col`, or None."""
    valid = frame.dropna(subset=[col])
    if valid.empty:
        return None
    row = valid.sort_values(col, ascending=ascending).iloc[0]
    return row["corp_name"], fmt(row[col])


st.markdown("##### 🏅 Criterion Leaders (5-year)")
lead_cols = st.columns(4)
_leaders = [
    ("★ Top Overall Score", _leader(latest_df, "score_overall", lambda v: f"{int(v)}/6")),
    ("① Biggest Margin Expansion", _leader(latest_df, "operating_margin_change_5y", lambda v: f"{v:+.1%}p")),
    ("② Least Dilution", _leader(latest_df, "share_count_change_5y", lambda v: f"{v:+.1%}", ascending=True)),
    ("③ Lowest Debt Growth", _leader(latest_df, "total_debt_change_5y", lambda v: f"{v:+.1%}", ascending=True)),
]
for slot, (title, result) in zip(lead_cols, _leaders):
    if result is None:
        slot.metric(title, "—")
    else:
        name, val = result
        slot.metric(title, val, delta=name, delta_color="off")

st.divider()
st.plotly_chart(sector_scatter(latest_df), width="stretch")

st.subheader("Margin & Free Cash Flow Trends Across the Sector")
st.caption(
    "One line per company. Use this alongside the Earnings/Revenue trends to see whether margin "
    "expansion or contraction is coinciding with revenue/profit growth, rather than just looking "
    "at growth in isolation."
)
trend_col1, trend_col2 = st.columns(2)
trend_col1.plotly_chart(
    sector_trend_chart(df, "operating_margin", "Operating Margin by Company", y_format=".1%"),
    width="stretch",
)
trend_col2.plotly_chart(
    sector_trend_chart(df, "net_margin", "Net Margin by Company", y_format=".1%"),
    width="stretch",
)
st.plotly_chart(
    sector_trend_chart(df, "free_cash_flow", "Free Cash Flow by Company"),
    width="stretch",
)

st.subheader("Ranked Companies — Full Detail")
display_cols = [
    "corp_name", "stock_code", "fs_div_used", "score_overall", "revenue", "operating_income", "net_income",
    "gross_margin", "operating_margin", "operating_margin_change_yoy",
    "operating_income_growth_yoy", "share_count_change_5y", "free_cash_flow", "total_debt_change_5y",
    "debt_to_equity", "has_convertible_instruments",
]
sort_options = {
    "Overall Score": "score_overall",
    "Operating Income Growth (YoY)": "operating_income_growth_yoy",
    "Operating Margin": "operating_margin",
    "Operating Margin Expansion (YoY)": "operating_margin_change_yoy",
    "Least Dilution (shares Δ5y)": "share_count_change_5y",
    "Free Cash Flow": "free_cash_flow",
    "Debt / Equity (lowest first)": "debt_to_equity",
}
sort_label = st.selectbox("Rank by", options=list(sort_options.keys()))
sort_col = sort_options[sort_label]
ascending = sort_col in ("debt_to_equity", "share_count_change_5y")
ranked = latest_df[display_cols].sort_values(sort_col, ascending=ascending, na_position="last")
st.dataframe(
    style_financial_table(ranked),
    width="stretch",
    hide_index=True,
    column_config=build_column_config(display_cols),
)
st.caption(
    "🟢 green = improving / healthy · 🔴 red = deteriorating / loss · 🟠 amber = elevated leverage or risk flag. "
    "Hover over a column header for its definition/formula."
)

fs_div_counts = df.groupby("fiscal_year")["fs_div_used"].value_counts().unstack(fill_value=0)
with st.expander("연결 (CFS) vs 별도 (OFS) basis used, by year"):
    st.dataframe(fs_div_counts, width="stretch")
