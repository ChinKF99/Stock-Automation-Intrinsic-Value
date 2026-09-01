"""
============================================================
Constants for DCF 

Constants used throughout Gold ETL pipelines.
============================================================
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import math

DCF_DEFAULTS = {
    "terminal_growth": 0.025,
    "projection_years": 10,
    "tax_rate": 0.15,
}

# ==========================================================
# Step 16 Function for DCF Assumptions
# ==========================================================

def calculate_historical_growth(
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

def calculate_average_fcf(financials, years=3):
    """
    Calculate average Free Cash Flow over the latest N years.
    """

    financials = financials.sort_values(
        ["symbol", "calendar_year"]
    )

    avg_fcf = (
        financials
        .groupby("symbol")
        .tail(years)
        .groupby("symbol")["free_cash_flow"]
        .mean()
        .reset_index()
        .rename(columns={
            "free_cash_flow": "starting_fcf"
        })
    )

    return avg_fcf

def calculate_discount_rate(
    beta,
    risk_free_rate=0.04,
    market_premium=0.05
):
    """
    Calculate Cost of Equity using a simplified CAPM.
    """

    if beta is None:
        beta = 1

    return risk_free_rate + beta * market_premium

# ==========================================================
# Step 17 & 18 Function for DCF Intrinsic Value
# ==========================================================

def get_growth_rate(
    initial_growth,
    terminal_growth,
    year,
    projection_years
):
    """
    Linearly reduce growth from the initial growth rate
    to the terminal growth rate.
    """

    if projection_years <= 1:
        return terminal_growth

    step = (
        initial_growth - terminal_growth
    ) / (projection_years - 1)

    growth = initial_growth - (
        step * (year - 1)
    )

    return max(growth, terminal_growth)

def forecast_free_cash_flows(
    starting_fcf: float,
    initial_growth: float,
    terminal_growth: float,
    projection_years: int
) -> list:
    """
    Forecast future Free Cash Flows using a constant growth model.
    """
    forecast = []
    fcf = starting_fcf
    for year in range(1, projection_years + 1):
        growth = get_growth_rate(
            initial_growth,
            terminal_growth,
            year,
            projection_years
        )
        fcf *= (1 + growth)
        forecast.append(fcf)
    return forecast

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
    calculated_ev = (
        sum(discounted_cashflows)
        + discounted_terminal_value)
    return calculated_ev

# Main Loop to carry out the above listed function
def calculate_dcf_enterprise_value(
    starting_fcf: float,
    growth_rate: float,
    discount_rate: float,
    terminal_growth: float,
    projection_years: int
) -> dict:
    """
    Calculate a complete DCF valuation.

    Returns every intermediate result so both
    Step17 and Step18 can reuse it.
    """

    # -------------------------------------
    # Forecast FCF
    # -------------------------------------

    forecast_cashflows = forecast_free_cash_flows(
        starting_fcf=starting_fcf,
        initial_growth=growth_rate,
        terminal_growth=terminal_growth,
        projection_years=projection_years
    )

    # -------------------------------------
    # Discount FCF
    # -------------------------------------

    discounted_cashflows = discount_cash_flows(
        forecast_cashflows,
        discount_rate
    )

    # -------------------------------------
    # Terminal Value
    # -------------------------------------

    terminal_value = calculate_terminal_value(
        forecast_cashflows[-1],
        terminal_growth,
        discount_rate
    )

    # -------------------------------------
    # Discount Terminal Value
    # -------------------------------------

    discounted_terminal_value = discount_terminal_value(
        terminal_value,
        discount_rate,
        projection_years
    )

    # -------------------------------------
    # Enterprise Value
    # -------------------------------------

    calculated_ev = calculate_enterprise_value(
        discounted_cashflows,
        discounted_terminal_value
    )

    return {
        "forecast_cashflows": forecast_cashflows,
        "discounted_cashflows": discounted_cashflows,
        "terminal_value": terminal_value,
        "discounted_terminal_value": discounted_terminal_value,
        "calculated_ev": calculated_ev
    }

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

def solve_implied_growth(
    starting_fcf,
    target_enterprise_value,
    discount_rate,
    terminal_growth,
    projection_years,
    max_iterations=100,
):
    low = -0.50
    high = 0.80

    absolute_tolerance = target_enterprise_value * 0.001

    for i in range(max_iterations):

        growth = (low + high) / 2

        cashflows = forecast_free_cash_flows(
            starting_fcf,
            growth,
            terminal_growth,
            projection_years
        )

        pv = discount_cash_flows(
            cashflows,
            discount_rate
        )

        tv = calculate_terminal_value(
            cashflows[-1],
            terminal_growth,
            discount_rate
        )

        pv_tv = discount_terminal_value(
            tv,
            discount_rate,
            projection_years
        )

        ev = calculate_enterprise_value(
            pv,
            pv_tv
        )

        difference = target_enterprise_value - ev

        if abs(difference) <= absolute_tolerance:
            return {
                "growth": growth,
                "iterations": i + 1,
                "difference": abs(difference),
                "converged": True
            }

        if ev < target_enterprise_value:
            low = growth
        else:
            high = growth

    return {
        "growth": growth,
        "iterations": max_iterations,
        "difference": abs(difference),
        "converged": False
    }
