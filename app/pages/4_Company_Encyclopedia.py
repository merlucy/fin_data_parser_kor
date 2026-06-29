import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.components.column_specs import build_column_config  # noqa: E402
from app.components.data_access import get_companies_df, get_industries  # noqa: E402

st.set_page_config(page_title="Company Encyclopedia", page_icon="📚", layout="wide")
st.title("📚 Company Encyclopedia")

_universe = get_companies_df()
u1, u2, u3 = st.columns(3)
u1.metric("Companies in Universe", len(_universe))
u2.metric("Industries", _universe["industry"].nunique())
u3.metric("KOSPI / KOSDAQ", f"{(_universe['market'] == 'KOSPI').sum()} / {(_universe['market'] == 'KOSDAQ').sum()}")
st.caption("Look up the industry classification for any KRX-listed company. Refreshed via jobs.refresh_universe.")

st.divider()
col1, col2 = st.columns([2, 2])
name_query = col1.text_input("🔎 Search by company name or ticker", placeholder="e.g. 삼성전자 or 005930")
industry_options = ["(All industries)"] + get_industries()
selected_industry = col2.selectbox("Filter by industry", options=industry_options)
industry_filter = None if selected_industry == "(All industries)" else selected_industry

df = get_companies_df(name_query=name_query or None, industry=industry_filter)

st.subheader(f"{len(df)} companies found")
if df.empty:
    st.info("No companies match this search. Try a different name/ticker or industry.")
else:
    display_cols = ["corp_name", "stock_code", "market", "industry", "sector", "is_active"]
    st.dataframe(
        df[display_cols],
        width="stretch",
        hide_index=True,
        column_config=build_column_config(display_cols),
    )
    st.caption(
        "Hover over a column header for its definition. 'Sector' is not yet populated for any "
        "company — see Industry for the available classification."
    )
