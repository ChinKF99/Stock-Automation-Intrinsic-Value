"""
============================================================
11_download_ratios.py

Download ratios (TTM) from Financial Modeling Prep.

Source
------
bronze.sp500_tickers

Output
------
data/raw/ratios/*.json
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
    FMP_RATIOS_URL,
    RATIOS_TTM_FOLDER,
    FMP_BATCH_SIZE,
)

from utils.sql_utils import (
    print_connection_info
)

from utils.download_utils import download_endpoint

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

def main():

    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    # Use this code if you have FMP Plan other than "BASIC"
    # tickers = get_sp500_tickers(BRONZE_02_SCHEMA_TABLE, engine)

    # Use this code if you have "BASIC" FMP Plan
    tickers = ["AAPL", "ADBE", "AMD","INTC", "MSFT", "NVDA", "PLTR", "GOOGL", "META", "NFLX","AMZN"]
    
    download_endpoint(
        tickers,
        FMP_RATIOS_URL,
        RATIOS_TTM_FOLDER,
        "Ratios", # e.g. "company_profile", "income_statement"
        FMP_BATCH_SIZE
    )

if __name__ == "__main__":
    main()