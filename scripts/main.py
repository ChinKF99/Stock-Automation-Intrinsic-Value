import os
from dotenv import load_dotenv
import pandas as pd
import requests

# =====================================================
# CONFIG
# =====================================================

TICKER_FILE = "sp500_tickers.csv"
OUTPUT_FUNDAMENTALS = "sp500_fundamentals.csv"
OUTPUT_DCF = "dcf_inputs.csv"
OUTPUT_FAILED = "failed_tickers.csv"

# If your FMP plan only supports older years, change these if needed.
REPORT_YEAR = 2024

# =====================================================
# STEP 0 - LOAD API KEY
# =====================================================

load_dotenv()
API_KEY = os.environ.get("MY_API_KEY")

if not API_KEY:
    raise ValueError(
        "MY_API_KEY not found. Put it in your .env file like:\n"
        "MY_API_KEY=your_actual_api_key"
    )

print("Success: API key securely loaded.")

# =====================================================
# STEP 1 - LOAD TICKERS
# =====================================================

def load_tickers(filepath: str) -> list[str]:
    """
    Load ticker list from CSV.
    Accepts either a 'Ticker' column or a 'Symbol' column.
    Returns a cleaned Python list of ticker strings.
    """
    df = pd.read_csv(filepath)

    print(f"Ticker file columns found: {df.columns.tolist()}")

    if "Ticker" in df.columns:
        tickers = df["Ticker"]
    elif "Symbol" in df.columns:
        tickers = df["Symbol"]
    else:
        raise ValueError(
            "Ticker file must contain either a 'Ticker' column or a 'Symbol' column."
        )

    tickers = (
        tickers.dropna()
        .astype(str)
        .str.strip()
        .str.replace(".", "-", regex=False)   # Yahoo/FMP-friendly format
        .tolist()
    )

    # remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            unique_tickers.append(t)

    print(f"Loaded {len(unique_tickers)} tickers.")
    return unique_tickers


# =====================================================
# STEP 2 - DOWNLOAD BULK DATA
# =====================================================

