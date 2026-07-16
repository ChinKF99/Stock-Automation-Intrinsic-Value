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

def get_sp500_tickers(engine):

    logger.info("Reading tickers from SQL Server...")

    sql = f"""
        SELECT ticker
        FROM {BRONZE_02_SCHEMA_TABLE}
        ORDER BY ticker
    """

    df = pd.read_sql(sql, engine)

    logger.info(f"{len(df)} tickers loaded.")

    return df["ticker"].tolist()

def main():

    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    tickers = get_sp500_tickers(engine)

    download_endpoint(
        tickers,
        FMP_PROFILE_URL,
        COMPANY_PROFILE_FOLDER,
        "Company Profile",
        FMP_BATCH_SIZE
    )

if __name__ == "__main__":
    main()