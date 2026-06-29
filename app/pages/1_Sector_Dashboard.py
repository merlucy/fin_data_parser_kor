import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.charts import sector_scatter  # noqa: E402
from app.components.data_access import get_industries, get_recent_runs, get_run_financials_df  # noqa: E402

st.set_page_config(page_title="Sector Dashboard", layout="wide")
st.title("Sector Dashboard")

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
m1, m2, m3, m4 = st.columns(4)
m1.metric("Companies", latest_df["corp_code"].nunique())
m2.metric("Median Op. Income YoY", f"{latest_df['operating_income_growth_yoy'].median():.1%}"
          if latest_df["operating_income_growth_yoy"].notna().any() else "N/A")
m3.metric("Median Debt/Equity", f"{latest_df['debt_to_equity'].median():.2f}"
          if latest_df["debt_to_equity"].notna().any() else "N/A")
m4.metric("With Convertible Debt", int(latest_df["has_convertible_instruments"].sum()))

st.plotly_chart(sector_scatter(latest_df), width="stretch")

st.subheader("Ranked Companies")
display_cols = [
    "corp_name", "stock_code", "fs_div_used", "revenue", "operating_income", "net_income",
    "operating_income_growth_yoy", "free_cash_flow", "debt_to_equity", "has_convertible_instruments",
]
st.dataframe(
    latest_df[display_cols].sort_values("operating_income_growth_yoy", ascending=False),
    width="stretch",
    hide_index=True,
)

fs_div_counts = df.groupby("fiscal_year")["fs_div_used"].value_counts().unstack(fill_value=0)
with st.expander("연결 (CFS) vs 별도 (OFS) basis used, by year"):
    st.dataframe(fs_div_counts, width="stretch")
