import os
from dotenv import load_dotenv
import pandas as pd
import requests
import time

# Load local .env file if it exists
load_dotenv()
132
# This looks for the variable locally OR from GitHub Actions
api_key = os.environ.get("MY_FMP_APIKEY")
if not api_key:
    print("Error: MY_API_KEY not found in environment!")
else:
    print("Success: Variable securely loaded.")


API_KEY = "MY_API_KEY"

tickers = pd.read_csv("sp500_tickers.csv")

results = []

for ticker in tickers["Symbol"]:

    try:

        print(f"Downloading {ticker}")

        profile_url = (
            f"https://financialmodelingprep.com/api/v3/profile/"
            f"{ticker}?apikey={API_KEY}"
        )

        ratios_url = (
            f"https://financialmodelingprep.com/api/v3/ratios-ttm/"
            f"{ticker}?apikey={API_KEY}"
        )

        cashflow_url = (
            f"https://financialmodelingprep.com/api/v3/cash-flow-statement/"
            f"{ticker}?limit=1&apikey={API_KEY}"
        )

        profile = requests.get(profile_url).json()
        ratios = requests.get(ratios_url).json()
        cashflow = requests.get(cashflow_url).json()

        if not profile:
            continue

        p = profile[0]

        r = ratios[0] if ratios else {}

        cf = cashflow[0] if cashflow else {}

        results.append({

            "Ticker": ticker,
            "Company_Name": p.get("companyName"),

            "Sector": p.get("sector"),
            "Industry": p.get("industry"),

            "Market_Cap": p.get("mktCap"),
            "Current_Price": p.get("price"),

            "Shares_Outstanding": p.get("sharesOutstanding"),

            "PE_Ratio": r.get("peRatioTTM"),
            "Price_to_Book": r.get("priceToBookRatioTTM"),

            "ROE": r.get("returnOnEquityTTM"),
            "ROA": r.get("returnOnAssetsTTM"),

            "Current_Ratio": r.get("currentRatioTTM"),

            "Debt_to_Equity": r.get(
                "debtEquityRatioTTM"
            ),

            "Free_Cash_Flow":
                cf.get("freeCashFlow"),

            "Operating_Cash_Flow":
                cf.get("operatingCashFlow"),

        })

        time.sleep(0.2)

    except Exception as e:

        print(f"Error {ticker}: {e}")

fundamentals = pd.DataFrame(results)

fundamentals.to_csv(
    "sp500_fundamentals.csv",
    index=False
)

print("Finished.")