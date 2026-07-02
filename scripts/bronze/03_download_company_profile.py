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
import json
import time
import requests
import pandas as pd

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    get_sqlalchemy_engine,
    FMP_API_KEY,
    FMP_PROFILE_URL,
    COMPANY_PROFILE_FOLDER,
    FMP_BATCH_SIZE,
    REQUEST_SLEEP_SECONDS
)

from utils.sql_utils import (
    BRONZE_02_TARGET_TABLE
)

from utils.file_utils import(
    json_exists
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)


def get_sp500_tickers():

    logger.info("Reading tickers from SQL Server...")

    sql = f"""
        SELECT ticker
        FROM {BRONZE_02_TARGET_TABLE}
        ORDER BY ticker
    """

    engine = get_sqlalchemy_engine()

    df = pd.read_sql(sql, engine)

    logger.info(f"{len(df)} tickers loaded.")

    return df["ticker"].tolist()


def download_profile(ticker):

    url = f"{FMP_PROFILE_URL}?symbol={ticker}&apikey={FMP_API_KEY}"

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def save_json(ticker, data):

    file = COMPANY_PROFILE_FOLDER / f"{ticker}.json"

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

def main():

    logger.info("=" * 60)
    logger.info("STEP 03 - DOWNLOAD COMPANY PROFILE")
    logger.info("=" * 60)

    tickers = get_sp500_tickers()

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

            profile = download_profile(ticker)

            save_json(
                ticker,
                profile
            )

            downloaded += 1

            time.sleep(REQUEST_SLEEP_SECONDS)

            if downloaded >= FMP_BATCH_SIZE:

                logger.info("Today's batch limit reached.")

                break

        except requests.exceptions.HTTPError as ex:

            logger.error(f"{ticker}: HTTP Error {ex}")

        except requests.exceptions.Timeout:

            logger.error(f"{ticker}: Timeout")

        except Exception as ex:

            logger.exception(ex)

if __name__ == "__main__":
    main()