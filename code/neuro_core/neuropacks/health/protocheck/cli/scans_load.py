# neuro_core/neuropacks/health/protocheck/cli/scans_load.py

import argparse
from pathlib import Path
from ..ingesters.scans import load_scans_index, upsert_scans
from ..core.logger import get_logger

LOGGER = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Load scanned documents index into DB.")
    parser.add_argument("--csv", required=True, help="Path to scans index CSV file")

    args = parser.parse_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        LOGGER.error("Provided CSV file does not exist: %s", csv_path)
        return

    try:
        df = load_scans_index(str(csv_path))
        upsert_scans(df)
    except Exception as e:
        LOGGER.exception("Failed to load scans index: %s", e)


if __name__ == "__main__":
    main()
