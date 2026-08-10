"""
============================================================
Constants for DCF 

Constants used throughout Gold ETL pipelines.
============================================================
"""

import pandas as pd

DCF_DEFAULTS = {
    "discount_rate": 0.09,
    "terminal_growth": 0.025,
    "projection_years": 10,
    "tax_rate": 0.15,
}

# ==========================================================
# Step 17 Function for DCF
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
    Sum of discounted cash flows +
    Discounted Terminal Value
    """
    return (
        sum(discounted_cashflows)+discounted_terminal_value)

def calculate_intrinsic_value(
    enterprise_value: float,
    shares_outstanding: float
) -> float:
    """
    Calculate intrinsic value per share.
    """
    if shares_outstanding <= 0:
        return None
    return (enterprise_value/shares_outstanding)

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

