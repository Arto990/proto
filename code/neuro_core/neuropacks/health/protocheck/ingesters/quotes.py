import pandas as pd
import sqlite3
from pathlib import Path
from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE
from neuro_core.neuropacks.health.protocheck.core.logger import get_logger

logger = get_logger(__name__)

VALID_STATUSES = {"proposed", "accepted", "deleted"}


def load_quotes_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype=str).fillna("")

    base_required = {"quote_id", "status", "date", "patient_id", "doctor_id", "code", "amount", "source_file"}
    optional = {"declared_material", "tooth_number"}
    available_columns = set(df.columns)

    if not base_required.issubset(available_columns):
        raise ValueError(f"Missing columns in quotes CSV. Required: {base_required}")

    # Normalize and preserve columns
    used_columns = list(base_required.union(optional).intersection(available_columns))
    df = df[used_columns]
    df = df[df["status"].isin(VALID_STATUSES)]

    # Ensure declared_material exists as a column
    if "declared_material" not in df.columns:
        df["declared_material"] = ""

    return df



def upsert_quotes(df: pd.DataFrame, db_path: str = DB_FILE):
    with sqlite3.connect(db_path) as conn:
        df.to_sql("quotes", conn, if_exists="append", index=False)
    logger.info("Inserted %d rows into quotes table.", len(df))
