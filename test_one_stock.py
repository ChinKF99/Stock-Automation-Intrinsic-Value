import os
import requests
import pandas as pd
from dotenv import load_dotenv

# =====================================================
# CONFIG
# =====================================================
TEST_TICKER = "AAPL"
OUTPUT_FILE = "test_one_stock_output.csv"

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

        # Try to parse JSON safely
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

    # IMPORTANT:
    # These are CURRENT /stable endpoints to test.
    # We are not using the legacy /api/v3 profile/income/balance/cashflow URLs anymore.

    urls = {
        # Company profile / reference data
        "profile": f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={API_KEY}",

        # Latest income statement
        "income": f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&limit=1&apikey={API_KEY}",

        # Latest balance sheet
        "balance": f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ticker}&limit=1&apikey={API_KEY}",

        # Latest cash flow statement
        "cashflow": f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&limit=1&apikey={API_KEY}",

        # Ratios / TTM-like metrics
        # If this fails, we will remove it and compute some ratios ourselves later.
        "ratios": f"https://financialmodelingprep.com/stable/ratios-ttm?symbol={ticker}&apikey={API_KEY}",
    }

    results = {}

    for name, url in urls.items():
        results[name] = fetch_json(session, name, url)

    # =================================================
    # PARSE RESULTS SAFELY
    # =================================================
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

    row = {
        "Ticker": ticker,

        # Profile / reference data
        "Company_Name": p.get("companyName") or p.get("company_name") or p.get("name"),
        "Sector": p.get("sector"),
        "Industry": p.get("industry"),
        "Current_Price": p.get("price"),
        "Market_Cap": p.get("mktCap") or p.get("marketCap"),
        "Shares_Outstanding": p.get("sharesOutstanding"),

        # Income statement
        "Revenue": i.get("revenue"),
        "Net_Income": i.get("netIncome"),
        "EPS": i.get("eps"),
        "Operating_Income": i.get("operatingIncome"),

        # Cash flow
        "Operating_Cash_Flow": c.get("operatingCashFlow") or c.get("netCashProvidedByOperatingActivities"),
        "Free_Cash_Flow": c.get("freeCashFlow"),
        "Capital_Expenditure": c.get("capitalExpenditure"),

        # Balance sheet
        "Cash_And_Short_Term_Investments": (
            b.get("cashAndShortTermInvestments")
            or b.get("cashAndCashEquivalents")
        ),
        "Total_Debt": b.get("totalDebt"),
        "Net_Debt": b.get("netDebt"),
        "Total_Equity": b.get("totalStockholdersEquity"),

        # Ratios
        "PE_Ratio": r.get("peRatioTTM") or r.get("peRatio"),
        "Price_to_Book": r.get("priceToBookRatioTTM") or r.get("priceToBookRatio"),
        "ROE": r.get("returnOnEquityTTM") or r.get("returnOnEquity"),
        "ROA": r.get("returnOnAssetsTTM") or r.get("returnOnAssets"),
        "Current_Ratio": r.get("currentRatioTTM") or r.get("currentRatio"),
        "Debt_to_Equity": r.get("debtEquityRatioTTM") or r.get("debtEquityRatio"),
    }

    df = pd.DataFrame([row])
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n======================================")
    print("1-stock stable-endpoint test completed.")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(df.T)
    print("======================================")

if __name__ == "__main__":
    main()