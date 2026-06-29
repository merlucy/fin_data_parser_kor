import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.data_access import get_recent_runs, get_run_financials_df  # noqa: E402

st.set_page_config(page_title="Screening Runs", layout="wide")
st.title("Screening Run History")

runs_df = get_recent_runs(limit=100)
if runs_df.empty:
    st.info("No screening runs yet. Go to Home and run a screen first.")
    st.stop()

st.dataframe(
    runs_df[["id", "industry", "status", "company_count", "fiscal_year_end", "history_years", "requested_at"]],
    width="stretch",
    hide_index=True,
)

st.subheader("Compare two runs of the same industry")
industries = sorted(runs_df["industry"].dropna().unique().tolist())
industry = st.selectbox("Industry", options=industries)
industry_runs = runs_df[runs_df["industry"] == industry].sort_values("requested_at", ascending=False)

if len(industry_runs) < 2:
    st.caption("Only one run exists for this industry so far — re-run the screen later to compare.")
else:
    col1, col2 = st.columns(2)
    run_a = col1.selectbox("Run A", options=industry_runs["id"].tolist(), key="run_a")
    run_b = col2.selectbox("Run B", options=industry_runs["id"].tolist(), index=1, key="run_b")

    df_a = get_run_financials_df(run_a)
    df_b = get_run_financials_df(run_b)

    if not df_a.empty and not df_b.empty:
        latest_a = df_a[df_a["fiscal_year"] == df_a["fiscal_year"].max()]
        latest_b = df_b[df_b["fiscal_year"] == df_b["fiscal_year"].max()]
        merged = latest_a.merge(
            latest_b, on="corp_code", suffixes=(f"_run{run_a}", f"_run{run_b}")
        )
        compare_cols = [
            "corp_name" + f"_run{run_a}",
            f"operating_income_run{run_a}", f"operating_income_run{run_b}",
            f"debt_to_equity_run{run_a}", f"debt_to_equity_run{run_b}",
        ]
        available_cols = [c for c in compare_cols if c in merged.columns]
        st.dataframe(merged[available_cols], width="stretch", hide_index=True)
