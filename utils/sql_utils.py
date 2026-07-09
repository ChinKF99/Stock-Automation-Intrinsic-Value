"""
============================================================
SQL Utility Functions

Common SQL Server helper functions used throughout
the Bronze, Silver and Gold ETL pipelines.

============================================================
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine
from config.logging_config import setup_logger
logger = setup_logger(__name__)


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
BRONZE_02_TABLE = "sp500_tickers"
BRONZE_02_TARGET_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_02_TABLE}"
BRONZE_04_TABLE = "company_profile"
BRONZE_04_TARGET_TABLE = f"{BRONZE_SCHEMA}.{BRONZE_04_TABLE}"

# ==========================================================
# Ensure Table
# ==========================================================

def ensure_table(engine, schema, table):
    """
    Create bronze.sp500_tickers if it does not exist.
    """

    sql = text(f"""

    IF NOT EXISTS
    (
        SELECT *
        FROM sys.schemas
        WHERE name= '{schema}'
    )
        EXEC('CREATE SCHEMA {schema}');

    IF OBJECT_ID('{table}','U') IS NULL

    CREATE TABLE {table}
    (
        ticker VARCHAR(20)
            PRIMARY KEY,

        load_date DATE
            DEFAULT CAST(GETDATE() AS DATE),

        load_ts DATETIME2
            DEFAULT SYSDATETIME()
    );

    """)

    with engine.begin() as conn:
        conn.execute(sql)

    logger.info(f"Verified table {table}")

# ==========================================================
# Get Row Count
# ==========================================================

def get_row_count(
    engine: Engine,
    table: str
) -> int:
    """
    Return row count of a SQL table.
    """

    sql = text(f"""
        SELECT COUNT(*)
        FROM {table}
    """)

    with engine.begin() as conn:
        count = conn.execute(sql).scalar()
    
    logger.info(f"{count} rows inserted")

# ==========================================================
# Delete Existing Rows
# ==========================================================

def delete_all_rows(
    engine: Engine,
    table
) -> None:
    """
    Delete all rows from a table.
    """

    logger.info(f"Deleting existing rows from {table}")

    sql = text(f"DELETE FROM {table}")

    with engine.begin() as conn:
        conn.execute(sql)

    logger.info("Delete completed.")

# ==========================================================
# Execute SQL
# ==========================================================

def execute_sql(
    engine: Engine,
    sql: str,
    records
) -> None:
    """
    Execute a SQL statement.
    """

    with engine.begin() as conn:
        conn.execute(sql,records)

    logger.info("SQL executed successfully.")

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
        f"Inserting {len(dataframe)} rows into {schema}.{table}"
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