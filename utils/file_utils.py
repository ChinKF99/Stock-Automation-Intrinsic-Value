#=====================================
# Common file helper functions
#=====================================

import json
from pathlib import Path
import pandas as pd


def read_csv(file_path: Path) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.
    """
    return pd.read_csv(file_path)


def save_csv(df: pd.DataFrame, file_path: Path):
    """
    Save DataFrame as CSV.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8"
    )


def save_json(data, file_path: Path):
    """
    Save JSON to disk.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4
        )


def read_json(file_path: Path):

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)
    

def json_exists(folder: Path, ticker: str) -> bool:

    return (folder / f"{ticker}.json").exists()