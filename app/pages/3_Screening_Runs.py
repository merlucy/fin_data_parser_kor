import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.column_specs import build_column_config  # noqa: E402
from app.components.data_access import get_recent_runs, get_run_financials_df  # noqa: E402
from app.components.styling import decorate_run_status  # noqa: E402

st.set_page_config(page_title="Screening Runs", page_icon="🗂️", layout="wide")
st.title("🗂️ Screening Run History")

runs_df = get_recent_runs(limit=100)
if runs_df.empty:
    st.info("No screening runs yet. Go to Home and run a screen first.")
    st.stop()

run_cols = ["id", "industry", "status", "company_count", "fiscal_year_end", "history_years", "requested_at"]
st.dataframe(
    decorate_run_status(runs_df[run_cols]),
    width="stretch",
    hide_index=True,
    column_config=build_column_config(run_cols),
)

st.divider()
st.subheader("Compare two runs of the same industry")
industries = sorted(runs_df["industry"].dropna().unique().tolist())
industry = st.selectbox("Industry", options=industries)
industry_runs = runs_df[runs_df["industry"] == industry].sort_values("requested_at", ascending=False)

if len(industry_runs) < 2:
    st.caption("Only one run exists for this industry so far — re-run the screen later to compare.")
else:
    metric_options = {
        "Operating Income": "operating_income",
        "Net Income": "net_income",
        "Operating Margin": "operating_margin",
        "Free Cash Flow": "free_cash_flow",
        "Debt / Equity": "debt_to_equity",
    }
    col1, col2, col3 = st.columns(3)
    run_a = col1.selectbox("Run A", options=industry_runs["id"].tolist(), key="run_a")
    run_b = col2.selectbox("Run B", options=industry_runs["id"].tolist(), index=1, key="run_b")
    metric_label = col3.selectbox("Metric", options=list(metric_options.keys()))
    metric = metric_options[metric_label]

    df_a = get_run_financials_df(run_a)
    df_b = get_run_financials_df(run_b)

    if not df_a.empty and not df_b.empty and metric in df_a.columns and metric in df_b.columns:
        latest_a = df_a[df_a["fiscal_year"] == df_a["fiscal_year"].max()][["corp_code", "corp_name", metric]]
        latest_b = df_b[df_b["fiscal_year"] == df_b["fiscal_year"].max()][["corp_code", metric]]
        merged = latest_a.merge(latest_b, on="corp_code", suffixes=("_a", "_b"))
        merged["delta"] = merged[f"{metric}_b"] - merged[f"{metric}_a"]
        merged = merged.rename(
            columns={"corp_name": "Company", f"{metric}_a": f"Run #{run_a}", f"{metric}_b": f"Run #{run_b}", "delta": "Δ"}
        )
        is_pct = metric in ("operating_margin",)
        num_fmt = "percent" if is_pct else ("%,.2f" if metric == "debt_to_equity" else "%,.0f")
        st.dataframe(
            merged[["Company", f"Run #{run_a}", f"Run #{run_b}", "Δ"]],
            width="stretch",
            hide_index=True,
            column_config={
                f"Run #{run_a}": st.column_config.NumberColumn(format=num_fmt),
                f"Run #{run_b}": st.column_config.NumberColumn(format=num_fmt),
                "Δ": st.column_config.NumberColumn(format=num_fmt, help="Run B minus Run A."),
            },
        )
