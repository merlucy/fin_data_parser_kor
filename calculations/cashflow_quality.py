from __future__ import annotations

import pandas as pd

from calculations.statement_parser import get_metric


def compute(df: pd.DataFrame) -> dict:
    operating_cash_flow = get_metric(df, "operating_cash_flow")
    capex = get_metric(df, "capex")
    depreciation = get_metric(df, "depreciation")
    amortization = get_metric(df, "amortization")

    da_parts = [v for v in (depreciation, amortization) if v is not None]
    depreciation_amortization = sum(da_parts) if da_parts else None
    depreciation_source = "CF_addback" if da_parts else "missing"

    free_cash_flow = (
        operating_cash_flow - capex if operating_cash_flow is not None and capex is not None else None
    )

    reinvestment_ratio_capex_da = (
        capex / depreciation_amortization
        if capex is not None and depreciation_amortization not in (None, 0)
        else None
    )
    reinvestment_ratio_capex_ocf = (
        capex / operating_cash_flow
        if capex is not None and operating_cash_flow not in (None, 0) and operating_cash_flow > 0
        else None
    )

    return {
        "operating_cash_flow": operating_cash_flow,
        "capex": capex,
        "depreciation_amortization": depreciation_amortization,
        "depreciation_source": depreciation_source,
        "free_cash_flow": free_cash_flow,
        "reinvestment_ratio_capex_da": reinvestment_ratio_capex_da,
        "reinvestment_ratio_capex_ocf": reinvestment_ratio_capex_ocf,
    }
