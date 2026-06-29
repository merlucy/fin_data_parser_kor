import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.components.data_access import get_industries, get_recent_runs, trigger_run  # noqa: E402

st.set_page_config(page_title="KR Stock Screener", layout="wide")
st.title("Korean Stock Sector Screener")
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

st.subheader("Recent Screening Runs")
runs_df = get_recent_runs(limit=20)
if runs_df.empty:
    st.info("No screening runs yet. Pick an industry above and click Run Screen.")
else:
    st.dataframe(
        runs_df[["id", "industry", "status", "company_count", "fiscal_year_end", "history_years", "requested_at"]],
        width="stretch",
        hide_index=True,
    )
    st.caption("Open the **Sector Dashboard** or **Company Detail** pages in the sidebar to explore a run.")
