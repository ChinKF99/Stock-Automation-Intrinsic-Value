"""
============================================================
08_load_balacne_sheet_sql.py

Purpose:
    Load balance_sheet.json file into SQL Server.

Source:
    data/raw/balance_sheet/.json file

Target:
    bronze.balance_sheet
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
    BALANCE_SHEET_FOLDER,
)
 
from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_08_TABLE,
    BRONZE_08_SCHEMA_TABLE,
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
TARGET_TABLE = BRONZE_08_TABLE
TARGET_SCHEMA_TABLE = BRONZE_08_SCHEMA_TABLE

# ==========================================================
# Clean Data Frame (Keep whatever column needed only)
# ==========================================================

def clean_dataframe(df):

    logger.info("Cleaning Data Frame...")

    keep_columns = [
    # General Info
    "symbol",
    "fiscalYear",

    # Data
    "cashAndCashEquivalents",
    "shortTermInvestments",
    "cashAndShortTermInvestments",
    "accountsReceivables",
    "inventory",
    "totalCurrentAssets",
    "propertyPlantEquipmentNet",
    "totalAssets",
    "accountPayables",
    "totalCurrentLiabilities",
    "shortTermDebt",
    "longTermDebt",
    "totalDebt",
    "netDebt",
    "totalLiabilities",
    "retainedEarnings",
    "totalStockholdersEquity"
    ]

    df = df[keep_columns].copy()

    df.columns = [
        # General Info
        "symbol",
        "calendar_year",
    
        # Data
        "cash_and_cash_equivalents",
        "short_term_investments",
        "cash_and_short_term_investments",
        "accounts_receivables",
        "inventory",
        "total_current_assets",
        "property_plant_equipment_net",
        "total_assets",
        "accounts_payable",
        "total_current_liabilities",
        "short_term_debt",
        "long_term_debt",
        "total_debt",
        "net_debt",
        "total_liabilities",
        "retained_earnings",
        "total_stockholders_equity"
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
    symbol                              VARCHAR(20)     NOT NULL,
    calendar_year                         SMALLINT,

    --========================================================
    -- Data
    --========================================================
    cash_and_cash_equivalents           BIGINT,
    short_term_investments              BIGINT,
    cash_and_short_term_investments     BIGINT,
    accounts_receivables                BIGINT,
    inventory                           BIGINT,
    total_current_assets                BIGINT,
    property_plant_equipment_net        BIGINT,
    total_assets                        BIGINT,
    accounts_payable                    BIGINT,
    total_current_liabilities           BIGINT,
    short_term_debt                     BIGINT,
    long_term_debt                      BIGINT,
    total_debt                          BIGINT,
    net_debt                            BIGINT,
    total_liabilities                   BIGINT,
    retained_earnings                   BIGINT,
    total_stockholders_equity           BIGINT,

    --========================================================
    -- ETL Metadata
    --========================================================
    load_date                           DATE
        DEFAULT CAST(GETDATE() AS DATE),

    load_ts                             DATETIME2
        DEFAULT SYSDATETIME(),

    CONSTRAINT PK_balance_sheet
        PRIMARY KEY(symbol, calendar_year)
);"""

# ==========================================================
# Main
# ==========================================================

def main():
    logger.info("=" * 60)
    logger.info("STEP 08 - LOAD BALANCE SHEET INTO SQL")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    ensure_table(
        engine=engine,
        schema=TARGET_SCHEMA,
        table=TARGET_TABLE,
        create_sql=TABLE_SQL
    )

    df = read_json_files("Balance Sheet", BALANCE_SHEET_FOLDER)
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