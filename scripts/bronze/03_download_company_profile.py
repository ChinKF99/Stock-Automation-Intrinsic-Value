"""
============================================================
03_download_company_profile.py

Download company profiles from Financial Modeling Prep.

Source
------
bronze.sp500_tickers

Output
------
data/raw/company_profile/*.json
============================================================
"""

from pathlib import Path
import sys

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    get_sqlalchemy_engine,
    FMP_PROFILE_URL,
    COMPANY_PROFILE_FOLDER,
    FMP_BATCH_SIZE,
)

from utils.sql_utils import (
    print_connection_info,
    get_sp500_tickers,
    BRONZE_02_SCHEMA_TABLE
)

from utils.download_utils import download_endpoint

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

def main():

    engine = get_sqlalchemy_engine()

    # Use this code if you have FMP Plan other than "BASIC"
    # tickers = get_sp500_tickers(BRONZE_02_SCHEMA_TABLE, engine)

    # Use this code if you have "BASIC" FMP Plan
    tickers = ["AAPL", "ADBE", "AMD","INTC", "MSFT", "NVDA", "PLTR", "GOOGL", "META", "NFLX","AMZN"]

    download_endpoint(
        tickers,
        FMP_PROFILE_URL,
        COMPANY_PROFILE_FOLDER,
        "Company Profile",
        FMP_BATCH_SIZE
    )

if __name__ == "__main__":
    main()