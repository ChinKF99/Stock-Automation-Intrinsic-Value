from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

PIPELINE = [
    
    # Bronze
    "python scripts/bronze/01_download_sp500_tickers.py",
    "python scripts/bronze/02_load_sp500_sql.py",
    "python scripts/bronze/03_download_company_profile.py",
    "python scripts/bronze/04_load_company_profile_sql.py",
    "python scripts/bronze/05_download_income_statement.py",
    "python scripts/bronze/06_load_income_statement_sql.py",
    "python scripts/bronze/07_download_balance_sheet.py",
    "python scripts/bronze/08_load_balance_sheet_sql.py",
    "python scripts/bronze/09_download_cash_flow.py",
    "python scripts/bronze/10_load_cash_flow_sql.py",
    "python scripts/bronze/11_download_ratios.py",
    "python scripts/bronze/12_load_ratios_sql.py",

    # Silver
    "python scripts/silver/13_build_company_financials.py",
    "python scripts/silver/14_build_company_growth_metrics.py",
    "python scripts/silver/15_build_company_financial_ratios.py",

    # Gold
    "python scripts/gold/16_build_dcf_assumptions.py",
    "python scripts/gold/17_build_standard_dcf_intrinsic_value.py",
    "python scripts/gold/18_build_reverse_dcf_intrinsic_value.py",
    "python scripts/gold/19_build_scenario_analysis.py",
    "python scripts/gold/20_build_investment_dashboard.py"

]

for script in PIPELINE:

    script_path = PROJECT_ROOT / script

    logger.info("=" * 70)
    logger.info(f"Running {script_path.name}")
    logger.info("=" * 70)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        logger.info(f"FAILED : {script_path.name}")
        break

logger.info("=" * 70)
logger.info("Pipeline Finished")
logger.info("=" * 70)