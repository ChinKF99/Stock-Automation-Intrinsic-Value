"""
============================================================
15_build_company_financial_ratios.py

Build silver table company financial ratios using data
from silver layer.

Source
------
silver.company_financials

Target:
    silver.company_financial_ratios
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
    SILVER_SCHEMA,
    SILVER_13_SCHEMA_TABLE,
    SILVER_15_TABLE,
    SILVER_15_SCHEMA_TABLE,
    print_connection_info,
    ensure_schema,
    get_row_count,
    load_dataframe_to_sql,
    load_table,
    COMPANY_FINANCIAL_RATIO_COLUMNS
)

from utils.validation_utils import(
    validate_primary_key,
    validate_columns,
    validate_nulls,
    validate_row_count
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = SILVER_SCHEMA
TARGET_TABLE = SILVER_15_TABLE
TARGET_SCHEMA_TABLE = SILVER_15_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Silver Company Financial Ratios")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    df = load_table(SILVER_13_SCHEMA_TABLE,engine)

# ==========================================================
# Calculate Historical Financial Ratios
# ==========================================================

    df["gross_margin"] = (
        df["gross_profit"] /
        df["revenue"]
    )

    df["operating_margin"] = (
        df["operating_income"] /
        df["revenue"]
    )

    df["net_margin"] = (
        df["net_income"] /
        df["revenue"]
    )

    df["fcf_margin"] = (
        df["free_cash_flow"] /
        df["revenue"]
    )

    df["operating_cash_flow_margin"] = (
        df["operating_cash_flow"] /
        df["revenue"]
    )

    df["capex_ratio"] = (
        df["capital_expenditure"] /
        df["operating_cash_flow"]
    )

    df["debt_to_equity"] = (
        df["total_debt"] /
        df["total_stockholders_equity"]
    )

    df["debt_to_assets"] = (
        df["total_debt"] /
        df["total_assets"]
    )

    df["cash_to_debt"] = (
        df["cash_and_short_term_investments"] /
        df["total_debt"]
    )

    df["asset_turnover"] = (
        df["revenue"] /
        df["total_assets"]
    )

    df["equity_ratio"] = (
        df["total_stockholders_equity"] /
        df["total_assets"]
    )

    df = df[
        [
            "symbol",
            "calendar_year",
            "gross_margin",
            "operating_margin",
            "net_margin",
            "fcf_margin",
            "operating_cash_flow_margin",
            "capex_ratio",
            "debt_to_equity",
            "debt_to_assets",
            "cash_to_debt",
            "asset_turnover",
            "equity_ratio",
        ]
    ]

    df = df.round(4) # Round to 4 decimal points for less noise

    validate_columns(df,COMPANY_FINANCIAL_RATIO_COLUMNS)
    validate_primary_key(df,["symbol", "calendar_year"])
    validate_nulls(df,["symbol", "calendar_year"])
    validate_row_count(df)

    load_dataframe_to_sql(engine, df, TARGET_SCHEMA, TARGET_TABLE)

    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

if __name__ == "__main__":
    main()

