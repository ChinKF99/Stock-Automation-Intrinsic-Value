import os
import sys
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from io import StringIO

# =========================================================
# Make project root importable
# =========================================================
CURRENT_FILE = os.path.abspath(__file__)
BRONZE_DIR = os.path.dirname(CURRENT_FILE)
SCRIPTS_DIR = os.path.dirname(BRONZE_DIR)
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config import (
    SQL_SERVER,
    SQL_DATABASE,
    SQL_USERNAME,
    SQL_PASSWORD,
    SQL_DRIVER
)

# =========================================================
# SQL connection
# =========================================================
def get_sql_engine():
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )

    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"
    )
    return engine

# =========================================================
# Clean ticker for FMP compatibility
# Example: BRK.B -> BRK-B
# =========================================================
def clean_ticker(ticker: str) -> str:
    ticker = str(ticker).strip().upper()
    ticker = ticker.replace(".", "-")
    return ticker

# =========================================================
# Download S&P 500 table from Wikipedia safely
# =========================================================
def download_sp500_table():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    }

    print("Requesting Wikipedia page...")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    # Read tables from HTML text instead of direct URL
    html_text = response.text
    tables = pd.read_html(StringIO(html_text))

    if not tables:
        raise ValueError("No HTML tables found on Wikipedia page.")

    # The first table is normally the S&P 500 constituents table
    df = tables[0].copy()
    return df

def main():
    print("Downloading S&P 500 ticker list from Wikipedia...")

    df = download_sp500_table()

    print("Columns found from Wikipedia table:")
    print(df.columns.tolist())

    # Expected Wikipedia columns usually include:
    # Symbol, Security, GICS Sector, GICS Sub-Industry, Headquarters Location, ...
    rename_map = {
        "Symbol": "ticker",
        "Security": "company_name"
    }

    df = df.rename(columns=rename_map)

    if "ticker" not in df.columns or "company_name" not in df.columns:
        raise ValueError(
            "Expected columns 'Symbol' and 'Security' were not found in the Wikipedia table. "
            f"Actual columns: {df.columns.tolist()}"
        )

    df["ticker"] = df["ticker"].astype(str).apply(clean_ticker)
    df["company_name"] = df["company_name"].astype(str)

    tickers_df = df[["ticker", "company_name"]].copy()
    tickers_df["source"] = "Wikipedia"

    print(f"Downloaded {len(tickers_df)} tickers.")
    print(tickers_df.head())

    engine = get_sql_engine()

    # Clear old ticker universe
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM bronze.sp500_tickers"))

    # Load into SQL Server
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