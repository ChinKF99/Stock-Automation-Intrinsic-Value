import os
import requests
import pandas as pd
from dotenv import load_dotenv

# =====================================================
# CONFIG
# =====================================================
TEST_TICKER = "AAPL"

# Define your existing folder path and file name
FOLDER_PATH = "data"
OUTPUT_FILE = "test_one_stock_output.csv"

# Combine them cleanly
FULL_PATH = os.path.join(FOLDER_PATH, OUTPUT_FILE)

# =====================================================
# LOAD API KEY
# =====================================================
load_dotenv()
API_KEY = os.environ.get("MY_API_KEY")

if not API_KEY:
    raise ValueError("MY_API_KEY not found in .env file")

print("API key loaded successfully.")

# =====================================================
# HELPER FUNCTION
# =====================================================
def fetch_json(session, name, url):
    print(f"\nTesting endpoint: {name}")
    print(url)

    try:
        response = session.get(url, timeout=30)
        print("Status code:", response.status_code)

        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.status_code != 200:
            print("FAILED")
            print(data)
            return None

        if not data:
            print("Returned empty data")
            return None

        print("SUCCESS")
        if isinstance(data, list) and len(data) > 0:
            print("Sample response:")
            print(data[0])
        else:
            print("Sample response:")
            print(data)

        return data

    except Exception as e:
        print(f"ERROR on {name}: {e}")
        return None

# =====================================================
# MAIN
# =====================================================
def main():
    ticker = TEST_TICKER
    session = requests.Session()

    urls = {
        "profile": f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={API_KEY}",
        "income": f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&limit=1&apikey={API_KEY}",
        "balance": f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ticker}&limit=1&apikey={API_KEY}",
        "cashflow": f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&limit=1&apikey={API_KEY}",
        "ratios": f"https://financialmodelingprep.com/stable/ratios-ttm?symbol={ticker}&apikey={API_KEY}",
    }

    results = {}
    for name, url in urls.items():
        results[name] = fetch_json(session, name, url)

    profile = results.get("profile")
    income = results.get("income")
    balance = results.get("balance")
    cashflow = results.get("cashflow")
    ratios = results.get("ratios")

    p = profile[0] if isinstance(profile, list) and len(profile) > 0 else {}
    i = income[0] if isinstance(income, list) and len(income) > 0 else {}
    b = balance[0] if isinstance(balance, list) and len(balance) > 0 else {}
    c = cashflow[0] if isinstance(cashflow, list) and len(cashflow) > 0 else {}
    r = ratios[0] if isinstance(ratios, list) and len(ratios) > 0 else {}

    # Shares outstanding is not present in your profile response,
    # so use weighted average diluted shares as the best available fallback.
    shares_outstanding = (
        p.get("sharesOutstanding")
        or i.get("weightedAverageShsOutDil")
        or i.get("weightedAverageShsOut")
    )

    row = {
        "Ticker": ticker,

        # Profile
        "Company_Name": p.get("companyName") or p.get("name"),
        "Sector": p.get("sector"),
        "Industry": p.get("industry"),
        "Current_Price": p.get("price"),
        "Market_Cap": p.get("marketCap") or p.get("mktCap"),
        "Shares_Outstanding": shares_outstanding,

        # Income statement
        "Revenue": i.get("revenue"),
        "Gross_Profit": i.get("grossProfit"),
        "Operating_Income": i.get("operatingIncome"),
        "Net_Income": i.get("netIncome"),
        "EPS": i.get("eps"),
        "Weighted_Avg_Shares_Diluted": i.get("weightedAverageShsOutDil"),

        # Cash flow
        "Operating_Cash_Flow": c.get("operatingCashFlow") or c.get("netCashProvidedByOperatingActivities"),
        "Free_Cash_Flow": c.get("freeCashFlow"),
        "Capital_Expenditure": c.get("capitalExpenditure"),

        # Balance sheet
        "Cash_And_Short_Term_Investments": b.get("cashAndShortTermInvestments") or b.get("cashAndCashEquivalents"),
        "Total_Debt": b.get("totalDebt"),
        "Net_Debt": b.get("netDebt"),
        "Total_Equity": b.get("totalStockholdersEquity") or b.get("totalEquity"),

        # Ratios (stable endpoint field names)
        "PE_Ratio": r.get("priceToEarningsRatioTTM"),
        "Price_to_Book": r.get("priceToBookRatioTTM"),
        "Price_to_Sales": r.get("priceToSalesRatioTTM"),
        "Current_Ratio": r.get("currentRatioTTM"),
        "Debt_to_Equity": r.get("debtToEquityRatioTTM"),

        # Derived metrics from stable ratios
        "Gross_Margin": r.get("grossProfitMarginTTM"),
        "Operating_Margin": r.get("operatingProfitMarginTTM"),
        "Net_Margin": r.get("netProfitMarginTTM"),
    }

    # Derive ROE and ROA manually because the stable ratios response
    # you showed does not include explicit returnOnEquityTTM / returnOnAssetsTTM.
    net_income = row["Net_Income"]
    total_equity = row["Total_Equity"]
    total_assets = b.get("totalAssets")

    row["ROE"] = (net_income / total_equity) if (net_income is not None and total_equity not in [None, 0]) else None
    row["ROA"] = (net_income / total_assets) if (net_income is not None and total_assets not in [None, 0]) else None

    df = pd.DataFrame([row])
    df.to_csv(FULL_PATH, index=False)

    print("\n======================================")
    print("1-stock stable-endpoint test completed.")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(df.T)
    print("======================================")

if __name__ == "__main__":
    main()