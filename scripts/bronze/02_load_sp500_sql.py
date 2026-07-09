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
    SP500_CSV,
    get_sqlalchemy_engine,
)

from config.logging_config import setup_logger

from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_02_TARGET_TABLE,
    print_connection_info,
    ensure_table,
    delete_all_rows,
    get_row_count,
    execute_sql
)

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

CSV_FILE = SP500_CSV
TARGET_SCHEMA = BRONZE_SCHEMA
TARGET_TABLE = BRONZE_02_TARGET_TABLE

# ==========================================================
# Read CSV
# ==========================================================

def read_csv():

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found:\n{CSV_FILE}"
        )

    logger.info("Reading CSV...")

    df = pd.read_csv(CSV_FILE)

    logger.info(f"{len(df)} rows loaded from CSV.")

    return df

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

    execute_sql(engine,insert_sql,records)

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("BRONZE STEP 02 - LOAD CSV INTO SQL")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    ensure_table(engine, TARGET_SCHEMA, TARGET_TABLE)

    delete_all_rows(engine, TARGET_TABLE)

    df = read_csv()

    load_to_sql(engine, df, TARGET_TABLE)

    get_row_count(engine, TARGET_TABLE)

    logger.info("Step 02 completed successfully.")

if __name__ == "__main__":
    main()