# ==========================================================
# config/config.py
# Central configuration for the Stock ETL project
# ==========================================================

from pathlib import Path
from urllib.parse import quote_plus
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# ==========================================================
# Project Directories
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
BRONZE_DATA_DIR = DATA_DIR / "bronze"
LOG_DIR = BASE_DIR / "logs"
COMPANY_PROFILE_FOLDER = RAW_DATA_DIR/ "company_profile"
INCOME_STATEMENT_FOLDER = RAW_DATA_DIR/ "income_statement"
BALANCE_SHEET_FOLDER = RAW_DATA_DIR / "balance_sheet"
CASH_FLOW_FOLDER = RAW_DATA_DIR / "cash_flow"

# Create folders automatically if missing
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
BRONZE_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
COMPANY_PROFILE_FOLDER.mkdir(parents=True,exist_ok=True)
INCOME_STATEMENT_FOLDER.mkdir(parents=True,exist_ok=True)
BALANCE_SHEET_FOLDER.mkdir(parents=True, exist_ok=True)
CASH_FLOW_FOLDER.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Raw SP500 tickers file path
# ==========================================================

SP500_TICKERS_CSV_FILE_PATH = RAW_DATA_DIR / "sp500_tickers.csv"

# ==========================================================
# Load .env
# ==========================================================

load_dotenv(BASE_DIR / ".env")

# ==========================================================
# Financial Modeling Prep API Key
# ==========================================================

FMP_API_KEY = os.getenv("MY_API_KEY")

if not FMP_API_KEY:
    raise ValueError("MY_API_KEY not found inside .env")

# ==========================================================
# SQL Server
# ==========================================================

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_DRIVER = os.getenv(
    "SQL_DRIVER",
    "ODBC Driver 17 for SQL Server"
)
SQL_TRUSTED_CONNECTION = os.getenv(
    "SQL_TRUSTED_CONNECTION",
    "yes"
)

# ==========================================================
# SQLAlchemy Engine
# ==========================================================

def get_sqlalchemy_engine():

    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"Trusted_Connection={SQL_TRUSTED_CONNECTION};"
        f"TrustServerCertificate=yes;"
    )

    connection_url = (
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(conn_str)
    )

    return create_engine(
        connection_url,
        fast_executemany=True,
        future=True
    )

# ==========================================================
# HTTP Settings
# ==========================================================

HTTP_TIMEOUT = 30

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/137.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT
}

# ==========================================================
# Wikipdia source for tickers
# ==========================================================

SP500_WIKIPEDIA_URL = (
    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
)

# ==========================================================
# API Batch Settings
# ==========================================================

FMP_BATCH_SIZE = 5
REQUEST_SLEEP_SECONDS = 0.25
HTTP_TIMEOUT = 30

# ==========================================================
# Financial Modeling Prep Endpoints
# ==========================================================

FMP_PROFILE_URL = (
    "https://financialmodelingprep.com/stable/profile"
)

FMP_INCOME_URL = (
    "https://financialmodelingprep.com/stable/income-statement"
)

FMP_BALANCE_URL = (
    "https://financialmodelingprep.com/stable/balance-sheet-statement"
)

FMP_CASHFLOW_URL = (
    "https://financialmodelingprep.com/stable/cash-flow-statement"
)

FMP_RATIOS_URL = (
    "https://financialmodelingprep.com/stable/ratios-ttm"
)