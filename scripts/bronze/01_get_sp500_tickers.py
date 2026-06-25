from pathlib import Path
import sys
from datetime import datetime

import pandas as pd
import requests
from sqlalchemy import text
from sqlalchemy.engine import Engine

# ============================================================
# Make project root importable
# Allows: from config.config import get_sqlalchemy_engine
# ============================================================
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import get_sqlalchemy_engine  # noqa: E402


# ============================================================
# Constants
# ============================================================
WIKIPEDIA_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
TARGET_SCHEMA = "bronze"
TARGET_TABLE = "sp500_tickers"
FULL_TABLE_NAME = f"{TARGET_SCHEMA}.{TARGET_TABLE}"
SOURCE_NAME = "Wikipedia"


# ============================================================
# Logging helper
# ============================================================
def log(message: str) -> None:
    """Print a timestamped log message."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


# ============================================================
# Extraction
# ============================================================
def fetch_sp500_from_wikipedia() -> pd.DataFrame:
    """
    Download the S&P 500 constituent list from Wikipedia.

    Returns a raw DataFrame containing at least:
        - Symbol
        - Security
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        )
    }

    log("Requesting S&P 500 constituents page from Wikipedia...")
    response = requests.get(WIKIPEDIA_SP500_URL, headers=headers, timeout=30)
    response.raise_for_status()

    tables = pd.read_html(response.text)

    if not tables:
        raise ValueError("No HTML tables found on Wikipedia page.")

    # On this page, the first table is the constituent list
    df = tables[0]

    log(f"Wikipedia table downloaded successfully. Rows found: {len(df)}")
    log(f"Columns found: {df.columns.tolist()}")

    required_columns = {"Symbol", "Security"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Wikipedia table structure changed. Missing columns: {missing_columns}"
        )

    return df


