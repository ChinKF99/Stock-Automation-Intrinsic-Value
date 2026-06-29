from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import text

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import get_sqlalchemy_engine

CSV_FILE = PROJECT_ROOT / "data" / "bronze" / "sp500_tickers.csv"


def main():

    print("Reading CSV...")

    df = pd.read_csv(CSV_FILE)

    print(df.head())

    engine = get_sqlalchemy_engine()

    insert_sql = text("""
        INSERT INTO bronze.sp500_tickers
        (
            ticker,
            company_name,
            source,
            load_date,
            load_ts
        )
        VALUES
        (
            :ticker,
            :company_name,
            :source,
            :load_date,
            :load_ts
        )
    """)

    with engine.begin() as conn:

        conn.execute(text("DELETE FROM bronze.sp500_tickers"))

        batch_size = 100

        records = df.to_dict("records")

        total = len(records)

        for i in range(0, total, batch_size):

            batch = records[i:i+batch_size]

            conn.execute(insert_sql, batch)

            print(f"Inserted {min(i+batch_size,total)} / {total}")

    print("Finished loading.")


if __name__ == "__main__":
    main()