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
import json
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

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = BRONZE_SCHEMA
TARGET_TABLE = BRONZE_06_TABLE
TARGET_SCHEMA_TABLE = BRONZE_06_SCHEMA_TABLE

# ==========================================================
# Read JSON file
# ==========================================================

def read_json_files():

    logger.info("Reading income statement JSON files...")

    json_files = sorted(INCOME_STATEMENT_FOLDER.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in:\n{INCOME_STATEMENT_FOLDER}"
        )

    logger.info(f"Found {len(json_files)} JSON files.")

    rows = []

    for file in json_files:

        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                logger.warning(f"{file.name} is empty.")
                continue

            for row in data:
                rows.append(row)

        except Exception as ex:
             logger.exception(
                f"Failed reading {file.name}: {ex}"
            )
        
    df = pd.DataFrame(rows)

    logger.info(f"{len(df)} income_statement loaded into data frame.")

    return df

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

    df = read_json_files()
    df = clean_dataframe(df)

    df.to_json('output_income_statement.json')

    truncate_table(engine, TARGET_SCHEMA, TARGET_TABLE)

    bulk_insert_dataframe(
        engine,
        schema=BRONZE_SCHEMA, table=TARGET_TABLE, dataframe=df
    )

    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

    logger.info("Finished.")

if __name__ == "__main__":
    main()