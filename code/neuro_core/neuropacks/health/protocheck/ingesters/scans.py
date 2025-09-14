# neuro_core/neuropacks/health/protocheck/ingesters/scans.py

import pandas as pd
import sqlite3
from pathlib import Path
from ..core.logger import get_logger
from ..core.constants import (
    DB_PATH,
    DOC_TYPE_LAB_SHEET,
    DOC_TYPE_SIGNED_QUOTE,
    DOC_TYPE_PEC,
    DOC_TYPE_INSURANCE_CARD,
    DOC_TYPE_INSURANCE_CLAIM,
)

LOGGER = get_logger(__name__)

VALID_DOC_TYPES = {
    DOC_TYPE_LAB_SHEET,
    DOC_TYPE_SIGNED_QUOTE,
    DOC_TYPE_PEC,
    DOC_TYPE_INSURANCE_CARD,
    DOC_TYPE_INSURANCE_CLAIM,
}


def load_scans_index(csv_path: str) -> pd.DataFrame:
    """
    Load and validate scans index from CSV.
    Required columns: patient_id, doc_type, file_path, date
    """
    df = pd.read_csv(csv_path)
    expected_cols = {"patient_id", "doc_type", "file_path", "date"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in scans CSV: {missing}")

    # Normalize doc_type
    df["doc_type"] = df["doc_type"].str.strip().str.lower()
    invalid_types = df.loc[~df["doc_type"].isin(VALID_DOC_TYPES), "doc_type"].unique()
    if len(invalid_types) > 0:
        raise ValueError(f"Invalid doc_type(s) found: {invalid_types}")

    LOGGER.info("Loaded %d scan entries from %s", len(df), csv_path)
    return df


def upsert_scans(df: pd.DataFrame, db_path: Path = DB_PATH):
    """
    Insert validated scan records into the scans table.
    """
    with sqlite3.connect(db_path) as conn:
        df.to_sql("scans", conn, if_exists="append", index=False)
    LOGGER.info("Inserted %d rows into scans table", len(df))
