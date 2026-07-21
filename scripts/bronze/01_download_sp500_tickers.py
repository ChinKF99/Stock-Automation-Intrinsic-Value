from pathlib import Path
import sys
import io
import csv

import pandas as pd
import requests

# ==========================================================
# Make project root importable
# ==========================================================
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Project Configuration
# ==========================================================
from config.config import (
    SP500_WIKIPEDIA_URL,
    SP500_TICKERS_CSV_FILE_PATH,
    HEADERS,
    HTTP_TIMEOUT,
)

from utils.api_utils import(
    save_csv
)


from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ====================================================================
# Extract S&P 500 Tickers from wikipedia and save it into data frame
# ====================================================================
def download_sp500_tickers() -> pd.DataFrame:
    """
    Download the latest S&P 500 constituent list from Wikipedia.
    """

    logger.info("Downloading S&P 500 ticker list...")

    response = requests.get(
        SP500_WIKIPEDIA_URL,
        headers=HEADERS,
        timeout=HTTP_TIMEOUT,
    )

    response.raise_for_status()

    html_stream = io.StringIO(response.text)

    tables = pd.read_html(
        html_stream,
        match="Symbol",
    )

    if not tables:
        raise ValueError(
            "Unable to locate the S&P 500 constituents table."
        )

    df = tables[0]

    logger.info("Wikipedia table downloaded successfully.")

    df = df[["Symbol"]].copy()

    df.rename(
        columns={
            "Symbol": "ticker"
        },
        inplace=True,
    )

    df["ticker"] = (
        df["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "-", regex=False)
    )

    df.drop_duplicates(inplace=True)

    logger.info("Total unique tickers found: %s", len(df))

    return df

# ==========================================================
# Main
# ==========================================================
def main():

    logger.info("=" * 70)
    logger.info("BRONZE STEP 01 - DOWNLOAD S&P 500 TICKERS")
    logger.info("=" * 70)

    try:

        df = download_sp500_tickers()

        logger.info("Preview:")
        logger.info("\n%s", df.head().to_string(index=False))

        save_csv(df,SP500_TICKERS_CSV_FILE_PATH)

    except Exception as ex:
        logger.exception("Step 01 failed.")
        logger.excepion(ex)

    logger.info("=" * 60)
    logger.info(f"Finished")
    logger.info("=" * 60)
    
if __name__ == "__main__":
    main()