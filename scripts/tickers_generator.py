import pandas as pd

try:
    print("Downloading tickers dataset")

    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"

    sp500 = pd.read_csv(url)

    tickers = sp500["Symbol"].tolist()

    pd.DataFrame({
        "Ticker": tickers
    }).to_csv("sp500_tickers.csv", index=False)

    print(f"Downloaded {len(tickers)} tickers.") 

except Exception as e:

    print(f"Download failed: {e}")

    tickers = pd.read_csv("sp500_tickers.csv")["Ticker"].tolist()

    print("Using local ticker file.")