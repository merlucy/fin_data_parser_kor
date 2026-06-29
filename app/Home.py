import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.components.column_specs import build_column_config  # noqa: E402
from app.components.data_access import get_industries, get_recent_runs, trigger_run  # noqa: E402
from app.components.styling import decorate_run_status  # noqa: E402

st.set_page_config(page_title="KR Stock Screener", page_icon="📈", layout="wide")
st.title("📈 Korean Stock Sector Screener")
st.caption("Powered by OpenDART financial statements + KIND industry classification.")

industries = get_industries()

with st.form("run_screen_form"):
    col1, col2 = st.columns([3, 1])
    industry = col1.selectbox("Industry", options=industries)
    history_years = col2.number_input("History (years)", min_value=2, max_value=10, value=5)
    submitted = st.form_submit_button("Run Screen")

if submitted and industry:
    with st.spinner(f"Screening '{industry}'... fetching/calculating financial data"):
        try:
            run_id = trigger_run(industry, history_years=history_years)
            st.success(f"Screening run #{run_id} completed for '{industry}'.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Screening run failed: {e}")

st.divider()
st.subheader("Recent Screening Runs")
runs_df = get_recent_runs(limit=20)
if runs_df.empty:
    st.info("No screening runs yet. Pick an industry above and click Run Screen.")
else:
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Runs Shown", len(runs_df))
    s2.metric("Industries Covered", runs_df["industry"].nunique())
    s3.metric("Companies Screened", int(runs_df["company_count"].fillna(0).sum()))

    run_cols = ["id", "industry", "status", "company_count", "fiscal_year_end", "history_years", "requested_at"]
    st.dataframe(
        decorate_run_status(runs_df[run_cols]),
        width="stretch",
        hide_index=True,
        column_config=build_column_config(run_cols),
    )
    st.caption("Open the **Sector Dashboard** or **Company Detail** pages in the sidebar to explore a run.")
