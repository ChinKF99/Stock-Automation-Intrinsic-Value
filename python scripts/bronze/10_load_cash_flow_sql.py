"""
============================================================
10_load_cash_flow_sql.py

Purpose:
    Load cash_flow.json file into SQL Server.

Source:
    data/raw/cash_flow/.json file

Target:
    bronze.cash_flow
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
    CASH_FLOW_FOLDER,
)
 
from utils.sql_utils import (
    BRONZE_SCHEMA,
    BRONZE_10_TABLE,
    BRONZE_10_SCHEMA_TABLE,
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
TARGET_TABLE = BRONZE_10_TABLE
TARGET_SCHEMA_TABLE = BRONZE_10_SCHEMA_TABLE

# ==========================================================
# Clean Data Frame (Keep whatever column needed only)
# ==========================================================

def clean_dataframe(df):

    logger.info("Cleaning Data Frame...")

    keep_columns = [
        # General Info
        "symbol",
        "fiscalYear",
        "period",
        "reportedCurrency",

        # Data
        "netIncome",
        "depreciationAndAmortization",
        "stockBasedCompensation",
        "changeInWorkingCapital",
        "netCashProvidedByOperatingActivities",
        "capitalExpenditure",
        "freeCashFlow",
        "netCashProvidedByInvestingActivities",
        "netCashProvidedByFinancingActivities",
        "netDebtIssuance",
        "commonStockRepurchased",
        "commonDividendsPaid",
        "cashAtBeginningOfPeriod",
        "cashAtEndOfPeriod",
        "netChangeInCash",
        "incomeTaxesPaid",
        "interestPaid"
    ]

    df = df[keep_columns].copy()

    df.columns = [
        # General Info
        "symbol",
        "calendar_year",
        "period",
        "reported_currency",
    
        # Data
        "net_income",
        "depreciation",
        "stock_based_compensation",
        "change_in_working_capital",
        "operating_cash_flow",
        "capital_expenditure",
        "free_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "net_debt_issuance",
        "share_buyback",
        "dividends_paid",
        "cash_beginning",
        "cash_ending",
        "net_change_cash",
        "tax_paid",
        "interest_paid"
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
    calendar_year           SMALLINT,
    period                  VARCHAR(5),
    reported_currency       VARCHAR(10),

    --========================================================
    -- Data
    --========================================================
    net_income              BIGINT,
    depreciation            BIGINT,
    stock_based_compensation BIGINT,
    change_in_working_capital BIGINT,
    operating_cash_flow     BIGINT,
    capital_expenditure     BIGINT,
    free_cash_flow          BIGINT,
    investing_cash_flow     BIGINT,
    financing_cash_flow     BIGINT,
    net_debt_issuance       BIGINT,
    share_buyback           BIGINT,
    dividends_paid          BIGINT,
    cash_beginning          BIGINT,
    cash_ending             BIGINT,
    net_change_cash         BIGINT,
    tax_paid                BIGINT,
    interest_paid           BIGINT,

    --========================================================
    -- ETL Metadata
    --========================================================
    load_date DATE
        DEFAULT CAST(GETDATE() AS DATE),

    load_ts DATETIME2
        DEFAULT SYSDATETIME(),

    CONSTRAINT PK_cash_flow
        PRIMARY KEY(symbol,calendar_year)
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

    df = read_json_files("Cash Flow", CASH_FLOW_FOLDER)
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