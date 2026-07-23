"""
============================================================
06_load_income_statement_sql.py

Purpose:
    Load income_statement.json file into SQL Server.

Source:
    data/raw/income_statement/.json file

Target:
    bronze.income_statement
============================================================
"""

"""
Load Income Statement JSON files into SQL Server
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
    get_sqlalchemy_engine,
    INCOME_STATEMENT_FOLDER,
)
 
from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_06_TABLE,
    BRONZE_06_SCHEMA_TABLE,
    print_connection_info,
    ensure_table,
    truncate_table,
    get_row_count,
    bulk_insert_dataframe
)

from utils.csv_json_utils import(
    read_json_files
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = BRONZE_SCHEMA
TARGET_TABLE = BRONZE_06_TABLE
TARGET_SCHEMA_TABLE = BRONZE_06_SCHEMA_TABLE

# ==========================================================
# Clean Data Frame (Keep whatever column needed only)
# ==========================================================

def clean_dataframe(df):

    logger.info("Cleaning Data Frame...")

    keep_columns = [
        "symbol",
        "fiscalYear",
        "period",
        "reportedCurrency",

        "revenue",
        "grossProfit",
        "operatingIncome",
        "netIncome",

        "eps",
        "weightedAverageShsOut",

        "cik",
        "filingDate",
    ]

    df = df[keep_columns].copy()

    df.columns = [
        "symbol",
        "calendar_year",
        "period",
        "reported_currency",

        "revenue",
        "gross_profit",
        "operating_income",
        "net_income",

        "eps",
        "weighted_average_shs_out",

        "cik",
        "filing_date",
    ]

    return df

# ==========================================================
# SQL Statements for ensure_table()
# ==========================================================

TABLE_SQL = f"""
CREATE TABLE {TARGET_SCHEMA_TABLE}
(
    symbol VARCHAR(20),
    calendar_year INT,
    period VARCHAR(10),
    reported_currency VARCHAR(10),
    revenue BIGINT,
    gross_profit BIGINT,
    operating_income BIGINT,
    net_income BIGINT,
    eps FLOAT,
    weighted_average_shs_out BIGINT,
    cik VARCHAR(20),
    filing_date DATE,
    load_date DATE
        DEFAULT CAST(GETDATE() AS DATE),
    load_ts DATETIME2
        DEFAULT SYSDATETIME(),
    CONSTRAINT PK_income_statement
        PRIMARY KEY(symbol, calendar_year)
);
"""

# ==========================================================
# Main
# ==========================================================

def main():
    logger.info("=" * 60)
    logger.info("STEP 06 - LOAD INCOME STATEMENT INTO SQL")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    ensure_table(
        engine=engine,
        schema=TARGET_SCHEMA,
        table=TARGET_TABLE,
        create_sql=TABLE_SQL
    )

    df = read_json_files("Income Statement", INCOME_STATEMENT_FOLDER)
    df = clean_dataframe(df)

    truncate_table(engine, TARGET_SCHEMA, TARGET_TABLE)

    bulk_insert_dataframe(
        engine,
        schema=BRONZE_SCHEMA, table=TARGET_TABLE, dataframe=df
    )

    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

    logger.info("=" * 60)
    logger.info(f"Finished")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()