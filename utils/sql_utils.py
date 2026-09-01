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
# SQL Schema & Tables
# ==========================================================

# Schemas
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# Bronze Tables
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
BRONZE_12_TABLE = 'ratios_ttm'
BRONZE_12_SCHEMA_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_12_TABLE}"

# Silver Tables
SILVER_13_TABLE = 'company_financials'
SILVER_13_SCHEMA_TABLE = f"{SILVER_SCHEMA}.{SILVER_13_TABLE}"
SILVER_14_TABLE = 'company_growth_metrics'
SILVER_14_SCHEMA_TABLE = f"{SILVER_SCHEMA}.{SILVER_14_TABLE}"
SILVER_15_TABLE = 'company_financial_ratios'
SILVER_15_SCHEMA_TABLE = f"{SILVER_SCHEMA}.{SILVER_15_TABLE}"

# Gold Tables
GOLD_16_TABLE = 'build_dcf_assumptions'
GOLD_16_SCHEMA_TABLE = f"{GOLD_SCHEMA}.{GOLD_16_TABLE}"
GOLD_17_TABLE = 'build_standard_dcf'
GOLD_17_SCHEMA_TABLE = f"{GOLD_SCHEMA}.{GOLD_17_TABLE}"
GOLD_18_TABLE = 'build_reverse_dcf'
GOLD_18_SCHEMA_TABLE = f"{GOLD_SCHEMA}.{GOLD_17_TABLE}"

# *****************************************************************************
# UNIVERSAL SQL SCRIPTS
# *****************************************************************************

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
# Ensure Schema
# ==========================================================
def ensure_schema(
    engine,
    schema: str,
) -> None:
    """
    engine : SQLAlchemy Engine

    schema : str
        Schema name.
        Example:
            bronze

    table : str
        Table name only.
        Example:
            sp500_tickers
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
        """

    with engine.begin() as conn:
        conn.execute(text(sql))

    logger.info("Verified Schema %s", schema)

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
# Load SQL Table
# ==========================================================

def load_table(schema_table, engine):
    query = f"""
    SELECT *
    FROM {schema_table}
    """
    return pd.read_sql(query, engine)

# ==========================================================
# Select only the required columns from a DataFrame.
# ==========================================================

def select_columns(df, columns, table_name):
    """
    Raises:
        KeyError: If one or more requested columns do not exist.
    """

    missing_columns = set(columns) - set(df.columns)

    if missing_columns:
        raise KeyError(
            f"{table_name} is missing columns: {sorted(missing_columns)}"
        )

    return df[columns].copy()

# ==========================================================
# Append DataFrame into existing created SQL Table
# ==========================================================

