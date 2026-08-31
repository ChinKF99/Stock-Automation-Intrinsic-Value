"""
============================================================
17_build_standard_dcf_intrinsic_value.py

Build gold table Standard DCF Intrinsic Value using data from
from gold table.

Source
------
16_build_dcf_assumptions.py

Target:
    gold.build_standard_dcf_intrinsic_value
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
    GOLD_17_TABLE,
    GOLD_17_SCHEMA_TABLE,
    STANDARD_DCF_INTRINSIC_VALUE_COLUMNS,
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
    calculate_dcf_enterprise_value,
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
TARGET_TABLE = GOLD_17_TABLE
TARGET_SCHEMA_TABLE = GOLD_17_SCHEMA_TABLE

# ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Building Gold INTRINSIC VALUATON (STANDARD DCF)")
    logger.info("=" * 60)

    engine = get_sqlalchemy_engine()
    print_connection_info(engine)

    ensure_schema(
    engine=engine,
    schema=TARGET_SCHEMA,)

    assumptions = load_table(GOLD_16_SCHEMA_TABLE,engine)
    
    results = []

    for _, row in assumptions.iterrows():


        # ============================================================
        # Sensitivity Analysis purposes

        # row["discount_rate"] = (
        #     0.08
        #     if row["symbol"] == "AAPL"
        #     else row["discount_rate"])
        # ============================================================

        dcf = calculate_dcf_enterprise_value(
            starting_fcf=row["starting_fcf"],
            growth_rate=row["historical_growth_rate"],
            discount_rate=row["discount_rate"],
            terminal_growth=row["terminal_growth"],
            projection_years=int(row["projection_years"])
        )

        enterprise_value = dcf["enterprise_value"]

        equity_value = calculate_equity_value(
            enterprise_value,
            row["net_debt"]
        )

        intrinsic_value = calculate_intrinsic_value(
            equity_value,
            row["weighted_average_shs_out"]
        )

        margin_of_safety = calculate_margin_of_safety(
            intrinsic_value,
            row["price"]
        )

        results.append({
            "symbol": row["symbol"],
            "calendar_year": row["calendar_year"],
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "intrinsic_value": intrinsic_value,
            "current_price": row["price"],
            "margin_of_safety": margin_of_safety
        })

        # ============================================================
        # Sensitivity Analysis purposes

        # if row["symbol"] == "AAPL":

        #     print("\n" + "=" * 80)
        #     print("AAPL STANDARD DCF AUDIT")
        #     print("=" * 80)

        #     print(f"\nCurrent Price           : {row['price']:,.2f}")
        #     print(f"Market Cap              : {row['market_cap']:,.0f}")
        #     print(f"Net Debt                : {row['net_debt']:,.0f}")

        #     market_ev = row["market_cap"] + row["net_debt"]

        #     print(f"Market Enterprise Value : {market_ev:,.0f}")

        #     print("\nAssumptions")
        #     print("-" * 40)
            
        #     print(f"Starting FCF            : {row['starting_fcf']:,.0f}")
        #     print(f"Historical Growth       : {row['historical_growth_rate']:.2%}")
        #     print(f"Discount Rate           : {row['discount_rate']:.2%}")
        #     print(f"Terminal Growth         : {row['terminal_growth']:.2%}")
        #     print(f"Projection Years        : {int(row['projection_years'])}")

        #     print("\nForecast Cash Flows")
        #     print("-" * 40)

        #     for i, fcf in enumerate(cashflows, start=1):
        #         print(f"Year {i:2d}: {fcf:,.0f}")

        #     print("\nDiscounted Cash Flows")
        #     print("-" * 40)

        #     for i, pv in enumerate(discounted_cash_flow, start=1):
        #         print(f"Year {i:2d}: {pv:,.0f}")

        #     forecast_total = sum(discounted_cash_flow)

        #     print("\nSummary")
        #     print("-" * 40)

        #     print(f"PV Forecast Cash Flows  : {forecast_total:,.0f}")
        #     print(f"Terminal Value          : {terminal_value:,.0f}")
        #     print(f"Discounted Terminal     : {discounted_terminal:,.0f}")
        #     print(f"Enterprise Value (DCF)  : {enterprise_value:,.0f}")
        #     print(f"Equity Value            : {equity_value:,.0f}")
        #     print(f"Intrinsic Value         : {intrinsic_value:,.2f}")
        #     print(f"Margin of Safety        : {margin_of_safety:.2%}")

        #     print("\nComparison")
        #     print("-" * 40)

        #     print(f"Market EV              : {market_ev:,.0f}")
        #     print(f"DCF EV                 : {enterprise_value:,.0f}")
        #     print(f"Difference             : {market_ev - enterprise_value:,.0f}")

        #     forecast_weight = forecast_total / enterprise_value
        #     terminal_weight = discounted_terminal / enterprise_value

        #     print("\nContribution")
        #     print("-" * 40)

        #     print(f"Forecast Contribution  : {forecast_weight:.2%}")
        #     print(f"Terminal Contribution  : {terminal_weight:.2%}")

        #     print("=" * 80)
        # ============================================================

    standard_dcf_df = pd.DataFrame(results).round(4)

    validate_columns(standard_dcf_df, STANDARD_DCF_INTRINSIC_VALUE_COLUMNS)
    validate_primary_key(standard_dcf_df,["symbol"])
    validate_nulls(standard_dcf_df,["symbol", "margin_of_safety"])
    validate_row_count(standard_dcf_df)

    load_dataframe_to_sql(engine, standard_dcf_df, TARGET_SCHEMA, TARGET_TABLE)
    
    get_row_count(engine, TARGET_SCHEMA, TARGET_TABLE)
    
if __name__ == "__main__":
    main()