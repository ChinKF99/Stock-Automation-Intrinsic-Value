import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# =====================================================
# STEP 0 - LOAD ENVIRONMENT VARIABLES
# =====================================================

#Looad local .env file if it exists
load_dotenv()

API_KEY = os.environ.get("MY_API_KEY")

if not API_KEY:
    raise ValueError("MY_API_KEY not found in environment variables.")
else:
    print("Success: API key securely loaded.")

# =====================================================
# STEP 1 - LOAD TICKERS
# =====================================================

ticker_file = "sp500_tickers.csv"

tickers_df = pd.read_csv(ticker_file)

print("Columns found in ticker file:", tickers_df.columns.tolist())

# Handle both possible column names: Ticker or Symbol
if "Ticker" in tickers_df.columns:
    ticker_list = tickers_df["Ticker"].dropna().astype(str).tolist()
elif "Symbol" in tickers_df.columns:
    ticker_list = tickers_df["Symbol"].dropna().astype(str).tolist()
else:
    raise ValueError(
        "Ticker file must contain either a 'Ticker' column or a 'Symbol' column."
    )

print(f"Loaded {len(ticker_list)} tickers.")