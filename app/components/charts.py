from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def sector_scatter(latest_df: pd.DataFrame) -> go.Figure:
    """Growth vs leverage scatter, bubble size = revenue, one point per company."""
    df = latest_df.dropna(subset=["debt_to_equity", "operating_income_growth_yoy"]).copy()
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").abs()
    df["debt_to_equity"] = pd.to_numeric(df["debt_to_equity"], errors="coerce")
    df["operating_income_growth_yoy"] = pd.to_numeric(df["operating_income_growth_yoy"], errors="coerce")
    fig = px.scatter(
        df,
        x="debt_to_equity",
        y="operating_income_growth_yoy",
        size="revenue",
        color="corp_name",
        hover_name="corp_name",
        labels={
            "debt_to_equity": "Debt / Equity",
            "operating_income_growth_yoy": "Operating Income YoY Growth",
        },
        title="Growth vs. Leverage",
    )
    if not df.empty:
        fig.add_hline(y=df["operating_income_growth_yoy"].median(), line_dash="dot", opacity=0.4)
        fig.add_vline(x=df["debt_to_equity"].median(), line_dash="dot", opacity=0.4)
    fig.update_layout(yaxis_tickformat=".0%")
    return fig


def multi_year_line(df: pd.DataFrame, y_cols: list[str], title: str, y_format: str | None = None) -> go.Figure:
    fig = go.Figure()
    for col in y_cols:
        fig.add_trace(go.Scatter(x=df["fiscal_year"], y=df[col], mode="lines+markers", name=col))
    fig.update_layout(title=title, xaxis_title="Fiscal Year")
    if y_format:
        fig.update_yaxes(tickformat=y_format)
    return fig
