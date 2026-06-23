import os
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("MY_API_KEY")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "stock_automation")

FMP_BASE = "https://financialmodelingprep.com/stable"

DAILY_API_CALL_BUDGET = 250
SAFE_DAILY_CALL_BUDGET = 150     # leave room for retries/tests
CALLS_PER_TICKER = 5
DEFAULT_BATCH_SIZE = SAFE_DAILY_CALL_BUDGET // CALLS_PER_TICKER   # 30 max safe theoretical
RECOMMENDED_BATCH_SIZE = 20