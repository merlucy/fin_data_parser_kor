"""Shared column metadata for st.dataframe tables: display labels, hover-tooltip
descriptions/formulas, and number formatting. Keeps both the Sector Dashboard
and Company Detail pages consistent and avoids repeating this in every page.
"""

from __future__ import annotations

import streamlit as st

CURRENCY_FMT = "%,.0f"  # KRW amounts: whole won, comma-grouped (e.g. "258,935,494,000,000")
RATIO_FMT = "%,.2f"  # e.g. debt/equity, capex/OCF
PERCENT_FMT = "percent"  # underlying value is already a fraction (0.10 -> "10.00%")

# kind: "currency" | "ratio" | "percent" | "text" | "bool" | "int" | "year" | "datetime"
COLUMN_SPECS: dict[str, dict] = {
    # --- screening run columns ---
    "id": {"label": "Run #", "kind": "int", "help": "Screening run identifier."},
    "status": {"label": "Status", "kind": "text", "help": "completed / partial / running / failed."},
    "company_count": {"label": "Companies", "kind": "int", "help": "Number of companies included in this run."},
    "fiscal_year_end": {"label": "Latest FY", "kind": "year", "help": "Most recent fiscal year covered by the run."},
    "history_years": {"label": "Years", "kind": "int", "help": "Number of historical fiscal years pulled."},
    "requested_at": {"label": "Run At", "kind": "datetime", "help": "When the screening run was launched (UTC)."},
    # --- company / financial columns ---
    "corp_name": {"label": "Company", "kind": "text", "help": "Company name."},
    "stock_code": {"label": "Ticker", "kind": "text", "help": "KRX 6-digit stock code."},
    "market": {"label": "Market", "kind": "text", "help": "KOSPI or KOSDAQ."},
    "industry": {"label": "Industry", "kind": "text", "help": "KIND industry classification (KSIC-based)."},
    "sector": {
        "label": "Sector",
        "kind": "text",
        "help": "Broader sector grouping. Not currently populated for any company (see Industry instead).",
    },
    "is_active": {
        "label": "Active Listing",
        "kind": "bool",
        "help": "True if the company is currently an active KRX listing in our universe snapshot.",
    },
    "fiscal_year": {"label": "Fiscal Year", "kind": "year", "help": "Fiscal year of the annual report (사업보고서)."},
    "fs_div_used": {
        "label": "Basis",
        "kind": "text",
        "help": (
            "Financial statement basis used for this year: CFS (연결, consolidated) or "
            "OFS (별도, separate). Falls back to OFS only when CFS is unavailable for that company-year."
        ),
    },
    "revenue": {
        "label": "Revenue",
        "kind": "currency",
        "help": "매출액 — total revenue for the fiscal year, in KRW.",
    },
    "gross_profit": {
        "label": "Gross Profit",
        "kind": "currency",
        "help": "매출총이익 = 매출액 − 매출원가 (Revenue − Cost of Goods Sold), in KRW.",
    },
    "operating_income": {
        "label": "Operating Income",
        "kind": "currency",
        "help": "영업이익 — operating profit before interest/tax, in KRW.",
    },
    "net_income": {
        "label": "Net Income",
        "kind": "currency",
        "help": "당기순이익 — bottom-line net income for the fiscal year, in KRW.",
    },
    "total_assets": {"label": "Total Assets", "kind": "currency", "help": "자산총계, in KRW."},
    "total_liabilities": {"label": "Total Liabilities", "kind": "currency", "help": "부채총계, in KRW."},
    "total_equity": {"label": "Total Equity", "kind": "currency", "help": "자본총계, in KRW."},
    "operating_cash_flow": {
        "label": "Operating Cash Flow",
        "kind": "currency",
        "help": "영업활동현금흐름 — cash generated from operations, in KRW.",
    },
    "capex": {
        "label": "CapEx",
        "kind": "currency",
        "help": (
            "자본적지출 — sum of 유형자산의 취득 (PP&E acquisitions) + 무형자산의 취득 "
            "(intangible asset acquisitions) from the investing cash flow section, in KRW."
        ),
    },
    "depreciation_amortization": {
        "label": "D&A",
        "kind": "currency",
        "help": (
            "감가상각비 + 무형자산상각비 — depreciation & amortization add-back from the operating "
            "cash flow section. Often unavailable (blank) for large consolidated filers that bundle "
            "this into a single 조정(adjustments) line instead of disclosing it separately."
        ),
    },
    "free_cash_flow": {
        "label": "Free Cash Flow",
        "kind": "currency",
        "help": "Free Cash Flow = Operating Cash Flow − CapEx, in KRW.",
    },
    "reinvestment_ratio_capex_da": {
        "label": "CapEx / D&A",
        "kind": "ratio",
        "help": (
            "CapEx ÷ D&A. >1 means capital spending exceeds the depreciation/amortization of "
            "existing assets (net reinvestment); requires D&A to be disclosed on the face cash "
            "flow statement, so this is blank for many large filers (see D&A column)."
        ),
    },
    "reinvestment_ratio_capex_ocf": {
        "label": "CapEx / OCF",
        "kind": "ratio",
        "help": "CapEx as a share of Operating Cash Flow. Blank when OCF is zero or negative.",
    },
    "short_term_borrowings": {
        "label": "ST Borrowings",
        "kind": "currency",
        "help": "단기차입금 + 유동성장기차입금 (current portion of long-term debt), in KRW.",
    },
    "long_term_borrowings": {
        "label": "LT Borrowings",
        "kind": "currency",
        "help": "장기차입금 — non-current borrowings, in KRW.",
    },
    "total_debt": {
        "label": "Total Debt",
        "kind": "currency",
        "help": (
            "Sum of all interest-bearing debt: ST + LT borrowings, 사채(bonds), and convertible "
            "instruments (전환사채/신주인수권부사채/교환사채). This is interest-bearing debt, not "
            "total liabilities."
        ),
    },
    "debt_to_equity": {
        "label": "Debt / Equity",
        "kind": "ratio",
        "help": "Total Debt ÷ Total Equity. Blank when equity is zero or negative (see Equity Impaired).",
    },
    "equity_impaired": {
        "label": "Equity Impaired",
        "kind": "bool",
        "help": "True when 자본총계 (Total Equity) is zero or negative for that year.",
    },
    "has_convertible_instruments": {
        "label": "Has Convertible Debt",
        "kind": "bool",
        "help": (
            "True if the balance sheet discloses 전환사채 (convertible bonds), 신주인수권부사채 "
            "(bonds with warrants), or 교환사채 (exchangeable bonds) — instruments that can dilute "
            "existing shareholders upon conversion."
        ),
    },
    "convertible_instruments_value": {
        "label": "Convertible Debt Value",
        "kind": "currency",
        "help": "Carrying value of disclosed convertible bonds / bonds with warrants / exchangeable bonds, in KRW.",
    },
    "gross_profit_growth_yoy": {
        "label": "Gross Profit YoY",
        "kind": "percent",
        "help": "Year-over-year change in gross profit = (current − prior) ÷ |prior|.",
    },
    "operating_income_growth_yoy": {
        "label": "Op. Income YoY",
        "kind": "percent",
        "help": "Year-over-year change in operating income = (current − prior) ÷ |prior|.",
    },
    "net_income_growth_yoy": {
        "label": "Net Income YoY",
        "kind": "percent",
        "help": "Year-over-year change in net income = (current − prior) ÷ |prior|.",
    },
    "gross_profit_cagr_5y": {
        "label": "Gross Profit CAGR",
        "kind": "percent",
        "help": (
            "Compound annual growth rate of gross profit over the full screening window: "
            "(last year ÷ first year)^(1/years) − 1. Only computed when both endpoints are positive."
        ),
    },
    "operating_income_cagr_5y": {
        "label": "Op. Income CAGR",
        "kind": "percent",
        "help": (
            "Compound annual growth rate of operating income over the full screening window: "
            "(last year ÷ first year)^(1/years) − 1. Only computed when both endpoints are positive."
        ),
    },
    "net_income_cagr_5y": {
        "label": "Net Income CAGR",
        "kind": "percent",
        "help": (
            "Compound annual growth rate of net income over the full screening window: "
            "(last year ÷ first year)^(1/years) − 1. Only computed when both endpoints are positive."
        ),
    },
    "operating_margin": {
        "label": "Operating Margin",
        "kind": "percent",
        "help": "Operating Income ÷ Revenue (영업이익 ÷ 매출액) for the fiscal year.",
    },
    "net_margin": {
        "label": "Net Margin",
        "kind": "percent",
        "help": "Net Income ÷ Revenue (당기순이익 ÷ 매출액) for the fiscal year.",
    },
    "operating_margin_change_yoy": {
        "label": "Op. Margin Δ YoY",
        "kind": "percent",
        "help": (
            "Year-over-year change in operating margin, in percentage points (e.g. 15%→18% = "
            "+3.0pp). Positive = margin expansion, negative = margin contraction."
        ),
    },
    "net_margin_change_yoy": {
        "label": "Net Margin Δ YoY",
        "kind": "percent",
        "help": (
            "Year-over-year change in net margin, in percentage points (e.g. 8%→6% = -2.0pp). "
            "Positive = margin expansion, negative = margin contraction."
        ),
    },
    "gross_margin": {
        "label": "Gross Margin",
        "kind": "percent",
        "help": "Gross Profit ÷ Revenue (매출총이익 ÷ 매출액).",
    },
    "gross_margin_change_yoy": {
        "label": "Gross Margin Δ YoY",
        "kind": "percent",
        "help": "Year-over-year change in gross margin, in percentage points.",
    },
    "revenue_growth_yoy": {
        "label": "Revenue YoY",
        "kind": "percent",
        "help": "Year-over-year revenue growth = (current − prior) ÷ |prior|.",
    },
    "revenue_cagr_5y": {
        "label": "Revenue CAGR",
        "kind": "percent",
        "help": "Compound annual growth rate of revenue over the screening window.",
    },
    # --- shares / dilution ---
    "shares_outstanding": {
        "label": "Shares Outstanding",
        "kind": "count",
        "help": "Total issued common shares (보통주 발행주식의 총수) from DART 주식의 총수 현황.",
    },
    "share_count_change_yoy": {
        "label": "Shares Δ YoY",
        "kind": "percent",
        "help": (
            "Year-over-year change in issued common shares. Positive = dilution (new issuance / "
            "convertible conversions); negative = buyback cancellation."
        ),
    },
    # --- 5-year window deltas (evidence behind the scorecard) ---
    "gross_margin_change_5y": {
        "label": "Gross Margin Δ 5y",
        "kind": "percent",
        "help": "Gross margin change over the full window, in percentage points (latest − earliest).",
    },
    "operating_margin_change_5y": {
        "label": "Op. Margin Δ 5y",
        "kind": "percent",
        "help": "Operating margin change over the full window, in percentage points (latest − earliest).",
    },
    "net_margin_change_5y": {
        "label": "Net Margin Δ 5y",
        "kind": "percent",
        "help": "Net margin change over the full window, in percentage points (latest − earliest).",
    },
    "share_count_change_5y": {
        "label": "Shares Δ 5y",
        "kind": "percent",
        "help": "Total dilution over the window: relative change in issued shares (latest vs earliest). Lower is better.",
    },
    "total_debt_change_5y": {
        "label": "Total Debt Δ 5y",
        "kind": "percent",
        "help": "Relative change in interest-bearing debt over the window (latest vs earliest). Lower is better.",
    },
    # --- scorecard ---
    "score_margin_growth": {
        "label": "① Margin & Growth",
        "kind": "score",
        "help": (
            "0–2. Rewards 5y gross AND operating margin expansion together with meaningful (>5% CAGR) "
            "revenue and operating-profit growth."
        ),
    },
    "score_low_dilution": {
        "label": "② Low Dilution",
        "kind": "score",
        "help": "0–2. Rewards little/no increase in issued shares (≤2% over 5y) and no outstanding convertible instruments.",
    },
    "score_capital_efficiency": {
        "label": "③ Capital Efficiency",
        "kind": "score",
        "help": (
            "0–2. Rewards reinvesting (capex) and generating positive free cash flow with profit growth, "
            "WITHOUT increasing debt (≤5% over 5y)."
        ),
    },
    "score_overall": {
        "label": "★ Overall",
        "kind": "score_overall",
        "help": "Sum of the three pillar scores (0–6). Higher = better aligned with the screening criteria.",
    },
}


