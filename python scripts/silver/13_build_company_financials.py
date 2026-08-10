"""
============================================================
13_build_company_financials

Build silver layer for company financials by merging
bronze table data.

Source
------
All bronze tables.

Target:
    silver.company_financials
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
    SILVER_13_TABLE,
    SILVER_13_SCHEMA_TABLE,
    BRONZE_04_SCHEMA_TABLE,
    BRONZE_06_SCHEMA_TABLE,
    BRONZE_08_SCHEMA_TABLE,
    BRONZE_10_SCHEMA_TABLE,
    BRONZE_12_SCHEMA_TABLE,
    print_connection_info,
    ensure_schema,
    get_row_count,
    load_dataframe_to_sql,
    load_table,
    select_columns,
    PROFILE_COLUMNS,
    INCOME_COLUMNS,
    BALANCE_COLUMNS,
    CASHFLOW_COLUMNS,
    RATIO_TTM_COLUMNS,
    COMPANY_FINANCIAL_COLUMNS
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
TARGET_TABLE = SILVER_13_TABLE
TARGET_SCHEMA_TABLE = SILVER_13_SCHEMA_TABLE
company_profile = BRONZE_04_SCHEMA_TABLE
income_statement = BRONZE_06_SCHEMA_TABLE
balance_sheet = BRONZE_08_SCHEMA_TABLE
cash_flow = BRONZE_10_SCHEMA_TABLE
ratios_ttm = BRONZE_12_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Silver Company Financials")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    profile = load_table(company_profile,engine)
    income = load_table(income_statement,engine)
    balance = load_table(balance_sheet,engine)
    cashflow = load_table(cash_flow,engine)
    ratiosttm = load_table(ratios_ttm,engine)

    logger.info("Merging Profile...")

    profile = select_columns(profile, PROFILE_COLUMNS, "company_profile")
    income = select_columns(income, INCOME_COLUMNS, "income_statement")
    balance = select_columns(balance, BALANCE_COLUMNS, "balance_sheet")
    cashflow = select_columns(cashflow, CASHFLOW_COLUMNS, "cash_flow")
    ratiosttm = select_columns(ratiosttm, RATIO_TTM_COLUMNS, "financial_ratios")

    df = income.merge(
        balance,
        on=["symbol", "calendar_year"],
        how="left"
    )

    df = df.merge(
        cashflow,
        on=["symbol", "calendar_year"],
        how="left"
    )

    df = df.merge(
        profile,
        on="symbol",
        how="left"
    )

    validate_columns(df,COMPANY_FINANCIAL_COLUMNS)
    validate_primary_key(df,["symbol","calendar_year"])
    validate_nulls(df,["symbol","calendar_year","revenue","net_income"])
    validate_row_count(df)

    load_dataframe_to_sql(engine, df, TARGET_SCHEMA, TARGET_TABLE)

    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

if __name__ == "__main__":
    main()