"""
============================================================
20_build_investment_dashboard.py

Create a final Gold table for Power BI.

Source

gold.build_dcf_assumptions
gold.build_standard_dcf_intrinsic_value
gold.build_reverse_dcf_intrinsic_value
gold.build_dcf_scenarios

Target

gold.investment_dashboard
============================================================
"""

from pathlib import Path
import sys

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

from config.config import get_sqlalchemy_engine

from utils.sql_utils import (
    BRONZE_04_SCHEMA_TABLE,
    GOLD_SCHEMA,
    GOLD_20_TABLE,
    GOLD_16_SCHEMA_TABLE,
    GOLD_17_SCHEMA_TABLE,
    GOLD_18_SCHEMA_TABLE,
    GOLD_19_SCHEMA_TABLE,
    GOLD_20_SCHEMA_TABLE,
    load_table,
    load_dataframe_to_sql,
    ensure_schema,
    print_connection_info,
    get_row_count
)

from utils.validation_utils import(
    validate_primary_key,
    validate_nulls,
    validate_row_count
)

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

# ============================================================
# Variables for File Path & Schema, Tables
# ============================================================

TARGET_SCHEMA = GOLD_SCHEMA
TARGET_TABLE = GOLD_20_TABLE
TARGET_SCHEMA_TABLE = GOLD_20_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():
    logger.info("=" * 60)
    logger.info("Building Gold INVESTMENT DASHBOARD")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    company_profile = load_table(BRONZE_04_SCHEMA_TABLE, engine)

    assumptions = load_table(GOLD_16_SCHEMA_TABLE, engine)
    standard = load_table(GOLD_17_SCHEMA_TABLE, engine)
    reverse = load_table(GOLD_18_SCHEMA_TABLE, engine)
    scenario = load_table(GOLD_19_SCHEMA_TABLE, engine)


    company_profile = company_profile[
    [
        "symbol",
        "company_name",
        "sector",
        "industry"
    ]]

    assumptions = assumptions[
    [
        "symbol",
        "calendar_year",
        "price",
        "market_cap"
    ]]

    standard = standard[
    [
        "symbol",
        "intrinsic_value",
        "margin_of_safety"
    ]]

    reverse = reverse[
    [
        "symbol",
        "historical_growth_rate",
        "implied_growth_rate",
        "growth_premium",
        "valuation_status"
    ]]

    scenario = scenario[
    [
        "symbol",
        "bear_intrinsic_value",
        "base_intrinsic_value",
        "bull_intrinsic_value"
    ]]

    dashboard = company_profile.merge(
        assumptions,
        on="symbol",
        how="left"
    )

    dashboard = dashboard.merge(
    standard,
    on="symbol",
    how="left"
    )

    dashboard = dashboard.merge(
        reverse,
        on="symbol",
        how="left"
    )

    dashboard = dashboard.merge(
        scenario,
        on="symbol",
        how="left"
    )

    dashboard.rename(columns={
    "price":"current_price",
    "intrinsic_value":"base_intrinsic_value_standard"}, inplace=True)

   # Add derived columns that is useful 

    dashboard["valuation_difference"] = (
    dashboard["base_intrinsic_value_standard"]
    - dashboard["current_price"]
    )

    dashboard["upside_percent"] = (
        dashboard["valuation_difference"]
        / dashboard["current_price"]
    )

    dashboard["market_expectation_gap"] = (
        dashboard["implied_growth_rate"]
        - dashboard["historical_growth_rate"]
    )

    dashboard["is_undervalued"] = (
        dashboard["base_intrinsic_value_standard"]
        > dashboard["current_price"]
    )

    dashboard = dashboard.sort_values("symbol")

    validate_primary_key(dashboard,["symbol"])
    validate_nulls(dashboard,["symbol"])
    validate_row_count(dashboard)

    load_dataframe_to_sql(engine, dashboard, TARGET_SCHEMA, TARGET_TABLE)
    
    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)

if __name__ == "__main__":
    main()