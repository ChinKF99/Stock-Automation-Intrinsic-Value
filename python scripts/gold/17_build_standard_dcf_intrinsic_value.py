"""
============================================================
17_build_standard_dcf_intrinsic_value.py

Build gold table Standard DCF Intrinsic Value using data from
from gold table.

Source
------
16_build_dcf_assumptions.py

Target:
    gold.build_standard_dcf_intrinsic_value
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
    GOLD_17_TABLE,
    GOLD_17_SCHEMA_TABLE,
    STANDARD_DCF_INTRINSIC_VALUE_COLUMNS,
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
    calculate_equity_value,
    calculate_intrinsic_value,
    calculate_margin_of_safety
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = GOLD_SCHEMA
TARGET_TABLE = GOLD_17_TABLE
TARGET_SCHEMA_TABLE = GOLD_17_SCHEMA_TABLE

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

        # if row["starting_fcf"] <= 0:

        #     results.append({

        #     "symbol": row["symbol"],
        #     "calendar_year": row["calendar_year"],
        #     "current_price": row["price"],
        #     "market_enterprise_value": None,
        #     "historical_growth_rate": row["historical_growth_rate"],
        #     "implied_growth_rate": None,
        #     "valuation_status": "Negative FCF"

        # })

        # continue

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

        equity_value = calculate_equity_value(
            enterprise_value,
            row["net_debt"]
        )

        intrinsic_value = calculate_intrinsic_value(
            equity_value,
            row["weighted_average_shs_out"]
        )

        margin_of_safety = calculate_margin_of_safety(
            intrinsic_value,
            row["price"]
        )

        results.append({
            "symbol": row["symbol"],
            "calendar_year": row["calendar_year"],
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "intrinsic_value": intrinsic_value,
            "current_price": row["price"],
            "margin_of_safety": margin_of_safety
        })

    standard_dcf_df = pd.DataFrame(results).round(4)

    validate_columns(standard_dcf_df, STANDARD_DCF_INTRINSIC_VALUE_COLUMNS)
    validate_primary_key(standard_dcf_df,["symbol"])
    validate_nulls(standard_dcf_df,["symbol", "margin_of_safety"])
    validate_row_count(standard_dcf_df)

    load_dataframe_to_sql(engine, standard_dcf_df, TARGET_SCHEMA, TARGET_TABLE)
    
    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)
    
if __name__ == "__main__":
    main()