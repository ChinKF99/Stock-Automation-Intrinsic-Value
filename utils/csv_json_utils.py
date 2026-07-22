#=====================================
# Common file helper functions
#=====================================

import os
import sys
import time
import requests
import json
from pathlib import Path
import pandas as pd

from config.config import (
    FMP_API_KEY,
    HTTP_TIMEOUT,
    REQUEST_SLEEP_SECONDS,
)

from config.logging_config import setup_logger

# 1. Get the base name (e.g., "script.py")
raw_name = os.path.basename(sys.argv[0])

# 2. Separate name from extension and add .log (e.g., "script.log")
log_name = os.path.splitext(raw_name)[0]

# 3. Initialize the logger
logger = setup_logger(log_name)

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
# Get Request for FMP End point to get JSON File.
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

    return response.json()

# ==========================================================
# Save the JSON file from Get Request to file directory
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
# Check if JSON file already existed in the file directory
# ==========================================================
def json_exists(folder: Path, ticker: str) -> bool:
    return (folder / f"{ticker}.json").exists()

# ==========================================================
# Sleep (API rate limit)
# ==========================================================

def wait():

    time.sleep(REQUEST_SLEEP_SECONDS)

# ==========================================================
# Read JSON file and convert it to Pandas data frame
# ========================================================== 

def read_json_files(end_point_name, folder_name) -> pd.DataFrame:
   
    # Read all company profile JSON files and return a single DataFrame.
    
    logger.info(f"Reading {end_point_name} JSON files...") # e.g. "Company Profile", "Income Statement"

    json_files = sorted(folder_name.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in:\n{folder_name}"
        )

    logger.info(f"Found {len(json_files)} JSON files.")

    rows = []

    for file in json_files:

        try:

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data:
                logger.warning(f"{file.name} is empty.")
                continue
            
            # -----------------------------
            # Case 1
            # JSON Object
            # {
            #    ...
            # }
            # -----------------------------
            if isinstance(data, dict):
                rows.append(data)

            # -----------------------------
            # Case 2
            # JSON Array
            # [
            #   {...},
            #   {...}
            # ]
            # -----------------------------
            elif isinstance(data, list):
                rows.extend(data)

        except Exception as ex:
            logger.exception(
                f"Failed reading {file.name}: {ex}"
            )

    df = pd.DataFrame(rows)
    
    logger.info(f"{len(df)} company profiles loaded into data frame.")

    return df
