#=====================================
# Common file helper functions
#=====================================

import time
import requests
import json
from pathlib import Path
import pandas as pd

from config.config import (
    FMP_API_KEY,
    HTTP_TIMEOUT,
    REQUEST_SLEEP_SECONDS,
    COMPANY_PROFILE_FOLDER
)

from config.logging_config import setup_logger
logger = setup_logger(__name__)

# ==========================================================
# Read CSV file into a dataframe
# ==========================================================

def read_csv(csv_file) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.
    """
    if not csv_file.exists():
        raise FileNotFoundError(
            f"CSV file not found:\n{csv_file}")

    logger.info("Reading CSV...")

    df = pd.read_csv(csv_file)

    logger.info(f"{len(df)} rows loaded from CSV.")

    return df

# ==========================================================
# Save Dataframe as CSV file
# ==========================================================

def save_csv(df: pd.DataFrame, file_path: Path):

    logger.info("Saving CSV...")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8"
    )

    logger.info("CSV saved successfully.")
    logger.info("Output file: %s", file_path)

# ==============================================================
# Generic get request and parse JSON into Python dictionary
# ==============================================================

def get_json( ticker, fmp_endpoint, params=None):
    """
    Execute GET request against FMP.

    Returns
    -------
    list | dict
    """

    if params is None:
        params = {}

    params = {
    "symbol": ticker,
    "apikey": FMP_API_KEY
    }
    
    response = requests.get(
        fmp_endpoint,
        params=params,
        timeout=HTTP_TIMEOUT
    )

    response.raise_for_status()

    # return response.json()

    data = response.json() # To delete after testing

    # Safely return the first dictionary if the list is not empty (to delete after testing)
    return data[0] if isinstance(data, list) and data else data

# ==========================================================
# Save JSON
# ==========================================================

def save_json(ticker, data, output_folder):

    file = output_folder / f"{ticker}.json"

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
        )

# ==========================================================
# Check if json file existed
# ==========================================================
def json_exists(folder: Path, ticker: str) -> bool:
    return (folder / f"{ticker}.json").exists()

# ==========================================================
# Sleep (API rate limit)
# ==========================================================

def wait():

    time.sleep(REQUEST_SLEEP_SECONDS)