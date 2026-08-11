"""
============================================================
Constants for DCF 

Constants used throughout Gold ETL pipelines.
============================================================
"""

from __future__ import annotations
import pandas as pd
import numpy as np


DCF_DEFAULTS = {
    "discount_rate": 0.09,
    "terminal_growth": 0.025,
    "projection_years": 10,
    "tax_rate": 0.15,
}

# ==========================================================
# Step 16 Function for DCF Assumptions
# ==========================================================

def calculate_revenue_growth_metrics(
    df: pd.DataFrame,
    revenue_column: str = "revenue",
    lookback_years: int = 5,
) -> pd.DataFrame:
    """
    Calculate historical revenue metrics for each company.

    Returns
    -------
    symbol
    revenue_cagr
    revenue_growth_avg
    earliest_revenue
    latest_revenue
    years_of_history
    """

    required_columns = [
        "symbol",
        "calendar_year",
        revenue_column
        ]

    missing = [
        c for c in required_columns
        if c not in df.columns
        ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df = (
        df
        .copy()
        .sort_values(
            ["symbol", "calendar_year"]
        )
    )

    results = []

    for symbol, group in df.groupby("symbol"):

        group = (
            group[
                ["calendar_year", revenue_column]
            ]
            .dropna()
            .sort_values("calendar_year")
        )

        if len(group) < 2:
            continue

        # -------------------------
        # Keep latest N years
        # -------------------------

        group = group.tail(lookback_years)

        beginning = group.iloc[0][revenue_column]
        ending = group.iloc[-1][revenue_column]

        periods = len(group) - 1

        if beginning <= 0 or ending <= 0:

            revenue_cagr = np.nan

        else:

            revenue_cagr = (
                (ending / beginning)
                ** (1 / periods)
            ) - 1

        growth_series = (
            group[revenue_column]
            .pct_change()
            .dropna()
        )

        revenue_growth_avg = (
            growth_series.mean()
            if len(growth_series)
            else np.nan
        )

        results.append({
            "symbol": symbol,
            "historical_growth_rate": revenue_cagr,
            "revenue_growth_avg": revenue_growth_avg,
            "earliest_revenue": beginning,
            "latest_revenue": ending,
            "years_of_history": len(group)
        })

    return pd.DataFrame(results)

# ==========================================================
# Step 17 Function for DCF Intrinsic Value
# ==========================================================

def forecast_free_cash_flows(
    starting_fcf: float,
    growth_rate: float,
    projection_years: int
) -> list:
    """
    Forecast future Free Cash Flows using a constant growth model.
    """
    cashflows = []
    fcf = starting_fcf
    for _ in range(projection_years):
        fcf *= (1 + growth_rate)
        cashflows.append(fcf)
    return cashflows

def discount_cash_flows(
    cashflows: list,
    discount_rate: float
) -> list:
    """
    Discount projected cash flows to present value.
    """
    discounted = []
    for year, cashflow in enumerate(cashflows, start=1):
        pv = cashflow / ((1 + discount_rate) ** year)
        discounted.append(pv)
    return discounted

def calculate_terminal_value(
    last_fcf: float,
    terminal_growth: float,
    discount_rate: float
) -> float:
    """
    Gordon Growth Terminal Value.
    """
    terminal_fcf = last_fcf * (1 + terminal_growth)
    terminal_value = (
        terminal_fcf/(discount_rate - terminal_growth))
    return terminal_value

def discount_terminal_value(
    terminal_value: float,
    discount_rate: float,
    projection_years: int
) -> float:
    """
    Discount Terminal Value to Present Value.
    """
    return (
        terminal_value/((1 + discount_rate) ** projection_years))

def calculate_enterprise_value(
    discounted_cashflows: list,
    discounted_terminal_value: float
) -> float:
    """
    Enterprise Value =
    Sum of discounted projected cash flows +
    Discounted terminal value.
    """
    enterprise_value = (
        sum(discounted_cashflows)
        + discounted_terminal_value)
    return enterprise_value

def calculate_equity_value(
    enterprise_value: float,
    net_debt: float
) -> float:
    """
    Equity Value =
    Enterprise Value - Net Debt

    Net debt may be negative if a company holds more cash than debt,
    which will increase the equity value.
    """
    return enterprise_value - net_debt

def calculate_intrinsic_value(
    equity_value: float,
    shares_outstanding: float
) -> float:
    """
    Calculate intrinsic value per share.
    """
    if shares_outstanding <= 0:
        return None
    return ( equity_value/ shares_outstanding)

def calculate_margin_of_safety(
    intrinsic_value: float,
    current_price: float
) -> float:
    """
    Margin of Safety expressed as decimal.
    """
    if current_price <= 0:
        return None
    
    return (intrinsic_value-current_price) / current_price
