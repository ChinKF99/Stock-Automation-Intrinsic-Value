"""
============================================================
12_load_ratios_sql.py

Purpose:
    Load ratios.json file into SQL Server.

Source:
    data/raw/ratios/.json file

Target:
    bronze.ratios
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
    RATIOS_FOLDER,
)
 
from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_12_TABLE,
    BRONZE_12_SCHEMA_TABLE,
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
TARGET_TABLE = BRONZE_12_TABLE
TARGET_SCHEMA_TABLE = BRONZE_12_SCHEMA_TABLE

# ==========================================================
# Clean Data Frame (Keep whatever column needed only)
# ==========================================================

def clean_dataframe(df):

    logger.info("Cleaning Data Frame...")

    keep_columns = [
        # General Info
        "symbol",

        # Data
        "grossProfitMarginTTM",
        "operatingProfitMarginTTM",
        "netProfitMarginTTM",
        "currentRatioTTM",
        "debtToEquityRatioTTM",
        "financialLeverageRatioTTM",
        "priceToEarningsRatioTTM",
        "priceToBookRatioTTM",
        "priceToSalesRatioTTM",
        "priceToFreeCashFlowRatioTTM",
        "enterpriseValueTTM",
        "enterpriseValueMultipleTTM",
        "dividendYieldTTM",
        "dividendPayoutRatioTTM"
    ]

    df = df[keep_columns].copy()

    df.columns = [
        # General Info
        "symbol",

        # Data
        "gross_margin",
        "operating_margin",
        "net_margin",
        "current_ratio",
        "debt_to_equity",
        "financial_leverage",
        "pe_ratio",
        "pb_ratio",
        "ps_ratio",
        "pfcf_ratio",
        "enterprise_value",
        "ev_ebitda",
        "dividend_yield",
        "dividend_payout"
        ]
        
    return df

# ==========================================================
# SQL Statements for ensure_table()
# ==========================================================

TABLE_SQL = f"""
CREATE TABLE {TARGET_SCHEMA_TABLE}
(
    --========================================================
    -- General Info
    --========================================================
    symbol                  VARCHAR(20)     NOT NULL,

    --========================================================
    -- Data
    --========================================================
    gross_margin                FLOAT,
    operating_margin            FLOAT,
    net_margin                  FLOAT,
    current_ratio               FLOAT,
    debt_to_equity              FLOAT,
    financial_leverage          FLOAT,
    pe_ratio                    FLOAT,
    pb_ratio                    FLOAT,
    ps_ratio                    FLOAT,
    pfcf_ratio                  FLOAT,
    enterprise_value            BIGINT,
    ev_ebitda                   FLOAT,
    dividend_yield              FLOAT,
    dividend_payout             FLOAT,

    --========================================================
    -- ETL Metadata
    --========================================================
    load_date DATE
        DEFAULT CAST(GETDATE() AS DATE),

    load_ts DATETIME2
        DEFAULT SYSDATETIME()
);"""

# ==========================================================
# Main
# ==========================================================

def main():
    logger.info("=" * 60)
    logger.info("STEP 10 - LOAD CASH FLOW INTO SQL")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    ensure_table(
        engine=engine,
        schema=TARGET_SCHEMA,
        table=TARGET_TABLE,
        create_sql=TABLE_SQL
    )

    df = read_json_files("Cash Flow", RATIOS_FOLDER)
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