def build_column_config(columns: list[str]) -> dict[str, object]:
    """Build a st.dataframe column_config dict for the given columns, using COLUMN_SPECS."""
    config: dict[str, object] = {}
    for col in columns:
        spec = COLUMN_SPECS.get(col)
        if spec is None:
            continue
        kind = spec["kind"]
        label, help_text = spec["label"], spec["help"]
        if kind == "currency":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format=CURRENCY_FMT)
        elif kind == "ratio":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format=RATIO_FMT)
        elif kind == "percent":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format=PERCENT_FMT)
        elif kind == "int":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format="%,d")
        elif kind == "count":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format="%,.0f")
        elif kind == "year":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format="%d")
        elif kind == "score":
            config[col] = st.column_config.NumberColumn(label, help=help_text, format="%d", min_value=0, max_value=2)
        elif kind == "score_overall":
            config[col] = st.column_config.ProgressColumn(
                label, help=help_text, format="%d", min_value=0, max_value=6
            )
        elif kind == "bool":
            config[col] = st.column_config.CheckboxColumn(label, help=help_text)
        elif kind == "datetime":
            config[col] = st.column_config.DatetimeColumn(label, help=help_text, format="YYYY-MM-DD HH:mm")
        else:
            config[col] = st.column_config.TextColumn(label, help=help_text)
    return config
