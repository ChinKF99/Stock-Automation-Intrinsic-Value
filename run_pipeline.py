from pathlib import Path
import subprocess
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent

from config.logging_config import setup_logger

logger = setup_logger(Path(__file__).stem)

PIPELINE = [
    
    # ---------------- Bronze ----------------
    ("Bronze Company Profile",
     "python scripts/bronze/03_download_company_profile.py"),

    ("Bronze Load Profile",
     "python scripts/bronze/04_load_company_profile_sql.py"),

    ("Bronze Income Statement",
     "python scripts/bronze/05_download_income_statement.py"),

    ("Bronze Load Income",
     "python scripts/bronze/06_load_income_statement_sql.py"),

    ("Bronze Balance Sheet",
     "python scripts/bronze/07_download_balance_sheet.py"),

    ("Bronze Load Balance",
     "python scripts/bronze/08_load_balance_sheet_sql.py"),

    ("Bronze Cash Flow",
     "python scripts/bronze/09_download_cash_flow.py"),

    ("Bronze Load Cash Flow",
     "python scripts/bronze/10_load_cash_flow_sql.py"),

    ("Bronze Ratios",
     "python scripts/bronze/11_download_ratios.py"),

    ("Bronze Load Ratios",
     "python scripts/bronze/12_load_ratios_sql.py"),

    # ---------------- Silver ----------------
    ("Silver Financials",
     "python scripts/silver/13_build_company_financials.py"),

    ("Silver Growth",
     "python scripts/silver/14_build_company_growth_metrics.py"),

    ("Silver Ratios",
     "python scripts/silver/15_build_company_financial_ratios.py"),

    # ---------------- Gold ----------------
    ("Gold DCF Assumptions",
     "python scripts/gold/16_build_dcf_assumptions.py"),

    ("Gold Standard DCF",
     "python scripts/gold/17_build_standard_dcf_intrinsic_value.py"),

    ("Gold Reverse DCF",
     "python scripts/gold/18_build_reverse_dcf_intrinsic_value.py"),

    ("Gold Scenario",
     "python scripts/gold/19_build_scenario_analysis.py"),

    ("Gold Dashboard",
     "python scripts/gold/20_build_investment_dashboard.py"),
]

results = []

pipeline_start = time.perf_counter()

for name, script in PIPELINE:

    script_path = PROJECT_ROOT / script

    logger.info("=" * 70)
    logger.info(f"Running {name}")
    logger.info("=" * 70)

    if not script_path.exists():
        logger.error(f"File not found : {script_path}")
        break

    start = time.perf_counter()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT
    )

    elapsed = time.perf_counter() - start

    if result.returncode == 0:
        results.append((name, elapsed, True))
    else:
        results.append((name, elapsed, False))
        logger.error(f"{name} FAILED")
        break

pipeline_time = time.perf_counter() - pipeline_start

print()
logger.info("=" * 60)
logger.info("PIPELINE SUMMARY")
logger.info("=" * 60)

for name, elapsed, success in results:

    status = "✔" if success else "✘"

    logger.info(f"{name:<28} {status} {elapsed:>6.1f} sec")

print()
logger.info(f"Pipeline Completed")
logger.info(f"Total Runtime : {pipeline_time:.1f} sec")
logger.info("=" * 60)