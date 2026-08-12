"""
============================================================
16_build_dcf_assumptions.py

Build gold table DCF Assumptions using data
from silver layer.

Source
------
13_build_company_financials
14_build_company_growth_metrics
15_build_company_financial_ratios

Target:
    gold.build_dcf_assumptions
============================================================
"""

from pathlib import Path
import sys

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
    SILVER_13_SCHEMA_TABLE,
    SILVER_14_SCHEMA_TABLE,
    SILVER_15_SCHEMA_TABLE,
    GOLD_SCHEMA,
    GOLD_16_TABLE,
    GOLD_16_SCHEMA_TABLE,
    DCF_ASSUMPTION_COLUMNS,
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
    DCF_DEFAULTS,
    calculate_revenue_growth_metrics,
    calculate_average_fcf,
    calculate_discount_rate
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = GOLD_SCHEMA
TARGET_TABLE = GOLD_16_TABLE
TARGET_SCHEMA_TABLE = GOLD_16_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Gold DCF Assumptions")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    financials = load_table(SILVER_13_SCHEMA_TABLE,engine)

    growth = load_table(SILVER_14_SCHEMA_TABLE,engine)

    ratios = load_table(SILVER_15_SCHEMA_TABLE,engine)

    # Produce a fair growth rate using CAGR Formula
    historical_growth = calculate_revenue_growth_metrics(financials).round(4)
    average_fcf = calculate_average_fcf(financials, years=3)

    financials = (financials.sort_values(["symbol", "calendar_year"])
                  .groupby("symbol").tail(1))

    growth = (growth.sort_values(["symbol", "calendar_year"])
              .groupby("symbol").tail(1))

    ratios = (ratios.sort_values(["symbol", "calendar_year"])
              .groupby("symbol").tail(1))

    df = financials.merge(growth, on=["symbol", "calendar_year"], how="left")

    df = df.merge(ratios, on=["symbol", "calendar_year"], how="left")

    df = df.merge(historical_growth,on="symbol",how="left")

    df = df.merge(average_fcf,on="symbol",how="left")

    df["discount_rate"] = (df["beta"].fillna(1).apply(calculate_discount_rate))
    df["terminal_growth"] = DCF_DEFAULTS["terminal_growth"]
    df["projection_years"] = DCF_DEFAULTS["projection_years"]
    df["tax_rate"] = DCF_DEFAULTS["tax_rate"]

    df["starting_operating_margin"] = df["operating_margin"]

    dcfa_df = df[
        [
            "symbol",
            "calendar_year",
            "price",
            "starting_fcf",
            "historical_growth_rate",
            "revenue_growth_avg",
            "earliest_revenue",
            "latest_revenue",
            "years_of_history",  
            "starting_operating_margin",
            "weighted_average_shs_out",
            "tax_rate",
            "discount_rate",
            "terminal_growth",
            "net_debt",
            "projection_years",
            ]
    ]

    validate_columns(dcfa_df,DCF_ASSUMPTION_COLUMNS)
    validate_primary_key(dcfa_df,["symbol"])
    validate_nulls(dcfa_df,DCF_ASSUMPTION_COLUMNS)
    validate_row_count(dcfa_df)

    load_dataframe_to_sql(engine, dcfa_df, TARGET_SCHEMA, TARGET_TABLE)
    
    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

    print(
    df[
        [
            "symbol",
            "starting_fcf",
            "historical_growth_rate",
            "discount_rate",
            "terminal_growth",
            "weighted_average_shs_out"
        ]
    ]
)
    
if __name__ == "__main__":
    main()