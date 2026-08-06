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
    DCF_DEFAULTS
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

    print(ratios.columns.tolist()) # For debug purposes
  
    financials = (financials.sort_values(["symbol", "calendar_year"])
                  .groupby("symbol").tail(1))

    growth = (growth.sort_values(["symbol", "calendar_year"])
              .groupby("symbol").tail(1))

    ratios = (ratios.sort_values(["symbol", "calendar_year"])
              .groupby("symbol").tail(1))

    df = financials.merge(growth, on="symbol", how="left")

    df = df.merge(ratios, on="symbol", how="left")

    df["discount_rate"] = DCF_DEFAULTS["discount_rate"]
    df["terminal_growth"] = DCF_DEFAULTS["terminal_growth"]
    df["projection_years"] = DCF_DEFAULTS["projection_years"]
    df["tax_rate"] = DCF_DEFAULTS["tax_rate"]

    df["growth_rate"] = (df[
        [
            "revenue_growth",
            "operating_income_growth",
            "free_cash_flow_growth"
        ]].mean(axis=1))

    df["starting_fcf"] = df["free_cash_flow"]

    print(df.columns.tolist()) # For debug purposes
  
#     df["starting_operating_margin"] = df["operating_margin"]
    

#     dcf_df = df[
#         [
#             "symbol",
#             "calendar_year",
#             "price",
#             "starting_fcf",
#             "growth_rate",
#             "starting_operating_margin",
#             "tax_rate",
#             "discount_rate",
#             "terminal_growth",
#             "projection_years"
#             ]
#     ]

#     validate_columns(dcf_df,DCF_ASSUMPTION_COLUMNS)
#     validate_primary_key(dcf_df,["symbol"])
#     validate_nulls(dcf_df,["symbol","starting_fcf","growth_rate","discount_rate"])
#     validate_row_count(dcf_df)

#     load_dataframe_to_sql(engine, dcf_df, TARGET_SCHEMA, TARGET_TABLE)
    
#     get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)
    
if __name__ == "__main__":
    main()