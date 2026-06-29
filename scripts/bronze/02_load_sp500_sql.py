"""
============================================================
02_load_sp500_sql.py

Purpose
-------
Load the downloaded S&P 500 CSV into SQL Server.

Source
------
data/raw/sp500_tickers.csv

Target
------
bronze.sp500_tickers
============================================================
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
    BRONZE_SCHEMA,
    SP500_TABLE,
    FULL_SP500_TABLE,
    SP500_CSV
)

from config.config import get_sqlalchemy_engine

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# File paths
# ============================================================

CSV_FILE = SP500_CSV

TARGET_SCHEMA = BRONZE_SCHEMA
TARGET_TABLE = SP500_TABLE
FULL_TABLE = FULL_SP500_TABLE

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
# Ensure SQL objects exist
# ==========================================================

def ensure_table(engine) -> None:
    """
    Create Bronze schema/table if it doesn't already exist.
    """

    logger.info("Checking SQL schema/table...")

    sql = """
    IF NOT EXISTS
    (
        SELECT *
        FROM sys.schemas
        WHERE name='bronze'
    )
        EXEC('CREATE SCHEMA bronze');

    IF OBJECT_ID('bronze.sp500_tickers','U') IS NULL

    CREATE TABLE bronze.sp500_tickers
    (
        ticker VARCHAR(20) PRIMARY KEY,

        load_date DATE
            DEFAULT CAST(GETDATE() AS DATE),

        load_ts DATETIME2
            DEFAULT SYSDATETIME()
    );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    logger.info("Schema/table verified.")


# ==========================================================
# Load CSV into SQL
# ==========================================================

def load_sql(engine, df: pd.DataFrame) -> None:
    """
    Replace existing tickers with the latest download.
    """

    logger.info("Deleting existing rows...")

    with engine.begin() as conn:

        conn.execute(
            text(
                "DELETE FROM bronze.sp500_tickers;"
            )
        )

        logger.info("Inserting %s rows...", len(df))

        insert_sql = text("""
            INSERT INTO bronze.sp500_tickers
            (
                ticker
            )
            VALUES
            (
                :ticker
            )
        """)

        conn.execute(
            insert_sql,
            df.to_dict(orient="records")
        )

        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM bronze.sp500_tickers;"
            )
        ).scalar()

    logger.info("Rows successfully inserted : %s", count)


# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("BRONZE STEP 02 - LOAD CSV INTO SQL")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()

    logger.info("SQL connection established.")

    ensure_table(engine)

    df = read_csv()

    load_sql(engine, df)

    logger.info("Step 02 completed successfully.")


if __name__ == "__main__":
    main()