"""
============================================================
14_build_company_growth_metrics.py

Build silver table company growth metrics using data
from silver layer.

Source
------
silver.company_financials

Target:
    silver.company_growth_metrics
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
    SILVER_14_TABLE,
    SILVER_14_SCHEMA_TABLE,
    print_connection_info,
    ensure_schema,
    get_row_count,
    load_dataframe_to_sql,
    load_table,
    COMPANY_GROWTH_METRICS_COLUMNS
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
TARGET_TABLE = SILVER_14_TABLE
TARGET_SCHEMA_TABLE = SILVER_14_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Silver Company Growth Metrics")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    df = load_table(SILVER_13_SCHEMA_TABLE,engine)

    df = df.sort_values(["symbol","calendar_year"])

    df["revenue_growth"] = (
        df.groupby("symbol")["revenue"].pct_change())

    df["gross_profit_growth"] = (
        df.groupby("symbol")["gross_profit"].pct_change())

    df["operating_income_growth"] = (
        df.groupby("symbol")["operating_income"].pct_change())

    df["net_income_growth"] = (
        df.groupby("symbol")["net_income"].pct_change())

    df["eps_growth"] = (
        df.groupby("symbol")["eps"].pct_change())

    df["free_cash_flow_growth"] = (
        df.groupby("symbol")["free_cash_flow"].pct_change())

    df["operating_cash_flow_growth"] = (
        df.groupby("symbol")["operating_cash_flow"].pct_change())

    df["equity_growth"] = (
        df.groupby("symbol")["total_stockholders_equity"].pct_change())

    df["debt_growth"] = (
        df.groupby("symbol")["total_debt"].pct_change())

    growth_df = df[
        [
            "symbol",
            "calendar_year",
            "revenue_growth",
            "gross_profit_growth",
            "operating_income_growth",
            "net_income_growth",
            "eps_growth",
            "operating_cash_flow_growth",
            "free_cash_flow_growth",
            "equity_growth",
            "debt_growth"
        ]
    ]

    growth_df = growth_df.round(4)

    validate_columns(growth_df,COMPANY_GROWTH_METRICS_COLUMNS)
    validate_primary_key(growth_df,["symbol","calendar_year"])
    validate_row_count(growth_df)
    # All columns for year 2021 will be null, due to no 2020 year to compare.
    validate_nulls(growth_df,["symbol","calendar_year"]) 

    load_dataframe_to_sql(engine, growth_df, TARGET_SCHEMA, TARGET_TABLE)

    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

if __name__ == "__main__":
    main()