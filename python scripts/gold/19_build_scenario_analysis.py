"""
============================================================
19_build_scenario_analysis.py

Build gold table scenario analysis

Source
------
17_build_standard_dcf_intrinsic_value.py

Target:
    gold.scenario_analysis
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
    GOLD_19_TABLE,
    GOLD_19_SCHEMA_TABLE,
    SCENARIO_ANALYSIS_COLUMNS,
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
    run_dcf_scenario
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = GOLD_SCHEMA
TARGET_TABLE = GOLD_19_TABLE
TARGET_SCHEMA_TABLE = GOLD_19_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Gold SCENARIO ANALYSIS")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    assumptions = load_table(GOLD_16_SCHEMA_TABLE,engine)

    results = []

    for _, row in assumptions.iterrows():

        bear = run_dcf_scenario(
            row,
            growth_adjustment=-0.02,
            discount_adjustment=0.01
            )

        base = run_dcf_scenario(row)

        bull = run_dcf_scenario(
            row,
            growth_adjustment=0.02,
            discount_adjustment=-0.01
            )

        if row["starting_fcf"] <= 0:
            results.append({
                "symbol": row["symbol"],
                "calendar_year": row["calendar_year"],
                "current_price": row["price"],
                "bear_intrinsic_value":0,
                "base_intrinsic_value":0,
                "bull_intrinsic_value":0,
                "bear_margin_of_safety":0,
                "base_margin_of_safety":0,
                "bull_margin_of_safety":0,
                "valuation_status": "Negative FCF"
            })

            continue
        
        results.append({
            "symbol": row["symbol"],
            "calendar_year": row["calendar_year"],
            "current_price": row["price"],
            "bear_intrinsic_value":
                bear["intrinsic_value"],
            "base_intrinsic_value":
                base["intrinsic_value"],
            "bull_intrinsic_value":
                bull["intrinsic_value"],
            "bear_margin_of_safety":
                bear["margin_of_safety"],
            "base_margin_of_safety":
                base["margin_of_safety"],
            "bull_margin_of_safety":
                bull["margin_of_safety"],
            "valuation_status": "Completed"
        })

    scenario_df = pd.DataFrame(results).round(4)
        
    validate_columns(scenario_df, SCENARIO_ANALYSIS_COLUMNS)
    validate_primary_key(scenario_df,["symbol"])
    validate_nulls(scenario_df,["symbol", "bear_intrinsic_value", "base_intrinsic_value", "bull_intrinsic_value",])
    validate_row_count(scenario_df)

    load_dataframe_to_sql(engine, scenario_df, TARGET_SCHEMA, TARGET_TABLE)
    
    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)
        
if __name__ == "__main__":
    main()