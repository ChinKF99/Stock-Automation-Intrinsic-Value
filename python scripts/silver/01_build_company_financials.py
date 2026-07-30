"""
============================================================
01_build_company_financials

Build silver layer for company financials by merging various
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
from sqlalchemy import text

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
    SILVER_01_TABLE,
    SILVER_01_SCHEMA_TABLE,
    BRONZE_04_SCHEMA_TABLE,
    BRONZE_06_SCHEMA_TABLE,
    BRONZE_08_SCHEMA_TABLE,
    BRONZE_10_SCHEMA_TABLE,
    BRONZE_12_SCHEMA_TABLE,
    print_connection_info,
    ensure_table,
    truncate_table,
    get_row_count,
    bulk_insert_dataframe,
    load_table
)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = SILVER_SCHEMA
TARGET_TABLE = SILVER_01_TABLE
TARGET_SCHEMA_TABLE = SILVER_01_SCHEMA_TABLE
company_profile = BRONZE_04_SCHEMA_TABLE
income_statement = BRONZE_06_SCHEMA_TABLE
balance_sheet = BRONZE_08_SCHEMA_TABLE
cash_flow = BRONZE_10_SCHEMA_TABLE
financial_ratios = BRONZE_12_SCHEMA_TABLE

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)


def load_to_silver_01(target_schema, target_table, target_schema_table,engine,df):
    with engine.begin() as conn:
        conn.execute(text(f"""
        IF NOT EXISTS (
            SELECT *
            FROM sys.schemas
            WHERE name={target_schema}
        )
        EXEC('CREATE SCHEMA {target_schema}')
        """))

        conn.execute(text(f"""
        IF OBJECT_ID({target_schema_table},'U') IS NOT NULL
            DROP TABLE {target_schema_table}
        """))

    df.to_sql(
        target_table,
        engine,
        schema= target_schema,
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi"
    )

    logger.info("Silver table created successfully.")


def main():

    logger.info("=" * 60)
    logger.info("Building Silver Company Financials")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info

    profile = load_table(company_profile,engine)
    income = load_table(income_statement,engine)
    balance = load_table(balance_sheet,engine)
    cashflow = load_table(cash_flow,engine)
    ratios = load_table(financial_ratios,engine)

    logger.info("Merging Profile...")

    df = profile.merge(
        income,
        on=["symbol", "calendar_year"],
        how="left"
    )

    logger.info("Merging Balance Sheet...")
    df = df.merge(
        balance,
        on=["symbol", "calendar_year"],
        how="left"
    )

    logger.info("Merging Cash Flow...")
    df = df.merge(
        cashflow,
        on=["symbol", "calendar_year"],
        how="left"
    )

    logger.info("Merging Ratios...")
    df = df.merge(
        ratios,
        on="symbol",
        how="left"
    )

    logger.info(f"Rows: {len(df)}")

    load_to_silver_01(TARGET_SCHEMA, TARGET_TABLE, TARGET_SCHEMA_TABLE, engine, df)

    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

if __name__ == "__main__":
    main()