"""
============================================================
SQL Utility Functions

Common SQL Server helper functions used throughout
the Bronze, Silver and Gold ETL pipelines.

============================================================
"""

import os
import sys
from sqlalchemy import text
from sqlalchemy.engine import Engine
import pandas as pd
from config.logging_config import setup_logger

# 1. Get the base name (e.g., "script.py")
raw_name = os.path.basename(sys.argv[0])

# 2. Separate name from extension and add .log (e.g., "script.log")
log_name = os.path.splitext(raw_name)[0]

# 3. Initialize the logger
logger = setup_logger(log_name)

# ==========================================================
# Connection Information
# ==========================================================

def print_connection_info(engine: Engine) -> None:
    """
    Print SQL Server connection information.
    Useful for confirming which database the script is writing to.
    """

    sql = """
    SELECT
        @@SERVERNAME AS server_name,
        DB_NAME() AS database_name,
        SUSER_SNAME() AS login_name;
    """

    with engine.begin() as conn:
        row = conn.execute(text(sql)).fetchone()

    logger.info("Connected SQL Server")
    logger.info(f"Server   : {row.server_name}")
    logger.info(f"Database : {row.database_name}")
    logger.info(f"Login    : {row.login_name}")

# ==========================================================
# SQL Scheme & Tables
# ==========================================================

#Bronze table for bronze.sp500_tickers
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
BRONZE_02_TABLE = "sp500_tickers"
BRONZE_02_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_02_TABLE}"
BRONZE_04_TABLE = "company_profile"
BRONZE_04_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_04_TABLE}"
BRONZE_06_TABLE = 'income_statement'
BRONZE_06_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_06_TABLE}"
BRONZE_08_TABLE = 'balance_sheet'
BRONZE_08_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_08_TABLE}"
BRONZE_10_TABLE = 'cash_flow'
BRONZE_10_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_10_TABLE}"
BRONZE_12_TABLE = 'ratios'
BRONZE_12_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_12_TABLE}"
SILVER_01_TABLE = 'company_financials'
SILVER_01_SCHEMA_TABLE = f"{SILVER_SCHEMA}.{SILVER_01_TABLE}"

# ==========================================================
# Ensure Schema & Table Exists
# ==========================================================
def ensure_table(
    engine,
    schema: str,
    table: str,
    create_sql: str
) -> None:
    """
    Ensure a schema and table exist.

    Parameters
    ----------
    engine : SQLAlchemy Engine

    schema : str
        Schema name.
        Example:
            bronze

    table_name : str
        Table name only.
        Example:
            sp500_tickers

    create_sql : str
        CREATE TABLE statement only.

        Example:

        CREATE TABLE bronze.sp500_tickers
        (
            ...
        );
    """

    sql = f"""
    IF NOT EXISTS
    (
        SELECT 1
        FROM sys.schemas
        WHERE name = '{schema}'
    )
    BEGIN
        EXEC('CREATE SCHEMA {schema}');
    END;

    IF OBJECT_ID('{schema}.{table}','U') IS NULL
    BEGIN
        {create_sql}
    END;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    logger.info("Verified table %s.%s", schema, table)

# ==========================================================
# Get Row Count
# ==========================================================

def get_row_count(engine, schema: str, table_name: str) -> int:

    sql = text(
        f"SELECT COUNT(*) FROM {schema}.{table_name}"
    )

    with engine.begin() as conn:
        count = conn.execute(sql).scalar()
    
    logger.info(f"Total {count} rows inserted")


# ==========================================================
# Truncate Table
# ==========================================================

def truncate_table(engine, schema: str, table_name: str) -> None:
    """
    Delete all rows from a table.
    """

    sql = text(f"DELETE FROM {schema}.{table_name}")

    with engine.begin() as conn:
        conn.execute(sql)

    logger.info("Table truncated %s.%s", schema, table_name)

# ==========================================================
# Get ticker from SQL
# ==========================================================

def get_sp500_tickers(scheme_table, engine):

    logger.info("Reading tickers from SQL Server...")

    sql = f"""
        SELECT ticker
        FROM {scheme_table}
        ORDER BY ticker
    """

    df = pd.read_sql(sql, engine)

    logger.info(f"{len(df)} tickers loaded.")

    return df["ticker"].tolist()

# ==========================================================
# Bulk Insert DataFrame
# ==========================================================

def bulk_insert_dataframe(
    engine: Engine,
    dataframe,
    schema: str,
    table: str
) -> None:
    """
    Bulk insert a pandas DataFrame into SQL Server.
    """

    logger.info(
        f"Inserting dataframe data into {schema}.{table}"
    )

    dataframe.to_sql(
        name=table,
        schema=schema,
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

    logger.info("Insert completed.")

# ==========================================================
# Load SQL Table
# ==========================================================

def load_table(schema_table, engine):
    query = f"""
    SELECT *
    FROM {schema_table}
    """
    return pd.read_sql(query, engine)