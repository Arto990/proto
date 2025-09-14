import pandas as pd
import sqlite3
from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE
from neuro_core.neuropacks.health.protocheck.core.logger import get_logger

EXPECTED_COLUMNS = [
    "invoice_no", "date", "patient_id", "patient_name", "doctor_id",
    "doctor_name", "code", "qty", "amount", "fse_no", "source_file"
]

def load_invoices_from_file(path: str) -> pd.DataFrame:
    df = pd.read_excel(path) if path.endswith((".xlsx", ".xls")) else pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in invoice file: {missing}")
    return df[EXPECTED_COLUMNS]

def upsert_invoices(df: pd.DataFrame, db_path: str = DB_FILE):
    with sqlite3.connect(db_path) as conn:
        df.to_sql("invoices", conn, if_exists="append", index=False)
        get_logger.info(f"{len(df)} invoices inserted into database.")