# ============================================================
# Transformation
# ============================================================
def transform_sp500_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw Wikipedia S&P 500 data into the Bronze table structure.

    Final output columns:
        ticker
        company_name
        source
    """
    df = raw_df.rename(
        columns={
            "Symbol": "ticker",
            "Security": "company_name"
        }
    )[["ticker", "company_name"]].copy()

    # Clean ticker
    # Wikipedia may use BRK.B / BF.B
    # FMP typically expects BRK-B / BF-B
    df["ticker"] = (
        df["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "-", regex=False)
    )

    # Clean company name
    df["company_name"] = (
        df["company_name"]
        .astype(str)
        .str.strip()
    )

    # Add source
    df["source"] = SOURCE_NAME

    # Remove duplicates by ticker
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["ticker"]).reset_index(drop=True)
    after_dedup = len(df)

    if before_dedup != after_dedup:
        log(f"Removed {before_dedup - after_dedup} duplicate ticker rows.")

    # Final validation
    if df.empty:
        raise ValueError("Transformed S&P 500 DataFrame is empty.")

    if df["ticker"].isna().any():
        raise ValueError("Null ticker values found after transformation.")

    if df["ticker"].duplicated().any():
        duplicates = df[df["ticker"].duplicated(keep=False)]["ticker"].tolist()
        raise ValueError(f"Duplicate tickers still exist after cleanup: {duplicates}")

    log(f"Transformed S&P 500 dataset ready. Final row count: {len(df)}")
    return df


# ============================================================
# SQL connection / diagnostics
# ============================================================
def print_sql_connection_info(engine: Engine) -> None:
    """
    Print SQL Server connection details to confirm where Python is writing.
    """
    sql = """
    SELECT
        @@SERVERNAME AS server_name,
        DB_NAME() AS database_name,
        SUSER_SNAME() AS login_name;
    """

    with engine.begin() as conn:
        row = conn.execute(text(sql)).fetchone()

    log("Connected SQL Server info:")
    log(f"  Server   : {row.server_name}")
    log(f"  Database : {row.database_name}")
    log(f"  Login    : {row.login_name}")


def inspect_target_table(engine: Engine) -> None:
    """
    Print the target SQL table structure for validation.
    """
    sql = f"""
    SELECT
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{TARGET_SCHEMA}'
      AND TABLE_NAME = '{TARGET_TABLE}'
    ORDER BY ORDINAL_POSITION;
    """

    with engine.begin() as conn:
        rows = conn.execute(text(sql)).fetchall()

    log(f"Current SQL table structure for {FULL_TABLE_NAME}:")
    if not rows:
        log("  Table does not exist yet.")
        return

    for row in rows:
        log(f"  {row.COLUMN_NAME} | {row.DATA_TYPE} | nullable={row.IS_NULLABLE}")


# ============================================================
# SQL DDL
# ============================================================
def ensure_bronze_schema_and_table(engine: Engine) -> None:
    """
    Create bronze schema and bronze.sp500_tickers table if they do not exist.

    Table structure:
        ticker
        company_name
        source
        load_date
        load_ts

    load_date and load_ts are generated by SQL Server defaults.
    """
    ddl = f"""
    IF NOT EXISTS (
        SELECT 1
        FROM sys.schemas
        WHERE name = '{TARGET_SCHEMA}'
    )
    BEGIN
        EXEC('CREATE SCHEMA {TARGET_SCHEMA}');
    END;

    IF OBJECT_ID('{FULL_TABLE_NAME}', 'U') IS NULL
    BEGIN
        CREATE TABLE {FULL_TABLE_NAME} (
            ticker VARCHAR(20) NOT NULL PRIMARY KEY,
            company_name VARCHAR(255) NULL,
            source VARCHAR(50) NULL,
            load_date DATE NOT NULL
                CONSTRAINT DF_{TARGET_TABLE}_load_date
                DEFAULT CAST(GETDATE() AS DATE),
            load_ts DATETIME2(0) NOT NULL
                CONSTRAINT DF_{TARGET_TABLE}_load_ts
                DEFAULT SYSDATETIME()
        );
    END;
    """

    with engine.begin() as conn:
        conn.execute(text(ddl))

    log(f"Ensured schema/table exists: {FULL_TABLE_NAME}")


# ============================================================
# SQL Load
# ============================================================
def get_table_row_count(engine: Engine) -> int:
    """Return row count of the target table."""
    sql = text(f"SELECT COUNT(*) FROM {FULL_TABLE_NAME};")
    with engine.begin() as conn:
        return conn.execute(sql).scalar()


def truncate_target_table(engine: Engine) -> None:
    """
    Remove all existing rows from bronze.sp500_tickers.

    Using DELETE instead of TRUNCATE to avoid issues if future FK relationships appear.
    """
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {FULL_TABLE_NAME};"))

    log(f"Existing rows deleted from {FULL_TABLE_NAME}")


def load_sp500_to_sql(engine: Engine, df: pd.DataFrame) -> None:
    """
    Load the transformed S&P 500 DataFrame into SQL Server.

    Python inserts only:
        ticker
        company_name
        source

    SQL Server automatically populates:
        load_date
        load_ts
    """
    insert_df = df[["ticker", "company_name", "source"]].copy()

    log("Preview of DataFrame to insert:")
    print(insert_df.head())
    log(f"Rows to insert: {len(insert_df)}")
    log(f"Columns to insert: {insert_df.columns.tolist()}")

    before_count = get_table_row_count(engine)
    log(f"Rows currently in {FULL_TABLE_NAME} before delete: {before_count}")

    truncate_target_table(engine)

    with engine.begin() as conn:
        insert_df.to_sql(
            name=TARGET_TABLE,
            con=conn,
            schema=TARGET_SCHEMA,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=200
        )

    log("df.to_sql completed successfully.")

    after_count = get_table_row_count(engine)
    log(f"Rows currently in {FULL_TABLE_NAME} after insert: {after_count}")

    if after_count != len(insert_df):
        raise ValueError(
            f"Row count validation failed. "
            f"Expected {len(insert_df)} rows, but found {after_count} rows in SQL."
        )


# ============================================================
# Main
# ============================================================
def main() -> None:
    log("=" * 70)
    log("BRONZE STEP 01 - LOAD S&P 500 TICKERS")
    log("=" * 70)

    # 1) Extract
    raw_df = fetch_sp500_from_wikipedia()

    # 2) Transform
    df = transform_sp500_dataframe(raw_df)

    # 3) Connect to SQL Server
    log("Connecting to SQL Server...")
    engine = get_sqlalchemy_engine()
    log("SQLAlchemy engine created successfully.")

    # 4) Print connection info so you know exactly where Python is writing
    print_sql_connection_info(engine)

    # 5) Ensure schema/table exist
    log(f"Ensuring {FULL_TABLE_NAME} exists...")
    ensure_bronze_schema_and_table(engine)

    # 6) Inspect target table
    inspect_target_table(engine)

    # 7) Load into SQL Server
    log(f"Loading S&P 500 ticker list into {FULL_TABLE_NAME}...")
    load_sp500_to_sql(engine, df)

    log("SUCCESS - bronze.sp500_tickers has been loaded.")
    log(f"Total tickers loaded: {len(df)}")
    log("=" * 70)


if __name__ == "__main__":
    main()