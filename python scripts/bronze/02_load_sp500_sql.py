"""
============================================================
02_load_sp500_sql.py

Purpose
-------
Load the downloaded S&P 500 ticker CSV into SQL Server.

Source
------
data/raw/sp500_tickers.csv

Target
------
bronze.sp500_tickers

"""
from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import text

# ==========================================================
# Make project root importable
# ==========================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Project imports
# ==========================================================

from config.config import (
    SP500_TICKERS_CSV_FILE_PATH,
    get_sqlalchemy_engine,
    )

from utils.csv_json_utils import(
    read_csv
    )

from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_02_TABLE,
    BRONZE_02_SCHEMA_TABLE,
    print_connection_info,
    ensure_table,
    truncate_table,
    get_row_count
    )

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

CSV_FILE = SP500_TICKERS_CSV_FILE_PATH
TARGET_SCHEMA = BRONZE_SCHEMA
TARGET_TABLE = BRONZE_02_TABLE
TARGET_SCHEMA_TABLE = BRONZE_02_SCHEMA_TABLE

# ==========================================================
# SQL Statements for ensure_table()
# ==========================================================

CREATE_SQL = f"""
CREATE TABLE {TARGET_SCHEMA_TABLE}
(
    ticker VARCHAR(20) PRIMARY KEY,

    load_date DATE
        DEFAULT CAST(GETDATE() AS DATE),

    load_ts DATETIME2
        DEFAULT SYSDATETIME()
);
"""

# ==========================================================
# Insert into SQL
# ==========================================================

def load_to_sql(engine, df, target_table):

    insert_sql = text(f"""

        INSERT INTO {target_table}
        (
            ticker
        )

        VALUES
        (
            :ticker
        )

    """)

    records = df.to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(insert_sql,records)

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("BRONZE STEP 02 - LOAD CSV INTO SQL")
    logger.info("=" * 60)
    

    try:
        engine = get_sqlalchemy_engine()
        print_connection_info(engine)

        ensure_table(
        engine=engine,
        schema=TARGET_SCHEMA,
        table=TARGET_TABLE,
        create_sql=CREATE_SQL)

        truncate_table(engine, TARGET_SCHEMA, TARGET_TABLE)

        df = read_csv(CSV_FILE)

        load_to_sql(engine, df, TARGET_SCHEMA_TABLE)

        get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

    except Exception as ex:
        logger.exception("Step 02 failed")
        logger.exception(ex)

    logger.info("=" * 60)
    logger.info(f"Finished")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()