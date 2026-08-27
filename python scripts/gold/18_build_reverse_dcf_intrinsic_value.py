"""
============================================================
18_build_reverse_dcf_intrinsic_value.py

Build gold table reverse DCF Intrinsic Value using data from
from gold table.

Source
------
16_build_dcf_assumptions.py

Target:
    gold.build_reverse_dcf_intrinsic_value
============================================================
"""

from pathlib import Path
import sys
import pandas as pd

# ==========================================================
# Make project root importable
# ==========================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Project Imports
# ==========================================================

from config.config import (
    get_sqlalchemy_engine
)

from utils.sql_utils import (
    GOLD_SCHEMA,
    GOLD_16_SCHEMA_TABLE,
    GOLD_18_TABLE,
    GOLD_18_SCHEMA_TABLE,
    print_connection_info,
    ensure_schema,
    get_row_count,
    load_dataframe_to_sql,
    load_table,
    )

from utils.validation_utils import(
    validate_primary_key,
    validate_columns,
    validate_nulls,
    validate_row_count
)

from utils.dcf_utils import(
    forecast_free_cash_flows,
    discount_cash_flows,
    calculate_terminal_value,
    discount_terminal_value,
    calculate_enterprise_value,
    solve_implied_growth
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = GOLD_SCHEMA
TARGET_TABLE = GOLD_18_TABLE
TARGET_SCHEMA_TABLE = GOLD_18_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Gold INTRINSIC VALUATON (STANDARD DCF)")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    assumptions = load_table(GOLD_16_SCHEMA_TABLE,engine)

    results = []

    for _, row in assumptions.iterrows():

        cashflows = forecast_free_cash_flows(
            row["starting_fcf"],
            row["historical_growth_rate"],
            row["terminal_growth"],
            int(row["projection_years"])
        )

        discounted_cash_flow = discount_cash_flows(
            cashflows,
            row["discount_rate"]
        )

        terminal_value = calculate_terminal_value(
            cashflows[-1],
            row["terminal_growth"],
            row["discount_rate"]
        )

        discounted_terminal = discount_terminal_value(
            terminal_value,
            row["discount_rate"],
            int(row["projection_years"])
        )

        enterprise_value = calculate_enterprise_value(
            discounted_cash_flow,
            discounted_terminal
        )

        target_enterprise_value = (
            row["market_cap"]
            + row["net_debt"]
        )

        implied_growth = solve_implied_growth(
            target_enterprise_value,
            enterprise_value
        )

        results.append({
            "symbol": row["symbol"],
            "calendar_year": row["calendar_year"],
            "current_price": row["price"],
            "market_enterprise_value": target_enterprise_value,
            "historical_growth_rate": row["historical_growth_rate"],
            "implied_growth_rate": implied_growth,
            "expectation_gap": (
                implied_growth -
                row["historical_growth_rate"]),
            "valuation_status": "Completed"
        })

        reverse_dcf_df = pd.DataFrame(results).round(4)
        
        # validate_columns(reverse_dcf_df, STANDARD_DCF_INTRINSIC_VALUE_COLUMNS)
        # validate_primary_key(reverse_dcf_df,["symbol"])
        # validate_nulls(reverse_dcf_df,["symbol", "margin_of_safety"])
        # validate_row_count(reverse_dcf_df)
    
    load_dataframe_to_sql(engine, reverse_dcf_df, TARGET_SCHEMA, TARGET_TABLE)
    
    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)
        
if __name__ == "__main__":
    main()