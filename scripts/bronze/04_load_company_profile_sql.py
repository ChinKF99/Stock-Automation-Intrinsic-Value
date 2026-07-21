"""
============================================================
04_load_company_profile_sql.py

Purpose:
    Load company_profile.csv into SQL Server.

Source:
    data/raw/company_profile/.json file

Target:
    bronze.company_profile
============================================================
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
    COMPANY_PROFILE_FOLDER,
)

from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_04_TABLE,
    BRONZE_04_SCHEMA_TABLE,
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
TARGET_TABLE = BRONZE_04_TABLE
TARGET_SCHEMA_TABLE = BRONZE_04_SCHEMA_TABLE

# ==========================================================
# Read JSON file
# ==========================================================

def read_json_files() -> pd.DataFrame:
   
    # Read all company profile JSON files and return a single DataFrame.
    
    logger.info("Reading company profile JSON files...")

    json_files = sorted(COMPANY_PROFILE_FOLDER.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in:\n{COMPANY_PROFILE_FOLDER}"
        )

    logger.info(f"Found {len(json_files)} JSON files.")

    rows = []

    for file in json_files:

        try:

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                logger.warning(f"{file.name} is empty.")
                continue

            if isinstance(data, dict):
                rows.append(data)

        except Exception as ex:
            logger.exception(
                f"Failed reading {file.name}: {ex}"
            )

    df = pd.DataFrame(rows)

    logger.info(f"{len(df)} company profiles loaded into data frame.")

    return df

# ==========================================================
# Clean Data Frame (Keep whatever column needed only)
# ==========================================================

def clean_dataframe(df):

    logger.info("Cleaning dataframe...")

    keep_columns = [
        "symbol",
        "companyName",
        "exchange",
        "sector",
        "industry",
        "country",
        "currency",
        "marketCap",
        "isActivelyTrading",
        "price",
        "beta",
        "lastDividend",
        "ceo",
        "ipoDate"
    ]

    df = df[keep_columns].copy()
    
    df.columns = [
        "symbol",
        "company_name",
        "exchange",
        "sector",
        "industry",
        "country",
        "currency",
        "market_cap",
        "is_actively_trading",
        "price",
        "beta",
        "last_dividend",
        "ceo",
        "ipo_date"
    ]

    # # Convert IPO Date
    # if "ipo_date" in df.columns:
    #     df["ipo_date"] = pd.to_datetime(df["ipo_date"], errors="coerce").dt.date

    # # Convert Active flag
    # if "is_actively_trading" in df.columns:
    #     df["is_actively_trading"] = (
    #         df["is_actively_trading"].fillna(False).astype(bool)
    #     )

    return df

# ==========================================================
# SQL Statements for ensure_table()
# ==========================================================

TABLE_SQL = f"""
CREATE TABLE {TARGET_SCHEMA_TABLE}
(
    symbol              VARCHAR(20)     NOT NULL PRIMARY KEY,
    company_name        VARCHAR(255),
    exchange            VARCHAR(50),
    sector              VARCHAR(100),
    industry            VARCHAR(150),
    country             VARCHAR(100),
    currency            VARCHAR(20),
    market_cap          BIGINT,
    is_actively_trading BIT,
    price               INT,
    beta                FLOAT,
    last_dividend       FLOAT,
    ceo                 VARCHAR(100),
    ipo_date            DATE,
    load_date           DATE DEFAULT CAST(GETDATE() AS DATE),
    load_ts             DATETIME2 DEFAULT SYSDATETIME()
);
"""

# ==========================================================
# Main
# ==========================================================

def main():
    logger.info("=" * 60)
    logger.info("STEP 04 - LOAD COMPANY PROFILE INTO SQL")
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

    df.to_json('output_company_profile.json')

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