def get_json(session: requests.Session, url: str):
    """
    GET JSON with basic validation.
    Raises a clear error if the API returns non-200.
    """
    response = session.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def download_bulk_data(api_key: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Download bulk datasets from Financial Modeling Prep.
    Returns:
        profiles_df, ratios_df, income_df, balance_df, cashflow_df
    """
    session = requests.Session()

    # NOTE:
    # These endpoints are much faster than 500 x per-ticker calls.
    # Depending on your FMP plan, endpoint names / access may differ.
    # These are the standard bulk endpoints we are targeting.

    urls = {
        "profiles": f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}",
        "ratios": f"https://financialmodelingprep.com/api/v4/ratios-ttm-bulk?apikey={api_key}",
        "income": f"https://financialmodelingprep.com/api/v4/income-statement-bulk?year={REPORT_YEAR}&apikey={api_key}",
        "balance": f"https://financialmodelingprep.com/api/v4/balance-sheet-statement-bulk?year={REPORT_YEAR}&apikey={api_key}",
        "cashflow": f"https://financialmodelingprep.com/api/v4/cash-flow-statement-bulk?year={REPORT_YEAR}&apikey={api_key}",
    }

    print("Downloading company profiles...")
    profiles = get_json(session, urls["profiles"])

    print("Downloading TTM ratios...")
    ratios = get_json(session, urls["ratios"])

    print("Downloading income statements...")
    income = get_json(session, urls["income"])

    print("Downloading balance sheets...")
    balance = get_json(session, urls["balance"])

    print("Downloading cash flow statements...")
    cashflow = get_json(session, urls["cashflow"])

    profiles_df = pd.DataFrame(profiles)
    ratios_df = pd.DataFrame(ratios)
    income_df = pd.DataFrame(income)
    balance_df = pd.DataFrame(balance)
    cashflow_df = pd.DataFrame(cashflow)

    print("Bulk downloads completed.")
    print(f"Profiles rows: {len(profiles_df)}")
    print(f"Ratios rows: {len(ratios_df)}")
    print(f"Income rows: {len(income_df)}")
    print(f"Balance rows: {len(balance_df)}")
    print(f"Cashflow rows: {len(cashflow_df)}")

    return profiles_df, ratios_df, income_df, balance_df, cashflow_df


# =====================================================
# STEP 3 - STANDARDIZE COLUMN NAMES
# =====================================================

def standardize_bulk_frames(
    profiles_df: pd.DataFrame,
    ratios_df: pd.DataFrame,
    income_df: pd.DataFrame,
    balance_df: pd.DataFrame,
    cashflow_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Rename columns to a consistent schema used by the project.
    """

    # ---------- Profiles ----------
    # stock/list typically contains columns like:
    # symbol, name, price, exchange, exchangeShortName, type
    # It may NOT contain sector / industry / market cap / shares outstanding on some plans.
    # So we rename only what is commonly available and leave missing fields for later.
    profiles_rename = {
        "symbol": "Ticker",
        "name": "Company_Name",
        "price": "Current_Price",
        "exchange": "Exchange",
        "exchangeShortName": "Exchange_Short_Name",
        "type": "Asset_Type",
        "marketCap": "Market_Cap",
        "sharesOutstanding": "Shares_Outstanding",
        "sector": "Sector",
        "industry": "Industry",
        "beta": "Beta",
    }
    profiles_df = profiles_df.rename(columns=profiles_rename)

    # ---------- Ratios ----------
    ratios_rename = {
        "symbol": "Ticker",
        "peRatioTTM": "PE_Ratio",
        "priceToBookRatioTTM": "Price_to_Book",
        "priceToSalesRatioTTM": "Price_to_Sales",
        "enterpriseValueMultipleTTM": "EV_to_EBITDA",
        "returnOnEquityTTM": "ROE",
        "returnOnAssetsTTM": "ROA",
        "currentRatioTTM": "Current_Ratio",
        "debtEquityRatioTTM": "Debt_to_Equity",
        "grossProfitMarginTTM": "Gross_Margin",
        "operatingProfitMarginTTM": "Operating_Margin",
        "netProfitMarginTTM": "Net_Margin",
    }
    ratios_df = ratios_df.rename(columns=ratios_rename)

    # ---------- Income ----------
    income_rename = {
        "symbol": "Ticker",
        "date": "Report_Date",
        "calendarYear": "Calendar_Year",
        "revenue": "Revenue",
        "grossProfit": "Gross_Profit",
        "operatingIncome": "Operating_Income",
        "netIncome": "Net_Income",
        "eps": "EPS",
        "weightedAverageShsOutDil": "Weighted_Avg_Shares_Diluted",
    }
    income_df = income_df.rename(columns=income_rename)

    # ---------- Balance ----------
    balance_rename = {
        "symbol": "Ticker",
        "date": "Report_Date",
        "calendarYear": "Calendar_Year",
        "cashAndCashEquivalents": "Cash_And_Cash_Equivalents",
        "cashAndShortTermInvestments": "Cash_And_Short_Term_Investments",
        "totalCurrentAssets": "Total_Current_Assets",
        "totalAssets": "Total_Assets",
        "totalCurrentLiabilities": "Total_Current_Liabilities",
        "totalLiabilities": "Total_Liabilities",
        "shortTermDebt": "Short_Term_Debt",
        "longTermDebt": "Long_Term_Debt",
        "totalDebt": "Total_Debt",
        "netDebt": "Net_Debt",
        "totalStockholdersEquity": "Total_Equity",
    }
    balance_df = balance_df.rename(columns=balance_rename)

    # ---------- Cash Flow ----------
    cashflow_rename = {
        "symbol": "Ticker",
        "date": "Report_Date",
        "calendarYear": "Calendar_Year",
        "netCashProvidedByOperatingActivities": "Operating_Cash_Flow",
        "operatingCashFlow": "Operating_Cash_Flow",
        "capitalExpenditure": "Capital_Expenditure",
        "freeCashFlow": "Free_Cash_Flow",
    }
    cashflow_df = cashflow_df.rename(columns=cashflow_rename)

    return profiles_df, ratios_df, income_df, balance_df, cashflow_df


# =====================================================
# STEP 4 - FILTER TO S&P 500 TICKERS ONLY
# =====================================================

def filter_to_sp500(df: pd.DataFrame, ticker_set: set[str]) -> pd.DataFrame:
    """
    Keep only rows whose Ticker is in the S&P 500 ticker set.
    If the frame doesn't have a Ticker column, return empty frame.
    """
    if "Ticker" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["Ticker"] = df["Ticker"].astype(str).str.strip()
    return df[df["Ticker"].isin(ticker_set)]


# =====================================================
# STEP 5 - DEDUPLICATE TO ONE ROW PER TICKER
# =====================================================

def keep_latest_per_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Some bulk statement endpoints may return multiple rows per ticker.
    Keep the latest row per ticker based on Report_Date if available.
    """
    if df.empty or "Ticker" not in df.columns:
        return df

    df = df.copy()

    if "Report_Date" in df.columns:
        df["Report_Date"] = pd.to_datetime(df["Report_Date"], errors="coerce")
        df = df.sort_values(["Ticker", "Report_Date"], ascending=[True, False])

    df = df.drop_duplicates(subset=["Ticker"], keep="first")
    return df


# =====================================================
# STEP 6 - BUILD MASTER FUNDAMENTALS TABLE
# =====================================================

def build_fundamentals(
    ticker_list: list[str],
    profiles_df: pd.DataFrame,
    ratios_df: pd.DataFrame,
    income_df: pd.DataFrame,
    balance_df: pd.DataFrame,
    cashflow_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge all cleaned frames into one master fundamentals table.
    Always starts from the ticker list so every S&P 500 ticker remains visible,
    even if some fields are missing.
    """

    base = pd.DataFrame({"Ticker": ticker_list})

    # Select only columns that actually exist to avoid KeyErrors
    def safe_select(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        existing = [c for c in columns if c in df.columns]
        return df[existing].copy()

    profiles_df = safe_select(profiles_df, [
        "Ticker", "Company_Name", "Sector", "Industry",
        "Current_Price", "Market_Cap", "Shares_Outstanding",
        "Beta", "Exchange", "Exchange_Short_Name", "Asset_Type"
    ])

    ratios_df = safe_select(ratios_df, [
        "Ticker", "PE_Ratio", "Price_to_Book", "Price_to_Sales", "EV_to_EBITDA",
        "ROE", "ROA", "Current_Ratio", "Debt_to_Equity",
        "Gross_Margin", "Operating_Margin", "Net_Margin"
    ])

    income_df = safe_select(income_df, [
        "Ticker", "Report_Date", "Calendar_Year", "Revenue", "Gross_Profit",
        "Operating_Income", "Net_Income", "EPS", "Weighted_Avg_Shares_Diluted"
    ])

    balance_df = safe_select(balance_df, [
        "Ticker", "Cash_And_Cash_Equivalents", "Cash_And_Short_Term_Investments",
        "Total_Current_Assets", "Total_Assets", "Total_Current_Liabilities",
        "Total_Liabilities", "Short_Term_Debt", "Long_Term_Debt",
        "Total_Debt", "Net_Debt", "Total_Equity"
    ])

    cashflow_df = safe_select(cashflow_df, [
        "Ticker", "Operating_Cash_Flow", "Capital_Expenditure", "Free_Cash_Flow"
    ])

    fundamentals = (
        base
        .merge(profiles_df, on="Ticker", how="left")
        .merge(ratios_df, on="Ticker", how="left")
        .merge(income_df, on="Ticker", how="left")
        .merge(balance_df, on="Ticker", how="left")
        .merge(cashflow_df, on="Ticker", how="left")
    )

    # ---------- Derived fields useful for DCF / Reverse DCF ----------
    # Prefer Cash_And_Short_Term_Investments; fallback to Cash_And_Cash_Equivalents
    if "Cash_And_Short_Term_Investments" not in fundamentals.columns:
        fundamentals["Cash_And_Short_Term_Investments"] = pd.NA

    if "Cash_And_Cash_Equivalents" not in fundamentals.columns:
        fundamentals["Cash_And_Cash_Equivalents"] = pd.NA

    fundamentals["Cash_For_Valuation"] = fundamentals["Cash_And_Short_Term_Investments"].fillna(
        fundamentals["Cash_And_Cash_Equivalents"]
    )

    # FCF Margin = Free Cash Flow / Revenue
    if "Free_Cash_Flow" in fundamentals.columns and "Revenue" in fundamentals.columns:
        fundamentals["FCF_Margin"] = fundamentals["Free_Cash_Flow"] / fundamentals["Revenue"]
    else:
        fundamentals["FCF_Margin"] = pd.NA

    # Net Cash / (Net Debt) sanity helper
    if "Cash_For_Valuation" in fundamentals.columns and "Total_Debt" in fundamentals.columns:
        fundamentals["Cash_minus_Debt"] = fundamentals["Cash_For_Valuation"] - fundamentals["Total_Debt"]
    else:
        fundamentals["Cash_minus_Debt"] = pd.NA

    # Reorder columns into a cleaner layout
    preferred_order = [
        # Identifier
        "Ticker", "Company_Name", "Sector", "Industry",

        # Market / valuation
        "Current_Price", "Market_Cap", "Shares_Outstanding", "Weighted_Avg_Shares_Diluted",
        "PE_Ratio", "Price_to_Book", "Price_to_Sales", "EV_to_EBITDA", "Beta",

        # Profitability / quality
        "ROE", "ROA", "Gross_Margin", "Operating_Margin", "Net_Margin", "Current_Ratio", "Debt_to_Equity",

        # Income statement
        "Report_Date", "Calendar_Year", "Revenue", "Gross_Profit", "Operating_Income", "Net_Income", "EPS",

        # Cash flow
        "Operating_Cash_Flow", "Capital_Expenditure", "Free_Cash_Flow", "FCF_Margin",

        # Balance sheet
        "Cash_And_Cash_Equivalents", "Cash_And_Short_Term_Investments", "Cash_For_Valuation",
        "Total_Current_Assets", "Total_Assets", "Total_Current_Liabilities", "Total_Liabilities",
        "Short_Term_Debt", "Long_Term_Debt", "Total_Debt", "Net_Debt", "Cash_minus_Debt", "Total_Equity",

        # Misc
        "Exchange", "Exchange_Short_Name", "Asset_Type",
    ]

    existing_cols = [c for c in preferred_order if c in fundamentals.columns]
    remaining_cols = [c for c in fundamentals.columns if c not in existing_cols]
    fundamentals = fundamentals[existing_cols + remaining_cols]

    return fundamentals


# =====================================================
# STEP 7 - BUILD DCF INPUT TABLE
# =====================================================

def build_dcf_inputs(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """
    Create a smaller DCF / Reverse DCF input table.
    """
    dcf_columns = [
        "Ticker",
        "Company_Name",
        "Current_Price",
        "Market_Cap",
        "Shares_Outstanding",
        "Weighted_Avg_Shares_Diluted",
        "Revenue",
        "Operating_Income",
        "Net_Income",
        "Operating_Cash_Flow",
        "Free_Cash_Flow",
        "Cash_For_Valuation",
        "Total_Debt",
        "Net_Debt",
        "ROE",
        "ROA",
        "Operating_Margin",
        "Net_Margin",
        "Debt_to_Equity",
        "PE_Ratio",
        "Price_to_Book",
        "FCF_Margin",
    ]

    existing = [c for c in dcf_columns if c in fundamentals.columns]
    dcf_df = fundamentals[existing].copy()

    # If Shares_Outstanding is missing but diluted weighted average shares exists,
    # use that as a fallback for valuation work.
    if "Shares_Outstanding" in dcf_df.columns and "Weighted_Avg_Shares_Diluted" in dcf_df.columns:
        dcf_df["Shares_For_Valuation"] = dcf_df["Shares_Outstanding"].fillna(
            dcf_df["Weighted_Avg_Shares_Diluted"]
        )
    elif "Shares_Outstanding" in dcf_df.columns:
        dcf_df["Shares_For_Valuation"] = dcf_df["Shares_Outstanding"]
    elif "Weighted_Avg_Shares_Diluted" in dcf_df.columns:
        dcf_df["Shares_For_Valuation"] = dcf_df["Weighted_Avg_Shares_Diluted"]
    else:
        dcf_df["Shares_For_Valuation"] = pd.NA

    return dcf_df


# =====================================================
# STEP 8 - IDENTIFY FAILED / INCOMPLETE TICKERS
# =====================================================

def build_failed_tickers(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """
    Flag tickers that are missing key DCF fields.
    This does NOT mean the API call failed; it means the final dataset is not
    complete enough for valuation work.
    """
    required_cols = [
        "Current_Price",
        "Market_Cap",
        "Revenue",
        "Free_Cash_Flow",
        "Total_Debt",
    ]

    # Make sure all required columns exist before checking
    for col in required_cols:
        if col not in fundamentals.columns:
            fundamentals[col] = pd.NA

    missing_mask = fundamentals[required_cols].isna().any(axis=1)

    failed = fundamentals.loc[missing_mask, ["Ticker", "Company_Name"] + required_cols].copy()
    failed["Missing_Count"] = failed[required_cols].isna().sum(axis=1)

    return failed.sort_values("Missing_Count", ascending=False)


# =====================================================
# MAIN
# =====================================================

def main():
    # 1) Load S&P 500 tickers
    ticker_list = load_tickers(TICKER_FILE)
    ticker_set = set(ticker_list)

    # 2) Download bulk datasets
    profiles_df, ratios_df, income_df, balance_df, cashflow_df = download_bulk_data(API_KEY)

    # 3) Standardize columns
    profiles_df, ratios_df, income_df, balance_df, cashflow_df = standardize_bulk_frames(
        profiles_df, ratios_df, income_df, balance_df, cashflow_df
    )

    # 4) Filter to S&P 500 only
    profiles_df = filter_to_sp500(profiles_df, ticker_set)
    ratios_df = filter_to_sp500(ratios_df, ticker_set)
    income_df = filter_to_sp500(income_df, ticker_set)
    balance_df = filter_to_sp500(balance_df, ticker_set)
    cashflow_df = filter_to_sp500(cashflow_df, ticker_set)

    print(f"S&P 500 filtered profiles rows: {len(profiles_df)}")
    print(f"S&P 500 filtered ratios rows: {len(ratios_df)}")
    print(f"S&P 500 filtered income rows: {len(income_df)}")
    print(f"S&P 500 filtered balance rows: {len(balance_df)}")
    print(f"S&P 500 filtered cashflow rows: {len(cashflow_df)}")

    # 5) Deduplicate statement tables to one row per ticker
    profiles_df = keep_latest_per_ticker(profiles_df)
    ratios_df = keep_latest_per_ticker(ratios_df)
    income_df = keep_latest_per_ticker(income_df)
    balance_df = keep_latest_per_ticker(balance_df)
    cashflow_df = keep_latest_per_ticker(cashflow_df)

    # 6) Build master fundamentals table
    fundamentals = build_fundamentals(
        ticker_list,
        profiles_df,
        ratios_df,
        income_df,
        balance_df,
        cashflow_df
    )

    # 7) Build DCF-ready subset
    dcf_df = build_dcf_inputs(fundamentals)

    # 8) Build failed / incomplete ticker report
    failed_df = build_failed_tickers(fundamentals)

    # 9) Save outputs
    fundamentals.to_csv(OUTPUT_FUNDAMENTALS, index=False)
    dcf_df.to_csv(OUTPUT_DCF, index=False)
    failed_df.to_csv(OUTPUT_FAILED, index=False)

    print("\n========================================")
    print("Pipeline finished successfully.")
    print(f"Saved: {OUTPUT_FUNDAMENTALS} ({len(fundamentals)} rows)")
    print(f"Saved: {OUTPUT_DCF} ({len(dcf_df)} rows)")
    print(f"Saved: {OUTPUT_FAILED} ({len(failed_df)} rows)")
    print("========================================")


if __name__ == "__main__":
    main()