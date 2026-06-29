import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.charts import multi_year_line  # noqa: E402
from app.components.data_access import get_recent_runs, get_run_financials_df  # noqa: E402

st.set_page_config(page_title="Company Detail", layout="wide")
st.title("Company Detail")

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

st.subheader(f"{selected_company} — {company_df['stock_code'].iloc[0]}")

st.plotly_chart(
    multi_year_line(company_df, ["revenue", "gross_profit", "operating_income", "net_income"], "Earnings"),
    width="stretch",
)
st.plotly_chart(
    multi_year_line(company_df, ["operating_cash_flow", "capex", "free_cash_flow"], "Cash Flow Quality"),
    width="stretch",
)
st.plotly_chart(
    multi_year_line(
        company_df, ["short_term_borrowings", "long_term_borrowings", "total_debt"], "Debt Levels"
    ),
    width="stretch",
)

st.subheader("Growth & Leverage Ratios")
ratio_cols = [
    "fiscal_year", "operating_income_growth_yoy", "net_income_growth_yoy",
    "reinvestment_ratio_capex_ocf", "debt_to_equity", "has_convertible_instruments",
]
st.dataframe(company_df[ratio_cols], width="stretch", hide_index=True)

st.subheader("연결(CFS) / 별도(OFS) basis used per year")
st.dataframe(company_df[["fiscal_year", "fs_div_used"]], width="stretch", hide_index=True)
