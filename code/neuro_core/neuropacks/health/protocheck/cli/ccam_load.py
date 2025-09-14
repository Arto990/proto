# neuro_core/neuropacks/health/protocheck/cli/ccam_load.py

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from neuro_core.neuropacks.health.protocheck.core.logger import get_logger
from neuro_core.neuropacks.health.protocheck.core.schema import init_db
from neuro_core.neuropacks.health.protocheck.core.constants import DB_PATH
from neuro_core.neuropacks.health.protocheck.core.adapters.azzem_ccam import (
    AzzemCcamAdapter,
)
from neuro_core.neuropacks.health.protocheck.ingesters.ccam import (
    load_ccam_from_docx,
    load_ccam_from_csv,
    load_ccam_from_txt,
    upsert_ccam,
)

LOGGER = get_logger(__name__)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Load CCAM prosthetic reference into ProtoCheck DB"
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--docx", type=str, help="Path to CCAM reference .docx file")
    src.add_argument("--csv", type=str, help="Path to CCAM reference .csv file")
    src.add_argument("--txt", type=str, help="Path to CCAM reference .txt file")
    parser.add_argument(
        "--txt-delimiter",
        type=str,
        default=";",
        help="Delimiter for TXT (default ';')",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(DB_PATH),
        help="SQLite DB path (default protocheck default)",
    )
    parser.add_argument(
        "--verify-with-azzem",
        action="store_true",
        help="Optionally verify a sample of codes via Azzem adapter (stub skips gracefully)",
    )
    args = parser.parse_args(argv)

    # Ensure DB exists
    db_path = init_db(args.db)

    # Load DataFrame
    if args.docx:
        df = load_ccam_from_docx(args.docx)
    elif args.csv:
        df = load_ccam_from_csv(args.csv)
    else:
        df = load_ccam_from_txt(args.txt, delimiter=args.txt_delimiter)

    # Upsert
    total = upsert_ccam(df, db_path)
    LOGGER.info("CCAM ingestion complete: %d rows upserted.", total)

    # Optional verify via Azzem stub
    if args.verify_with_azzem:
        adapter = AzzemCcamAdapter()
        if not adapter.ping():
            LOGGER.info("Verification skipped (Azzem adapter not connected).")
        else:
            # If ever connected in the future, verify first 3 codes
            sample = df["code"].head(3).tolist()
            for code in sample:
                remote = adapter.fetch_by_code(code)
                LOGGER.info("Azzem verify %s -> %r", code, remote)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
