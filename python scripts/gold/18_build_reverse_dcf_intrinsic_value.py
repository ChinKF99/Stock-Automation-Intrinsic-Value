"""
============================================================
18_build_reverse_dcf_intrinsic_value.py

Build gold table reverse DCF Intrinsic Value using data from
from gold table.

Source
------
16_build_dcf_assumptions.py

Target:
    gold.build_reverse_dcf_intrinsic_value
============================================================
"""

from pathlib import Path
import sys
import pandas as pd

# ==========================================================
# Make project root importable
# ==========================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Project Imports
# ==========================================================

from config.config import (
    get_sqlalchemy_engine
)

from utils.sql_utils import (
    GOLD_SCHEMA,
    GOLD_16_SCHEMA_TABLE,
    GOLD_18_TABLE,
    GOLD_18_SCHEMA_TABLE,
    INTRINSIC_VALUE_COLUMNS,
    print_connection_info,
    ensure_schema,
    get_row_count,
    load_dataframe_to_sql,
    load_table,
    )

from utils.validation_utils import(
    validate_primary_key,
    validate_columns,
    validate_nulls,
    validate_row_count
)

from utils.dcf_utils import(
    forecast_cashflows,
    discount_cash_flows,
    calculate_terminal_value,
    discount_terminal_value,
    calculate_enterprise_value,
    calculate_equity_value,
    calculate_intrinsic_value,
    calculate_margin_of_safety
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = GOLD_SCHEMA
TARGET_TABLE = GOLD_18_TABLE
TARGET_SCHEMA_TABLE = GOLD_18_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():