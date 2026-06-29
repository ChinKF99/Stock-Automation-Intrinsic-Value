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
    SP500_CSV,
    HEADERS,
    HTTP_TIMEOUT,
)

# ==========================================================
# Logging Helper
# ==========================================================
def log(message: str):
    print(f"[INFO] {message}")

# ==========================================================
# Extract S&P 500 Tickers
# ==========================================================
def download_sp500_tickers():

    log("Extracting S&P 500 tickers from Wikipedia...")

    response = requests.get(
        SP500_WIKIPEDIA_URL,
        headers=HEADERS,
        timeout=HTTP_TIMEOUT
    )

    response.raise_for_status()

    html_stream = io.StringIO(response.text)

    tables = pd.read_html(
        html_stream,
        match="Symbol"
    )

    if not tables:
        raise ValueError("Unable to locate the S&P 500 constituents table.")

    df = tables[0]

    # Keep only ticker column
    df = df[["Symbol"]].copy()

    df.rename(
        columns={"Symbol": "ticker"},
        inplace=True
    )

    df["ticker"] = (
        df["ticker"]
        .str.strip()
        .str.upper()
        .str.replace(".", "-", regex=False)
    )

    df.drop_duplicates(inplace=True)

    return df

# ==========================================================
# Save CSV
# ==========================================================
def save_csv(df):

    log(f"Saving CSV to:\n{SP500_CSV}")

    with open(
        SP500_CSV,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(["ticker"])

        writer.writerows(df.values.tolist())

    log("CSV saved successfully.")

# ==========================================================
# Main
# ==========================================================
def main():

    print("=" * 60)
    print("BRONZE STEP 01 - DOWNLOAD S&P 500 TICKERS")
    print("=" * 60)

    df = download_sp500_tickers()

    log(f"Total tickers found : {len(df)}")

    print("\nPreview:")

    print(df.head())

    save_csv(df)

    print("\nCompleted successfully.")

if __name__ == "__main__":
    main()