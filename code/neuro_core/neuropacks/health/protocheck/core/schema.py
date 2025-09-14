from pathlib import Path
import sqlite3
from .logger import get_logger
from .constants import DB_PATH
from typing import Optional

LOGGER = get_logger(__name__)

DDL = [
    # CCAM prosthetics reference (from your DOCX / Azzem DB)
    """
    CREATE TABLE IF NOT EXISTS ccam_prosthetics (
        code TEXT PRIMARY KEY,
        label TEXT,
        is_prosthetic INTEGER NOT NULL,
        materials TEXT,
        basket TEXT
    );
    """,
    # Deleted acts / deleted invoices (raw import)
    """
    CREATE TABLE IF NOT EXISTS deleted_acts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        patient_id TEXT,
        patient_name TEXT,
        doctor_id TEXT,
        doctor_name TEXT,
        code TEXT,
        label TEXT,
        amount REAL,
        source_file TEXT
    );
    """,
    # Issued invoices (raw import)
    """
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_no TEXT,
        date TEXT,
        patient_id TEXT,
        patient_name TEXT,
        doctor_id TEXT,
        doctor_name TEXT,
        code TEXT,
        qty INTEGER,
        amount REAL,
        fse_no TEXT,
        source_file TEXT,
        PRIMARY KEY (invoice_no, code)
    );
    """,
    # Scanned documents index (lab sheet, signed quote, PEC, insurance)
    """
    CREATE TABLE IF NOT EXISTS scans (
        patient_id TEXT,
        doc_type TEXT,
        file_path TEXT,
        date TEXT
    );
    """,
    # Quotes table to support deleted/proposed/accepted quotes logic
    """
    CREATE TABLE IF NOT EXISTS quotes (
        quote_id TEXT,
        status TEXT,          -- proposed | accepted | deleted
        date TEXT,
        patient_id TEXT,
        doctor_id TEXT,
        code TEXT,
        amount REAL,
        declared_material TEXT,
        tooth_number TEXT,     -- ✅ NEW COLUMN
        source_file TEXT,
        PRIMARY KEY (quote_id, code)
    );
    """,
]

def init_db(db_path: Optional[str] = None) -> str:
    """
    Create (or migrate) the ProtoCheck DB. Returns the DB path used.
    """
    path = Path(db_path) if db_path else Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()
        for stmt in DDL:
            cur.execute(stmt)
        conn.commit()
    LOGGER.info("ProtoCheck database initialized at %s", path)
    return str(path)
