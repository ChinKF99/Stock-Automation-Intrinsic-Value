import csv
import io
import os
import pandas as pd
import requests

try:
    print("Extracting S&P 500 tickers from alternative free source (Wikipedia)...")
    
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Use 'match' to isolate the specific component table explicitly
    html_stream = io.StringIO(response.text)
    tables = pd.read_html(html_stream, match="Symbol")
    df = tables[0]
    
    # Isolate tickers and replace dots with hyphens (e.g., BRK.B to BRK-B)
    sp500_tickers = df["Symbol"].str.replace('.', '-', regex=False).tolist()
    
    # Target output file layout
    output_file = "sp500_tickers.csv"
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ticker"])  # Set header
        for ticker in sp500_tickers:
            writer.writerow([ticker])
            
    print(f"\nSuccess! Found {len(sp500_tickers)} S&P 500 tickers.")
    print(f"Saved CSV file to: {os.path.abspath(output_file)}")

except Exception as e:
    print(f"\nAn unexpected script error occurred: {e}")
