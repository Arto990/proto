import argparse
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE
from neuro_core.neuropacks.health.protocheck.checks.feature1_lab_no_billing import run_feature1_lab_no_billing
from neuro_core.neuropacks.health.protocheck.core.logger import logger


def main():
    parser = argparse.ArgumentParser(description="Run Feature 1: Lab Sheet without Billing Check")
    parser.add_argument("--start", required=True, help="Start date in YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date in YYYY-MM-DD")
    parser.add_argument("--out", required=True, help="Output CSV path")

    args = parser.parse_args()
    start_date = datetime.strptime(args.start, "%Y-%m-%d").date()
    end_date = datetime.strptime(args.end, "%Y-%m-%d").date()
    output_path = Path(args.out)

    logger.info(f"Running Feature 1 from {start_date} to {end_date}")

    try:
        conn = sqlite3.connect(DB_FILE)
        df_results = run_feature1_lab_no_billing(conn, start_date, end_date)
        df_results.to_csv(output_path, index=False)
        logger.info(f"Results written to {output_path}")
    except Exception as e:
        logger.exception("Failed to run Feature 1 check")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
