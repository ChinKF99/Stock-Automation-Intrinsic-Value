"""
============================================================
02_load_sp500_sql.py

Purpose:
    Load the downloaded S&P 500 CSV into SQL Server.

Source:
    data/raw/sp500_tickers.csv

Target:
    bronze.sp500_tickers
============================================================
"""

from pathlib import Path
import sys
from datetime import datetime

import pandas as pd
from sqlalchemy import text

# ============================================================
# Make project root importable
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# Project imports
# ============================================================

from config.config import get_sqlalchemy_engine


# ============================================================
# File paths
# ============================================================

CSV_FILE = PROJECT_ROOT / "data" / "raw" / "sp500_tickers.csv"

TARGET_SCHEMA = "bronze"
TARGET_TABLE = "sp500_tickers"

FULL_TABLE = f"{TARGET_SCHEMA}.{TARGET_TABLE}"


# ============================================================
# Logging
# ============================================================

def log(message: str):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}] {message}")


# ============================================================
# Read CSV
# ============================================================

def read_csv():

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found:\n{CSV_FILE}"
        )

    log("Reading CSV...")

    df = pd.read_csv(CSV_FILE)

    log(f"{len(df)} rows loaded from CSV.")

    return df


# ============================================================
# Ensure SQL table exists
# ============================================================

def ensure_table(engine):

    sql = """
    IF NOT EXISTS (
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

    log("SQL table verified.")


# ============================================================
# Load into SQL
# ============================================================

def load_sql(engine, df):

    log("Deleting existing rows...")

    with engine.begin() as conn:

        conn.execute(
            text(
                "DELETE FROM bronze.sp500_tickers"
            )
        )

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
            df.to_dict("records")
        )

        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM bronze.sp500_tickers"
            )
        ).scalar()

    log(f"{count} rows inserted.")


# ============================================================
# Main
# ============================================================

def main():

    log("=" * 60)
    log("STEP 02 - LOAD CSV INTO SQL")
    log("=" * 60)

    engine = get_sqlalchemy_engine()

    ensure_table(engine)

    df = read_csv()

    load_sql(engine, df)

    log("Finished.")


if __name__ == "__main__":
    main()