def bulk_append_dataframe(
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


# *****************************************************************************
# BRONZE LAYER SQL SCRIPTS
# *****************************************************************************

# ==========================================================
# Create Table from scratch with known Schemas & Columns
# ==========================================================

def ensure_table(engine, schema, table, create_sql):
    """    

    engine : SQLAlchemy Engine

    schema : str
        Schema name.
        Example:
            bronze

    table : str
    Table name only.
    Example:
        sp500_tickers

    create_sql : str
    CREATE TABLE statement only.

    Example:

    CREATE TABLE bronze.sp500_tickers
    (
        ...
    );"""

    sql = f"""
        IF OBJECT_ID('{schema}.{table}','U') IS NULL
        BEGIN
            {create_sql}
        END;
        """
    
    with engine.begin() as conn:
        conn.execute(text(sql))

    logger.info("Verified Schema Table %s.%s", schema, table)

# *****************************************************************************
# SILVER LAYER SQL SCRIPTS
# *****************************************************************************

# ==========================================================
# Check if the table exists (For Silver & Gold Layer)
# ==========================================================

def table_exists(engine, schema, table):

    sql = text("""
        SELECT 1
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = :schema
          AND TABLE_NAME = :table
    """)

    with engine.begin() as conn:

        result = conn.execute(
            sql,
            {
                "schema": schema,
                "table": table
            }
        )

        return result.first() is not None

# ==========================================================
# Append dataframe after checking if table existed
# ==========================================================

def load_dataframe_to_sql(
    engine,
    dataframe,
    schema,
    table
):
    """
    To check if table with data already existed
    This is to avoid double entry of data.
    """
    if table_exists(engine, schema, table):
        truncate_table(engine, schema, table)
        bulk_append_dataframe(engine, dataframe, schema, table)

    else:
        dataframe.to_sql(
        name=table,
        schema=schema,
        con=engine,
        if_exists="fail",
        index=False,
        method="multi",
        chunksize=1000
        )

# ==========================================================
# Bronze input columns for Step13
# ==========================================================

PROFILE_COLUMNS = [
    "symbol",
    "company_name",
    "exchange",
    "sector",
    "industry",
    "country",
    "currency",
    "market_cap",
    "price",
    "beta"
]

INCOME_COLUMNS = [
    "symbol",
    "calendar_year",
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "eps",
    "weighted_average_shs_out"
]

BALANCE_COLUMNS = [
    "symbol",
    "calendar_year",
    "cash_and_short_term_investments",
    "total_assets",
    "total_debt",
    "net_debt",
    "total_stockholders_equity",
]

CASHFLOW_COLUMNS = [
    "symbol",
    "calendar_year",
    "operating_cash_flow",
    "capital_expenditure",
    "free_cash_flow",
]

RATIO_TTM_COLUMNS = [
    "symbol",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "current_ratio",
    "debt_to_equity",
    "pe_ratio",
    "pb_ratio",
]

# ==========================================================
# Silver output Columns
# ==========================================================

# step13_company_financials Columns
COMPANY_FINANCIAL_COLUMNS = [
    #Primary Key Column (Use for merge)
    "symbol",
    "calendar_year",
    # Company Profile Column
    "company_name",
    "exchange",
    "sector",
    "industry",
    "country",
    "currency",
    "market_cap",
    "price",
    "beta",
    # Income Statement Column
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "eps",
    "weighted_average_shs_out",
    # Balance Statement Column
    "cash_and_short_term_investments",
    "total_assets",
    "total_debt",
    "net_debt",
    "total_stockholders_equity",
    # Cashflow Column
    "operating_cash_flow",
    "capital_expenditure",
    "free_cash_flow",
]

# step14_company_growth_metrics Columns
COMPANY_GROWTH_METRICS_COLUMNS =[
    "symbol",
    "calendar_year",
    "revenue_growth",
    "gross_profit_growth",
    "operating_income_growth",
    "net_income_growth",
    "eps_growth",
    "operating_cash_flow_growth",
    "free_cash_flow_growth",
    "equity_growth",
    "debt_growth"
]

# step15_company_financial_ratios Columns
COMPANY_FINANCIAL_RATIO_COLUMNS = [
    "symbol",
    "calendar_year",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "fcf_margin",
    "operating_cash_flow_margin",
    "capex_ratio",
    "debt_to_equity",
    "debt_to_assets",
    "cash_to_debt",
    "asset_turnover",
    "equity_ratio",
]

# ==========================================================
# Gold output Columns
# ==========================================================

DCF_ASSUMPTION_COLUMNS = [
    "symbol",
    "calendar_year",
    "price",
    "starting_fcf",
    "historical_growth_rate",
    "revenue_growth_avg",
    "earliest_revenue",
    "latest_revenue",
    "years_of_history",  
    "starting_operating_margin",
    "weighted_average_shs_out",
    "tax_rate",
    "discount_rate",
    "terminal_growth",
    "net_debt",
    "projection_years",
    "market_cap"
]

STANDARD_DCF_INTRINSIC_VALUE_COLUMNS = [
    "symbol",
    "calendar_year",
    "calculated_ev",
    "equity_value",
    "intrinsic_value",
    "current_price",
    "margin_of_safety",
    "valuation_status"
]

REVERSE_DCF_INTRINSIC_VALUE_COLUMNS = [
    "symbol",
    "calendar_year",
    "current_price",
    "market_ev",
    "calculated_ev",
    "historical_growth_rate",
    "implied_growth_rate",
    "growth_premium",
    "iterations",
    "difference",
    "converged",
    "valuation_status"
]