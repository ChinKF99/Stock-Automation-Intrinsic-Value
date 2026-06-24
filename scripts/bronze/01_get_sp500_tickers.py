import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# =========================================================
# Make project root importable
# This file is inside: scripts/bronze/
# We want to import from: config/config.py
# =========================================================
CURRENT_FILE = os.path.abspath(__file__)
BRONZE_DIR = os.path.dirname(CURRENT_FILE)                 # .../scripts/bronze
SCRIPTS_DIR = os.path.dirname(BRONZE_DIR)                  # .../scripts
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)                # project root

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import (
    SQL_SERVER,
    SQL_DATABASE,
    SQL_USERNAME,
    SQL_PASSWORD,
    SQL_DRIVER
)

def get_sql_engine():
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )

    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"
    )
    return engine

def clean_ticker(ticker: str) -> str:
    """
    Wikipedia may use BRK.B, BF.B etc.
    FMP usually expects BRK-B, BF-B.
    """
    ticker = str(ticker).strip().upper()
    ticker = ticker.replace(".", "-")
    return ticker

def main():
    print("Downloading S&P 500 ticker list from Wikipedia...")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    tables = pd.read_html(url)
    df = tables[0].copy()

    print("Columns found from Wikipedia table:")
    print(df.columns.tolist())

    df = df.rename(columns={
        "Symbol": "ticker",
        "Security": "company_name"
    })

    if "ticker" not in df.columns or "company_name" not in df.columns:
        raise ValueError(
            f"Expected columns not found after rename. Current columns: {df.columns.tolist()}"
        )

    df["ticker"] = df["ticker"].astype(str).apply(clean_ticker)
    df["company_name"] = df["company_name"].astype(str)

    tickers_df = df[["ticker", "company_name"]].copy()
    tickers_df["source"] = "Wikipedia"

    print(f"Downloaded {len(tickers_df)} tickers.")

    engine = get_sql_engine()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM bronze.sp500_tickers"))

    tickers_df.to_sql(
        "sp500_tickers",
        engine,
        schema="bronze",
        if_exists="append",
        index=False
    )

    print("bronze.sp500_tickers loaded successfully.")

if __name__ == "__main__":
    main()