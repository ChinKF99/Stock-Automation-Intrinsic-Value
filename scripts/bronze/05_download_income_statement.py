"""
============================================================
05_download_income_statement.py

Download income statement from Financial Modeling Prep.

Source
------
bronze.sp500_tickers

Output
------
data/raw/income_statement/*.json
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
    FMP_INCOME_URL,
    INCOME_STATEMENT_FOLDER,
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

    print_connection_info(engine)

    # tickers = get_sp500_tickers(BRONZE_02_SCHEMA_TABLE, engine)

    download_endpoint(
        ["APPL"], #to replace with tickers variable after testing.
        FMP_INCOME_URL,
        INCOME_STATEMENT_FOLDER,
        "Company Profile",
        FMP_BATCH_SIZE
    )

if __name__ == "__main__":
    main()