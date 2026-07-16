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
import pandas as pd

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
    BRONZE_02_SCHEMA_TABLE
)

from utils.download_utils import download_endpoint

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

from utils.download_utils import download_endpoint


def income_params(_):

    return {
        "limit": 10
    }


def main():

    download_endpoint(

        csv_file=SP500_CSV,

        endpoint_url=FMP_INCOME_URL,

        output_folder=INCOME_STATEMENT_FOLDER,

        endpoint_name="Income Statement",

        params_builder=income_params

    )


if __name__ == "__main__":
    main()