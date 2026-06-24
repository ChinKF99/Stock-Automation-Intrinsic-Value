# config/config.py
from pathlib import Path
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
# =========================
# FMP
# =========================
FMP_API_KEY = os.getenv("MY_API_KEY")

if not FMP_API_KEY:
    raise ValueError("FMP_API_KEY not found in .env")

# =========================
# SQL Server
# =========================
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_TRUSTED_CONNECTION = os.getenv("SQL_TRUSTED_CONNECTION", "yes")

def get_sqlalchemy_engine():
    """
    Create SQLAlchemy engine for SQL Server using Windows Authentication.
    """
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"Trusted_Connection={SQL_TRUSTED_CONNECTION};"
        f"TrustServerCertificate=yes;"
    )

    connection_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"
    return create_engine(connection_url, fast_executemany=True)

# =========================
# FMP batch settings
# =========================
BATCH_SIZE = 20
REQUEST_SLEEP_SECONDS = 0.25

# =========================
# Stable FMP endpoints
# =========================
FMP_PROFILE_URL = "https://financialmodelingprep.com/stable/profile"
FMP_INCOME_URL = "https://financialmodelingprep.com/stable/income-statement"
FMP_BALANCE_URL = "https://financialmodelingprep.com/stable/balance-sheet-statement"
FMP_CASHFLOW_URL = "https://financialmodelingprep.com/stable/cash-flow-statement"
FMP_RATIOS_URL = "https://financialmodelingprep.com/stable/ratios-ttm"