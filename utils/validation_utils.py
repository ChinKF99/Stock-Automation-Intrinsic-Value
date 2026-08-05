"""
============================================================
Validaton Function for dataframe before merging/appending
dataframe to SQL.
============================================================
"""

import os
import sys
from config.logging_config import setup_logger
from pathlib import Path


from config.logging_config import setup_logger
# 1. Get the base name (e.g., "script.py")
raw_name = os.path.basename(sys.argv[0])

# 2. Separate name from extension and add .log (e.g., "script.log")
log_name = os.path.splitext(raw_name)[0]

# 3. Initialize the logger
logger = setup_logger(log_name)



# ==========================================================
# Primary Key Validation
# ==========================================================

def validate_primary_key(df, key_columns):
    """
    Validate that the primary key columns are unique.

    Raises
    ------
    ValueError
        If duplicate keys are found.
    """

    duplicates = df.duplicated(subset=key_columns,keep=False)

    duplicate_count = duplicates.sum()

    if duplicate_count > 0:
        logger.error(
            "Found %s duplicate rows on primary key %s",duplicate_count,key_columns)
        
        logger.error("\n%s",df.loc[duplicates, key_columns])

        raise ValueError(f"Duplicate primary key detected: {key_columns}")

    logger.info("Primary key validation passed.")

# ==========================================================
# NUll Validation
# ==========================================================

def validate_nulls(df, required_columns):
    """
    Validate required columns contain no NULL values.
    """

    failed = False
    for column in required_columns:

        null_count = df[column].isna().sum()

        if null_count > 0:

            logger.warning(
                "%s contains %s NULL values",
                column,
                null_count)

            failed = True

    if failed:

        raise ValueError("NULL validation failed.")

    logger.info("NULL validation passed.")

# ==========================================================
# Row Count Validation
# ==========================================================

def validate_row_count(df):

    if len(df) == 0:

        raise ValueError("DataFrame contains zero rows.")

    logger.info(
        "Row count validation passed (%s rows).",len(df))

# ==========================================================
# Column Validation
# ==========================================================

def validate_columns(df, expected_columns):
    """
    Ensure expected columns exist.
    """

    missing = set(expected_columns) - set(df.columns)
    unexpected = set(df.columns) - set(expected_columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if unexpected:
        raise ValueError(f"Unexpected columns: {sorted(unexpected)}")

    logger.info("Column validation passed.")
