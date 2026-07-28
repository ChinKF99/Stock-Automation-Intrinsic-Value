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

from utils.csv_json_utils import (
    read_json_files
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
# Clean Data Frame (Keep whatever column needed only)
# ==========================================================

def clean_dataframe(df):

    logger.info("Cleaning dataframe...")

    keep_columns = [
        # Data
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
        # Data
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

    return df

# ==========================================================
# SQL Statements for ensure_table()
# ==========================================================

TABLE_SQL = f"""
CREATE TABLE {TARGET_SCHEMA_TABLE}
(
    --========================================================
    -- General Info & Data
    --========================================================
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

    --========================================================
    -- ETL Metadata
    --========================================================   
    load_date DATE
        DEFAULT CAST(GETDATE() AS DATE),

    load_ts DATETIME2
        DEFAULT SYSDATETIME()
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

    df = read_json_files("Company Profile", COMPANY_PROFILE_FOLDER)
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