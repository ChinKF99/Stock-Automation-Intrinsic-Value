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
import requests
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

from utils.file_utils import(
    json_exists,
    get_json,
    save_json,
    wait
)

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

    logger.info("=" * 60)
    logger.info("STEP 03 - DOWNLOAD COMPANY PROFILE")
    logger.info("=" * 60)
    
    engine = get_sqlalchemy_engine()

    print_connection_info(engine)

    tickers = get_sp500_tickers(engine)

    downloaded = 0

    for index, ticker in enumerate(tickers, start=1):

        try:
            if json_exists(COMPANY_PROFILE_FOLDER, ticker):

                logger.info(
                    f"[{index}/{len(tickers)}] {ticker} already exists. Skipped."
                )

                continue

            logger.info(
                f"[{index}/{len(tickers)}] Downloading {ticker}"
            )

            profile = get_json(ticker, FMP_PROFILE_URL)

            save_json(
                ticker,
                profile
            )

            downloaded += 1

            # API rate limit
            wait()

            if downloaded >= FMP_BATCH_SIZE:

                logger.info("Today's batch limit reached.")

                break

        except requests.exceptions.HTTPError as ex:

            logger.error(f"{ticker}: HTTP Error {ex}")

        except requests.exceptions.Timeout:

            logger.error(f"{ticker}: Timeout")

        except Exception as ex:
            logger.exception("Step 03 failed.")
            logger.exception(ex)

if __name__ == "__main__":
    main()