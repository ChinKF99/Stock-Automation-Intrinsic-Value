"""
============================================================
download_utils.py

Generic downloader for all FMP endpoints.

Used by

03_download_company_profile.py
05_download_income_statement.py
07_download_balance_sheet.py
09_download_cashflow_statement.py
11_download_ratios.py

============================================================
"""
import os
import sys
from pathlib import Path
import pandas as pd
import requests
from utils.api_utils import (
    get_json,
    save_json,
    json_exists,
    wait
)

from config.logging_config import setup_logger

# 1. Get the base name (e.g., "script.py")
raw_name = os.path.basename(sys.argv[0])

# 2. Separate name from extension and add .log (e.g., "script.log")
log_name = os.path.splitext(raw_name)[0]

# 3. Initialize the logger
logger = setup_logger(log_name)

def download_endpoint(
    tickers,
    endpoint_url,
    output_folder,
    endpoint_name,
    fmp_batch_size,
    params_builder=None
):
    """
    Generic downloader.

    Parameters
    ----------
    tickers
        ticker from SQL.

    endpoint_url
        FMP endpoint.

    output_folder
        Folder to save JSON.

    endpoint_name
        Logging purposes only.

    fmp_batch_size
        Limit 5 request per seassion.
          
    params_builder
        Optional function for endpoint-specific parameters.
    """

    logger.info("=" * 60)
    logger.info(f"Downloading {endpoint_name}")
    logger.info("=" * 60)

    downloaded = 0

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    for index, ticker in enumerate(tickers, start=1):
        try:
            
            if json_exists(output_folder, ticker):
                logger.info(
                    f"[{index}/{len(tickers)}] {ticker} already exists. Skipped.")
                
                continue

            logger.info(f"[{index}/{len(tickers)}] Downloading {ticker}")

            params = ticker

            if params_builder:

                params.update(params_builder(ticker))

            data = get_json(params,endpoint_url)

            save_json(params,data, output_folder)

            downloaded += 1

            # API rate limit
            wait()

            if downloaded >= fmp_batch_size:
                logger.info("Today's batch limit reached.")

                break

        except requests.exceptions.HTTPError as ex:

            logger.error(f"{ticker}: HTTP Error {ex}")

        except requests.exceptions.Timeout:

            logger.error(f"{ticker}: Timeout")

        except Exception as ex:
            logger.exception(ex)

    logger.info("=" * 60)
    logger.info(f"{endpoint_name} Finished")
    logger.info("=" * 60)