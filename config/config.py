import os
from dotenv import load_dotenv

load_dotenv()

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
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

if not all([SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD]):
    raise ValueError("One or more SQL Server environment variables are missing in .env")

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