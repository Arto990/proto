# neuro_core/neuropacks/health/protocheck/ingesters/ccam.py

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # We still support csv/txt without pandas in tests

try:
    from docx import Document  # python-docx
except Exception:  # pragma: no cover
    Document = None  # DOCX support optional

import sqlite3

from neuro_core.neuropacks.health.protocheck.core.logger import get_logger
from neuro_core.neuropacks.health.protocheck.core.constants import DB_PATH

LOGGER = get_logger(__name__)

REQUIRED_COLS = ["code", "label", "is_prosthetic", "materials", "basket"]


def _normalize_df(df: "pandas.DataFrame") -> "pandas.DataFrame":
    """
    Ensure the DataFrame has the required columns and types.
    - code: str (upper-stripped)
    - label: str (strip)
    - is_prosthetic: int (1 for prosthetic ref)
    - materials: str
    - basket: str
    Unknown or missing columns are created empty. Extra columns are ignored.
    """
    if pd is None:
        raise RuntimeError("pandas is required for DataFrame normalization")

    # Lower-case existing columns for flexible mapping
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    mapping = {
        "code": "code",
        "libellé": "label",
        "label": "label",
        "intitule": "label",
        "designation": "label",
        "is_prosthetic": "is_prosthetic",
        "materials": "materials",
        "matiere": "materials",
        "basket": "basket",
        "panier": "basket",
    }
    cols = {}
    for src, dst in mapping.items():
        if src in df.columns:
            cols[dst] = df[src]
    out = pd.DataFrame(cols)

    for col in REQUIRED_COLS:
        if col not in out.columns:
            if col == "is_prosthetic":
                out[col] = 1
            else:
                out[col] = ""

    # Clean types
    out["code"] = out["code"].astype(str).str.strip().str.upper()
    out["label"] = out["label"].astype(str).str.strip()
    out["materials"] = out["materials"].astype(str).str.strip()
    out["basket"] = out["basket"].astype(str).str.strip()
    # Force prosthetic flag to int (1)
    out["is_prosthetic"] = 1

    # Drop empties and duplicates by code
    out = out[out["code"] != ""]
    out = out.drop_duplicates(subset=["code"])

    # Keep only required columns in order
    out = out[REQUIRED_COLS]
    return out


def load_ccam_from_docx(path: str | Path) -> "pandas.DataFrame":
    """
    Parse a DOCX reference table into a normalized DataFrame with columns:
    [code, label, is_prosthetic, materials, basket]
    Assumes at least one table where the first row is headers.
    """
    if Document is None:
        raise RuntimeError("python-docx not installed; cannot parse DOCX")

    if pd is None:
        raise RuntimeError("pandas is required to return a DataFrame")

    path = Path(path)
    LOGGER.info("Loading CCAM DOCX from %s", path)
    doc = Document(str(path))
    rows: list[list[str]] = []
    headers: Optional[list[str]] = None

    for table in doc.tables:
        # Read table
        raw = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        if not raw:
            continue
        if headers is None:
            headers = [h.strip().lower() for h in raw[0]]
            data_rows = raw[1:]
        else:
            data_rows = raw
        rows.extend(data_rows)

    if not headers:
        raise ValueError("No table with headers found in the DOCX")

    df = pd.DataFrame(rows, columns=headers[: len(rows[0])])
    df = _normalize_df(df)
    LOGGER.info("Loaded %d CCAM rows from DOCX", len(df))
    return df


def load_ccam_from_csv(path: str | Path) -> "pandas.DataFrame":
    """
    Load CCAM from a CSV file. Flexible headers; normalized to REQUIRED_COLS.
    """
    if pd is None:
        # Fallback to csv module, then wrap into minimal dicts
        path = Path(path)
        LOGGER.info("Loading CCAM CSV (no pandas) from %s", path)
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Try to map keys tolerant to casing
        mapped = []
        for r in rows:
            mr = {k.strip().lower(): (v or "").strip() for k, v in r.items()}
            code = (mr.get("code") or "").upper()
            label = mr.get("label") or mr.get("libellé") or mr.get("intitule") or ""
            materials = mr.get("materials") or mr.get("matiere") or ""
            basket = mr.get("basket") or mr.get("panier") or ""
            if code:
                mapped.append(
                    {
                        "code": code,
                        "label": label,
                        "is_prosthetic": 1,
                        "materials": materials,
                        "basket": basket,
                    }
                )
        # Convert to DataFrame if pandas available later, else raise
        if pd is None:
            raise RuntimeError("pandas not available to return DataFrame in tests")
    # If pandas exists, just read_csv then normalize
    if pd is None:
        # Should not reach here due to raise above
        raise RuntimeError("pandas required")
    df = pd.read_csv(path, dtype=str).fillna("")
    df = _normalize_df(df)
    LOGGER.info("Loaded %d CCAM rows from CSV", len(df))
    return df


def load_ccam_from_txt(path: str | Path, delimiter: str = ";") -> "pandas.DataFrame":
    """
    Load CCAM from a TXT/TSV-like file with a header row.
    Default delimiter ';' (common in FR refs). Normalize columns.
    """
    if pd is None:
        raise RuntimeError("pandas required for TXT ingestion")
    path = Path(path)
    LOGGER.info("Loading CCAM TXT from %s (delimiter=%r)", path, delimiter)
    df = pd.read_csv(path, sep=delimiter, dtype=str).fillna("")
    df = _normalize_df(df)
    LOGGER.info("Loaded %d CCAM rows from TXT", len(df))
    return df


def upsert_ccam(df: "pandas.DataFrame", db_path: Optional[str] = None) -> int:
    """
    Upsert CCAM rows into SQLite. Returns number of rows written.
    Uses INSERT OR REPLACE on PRIMARY KEY (code).
    """
    if pd is None:
        raise RuntimeError("pandas is required to upsert CCAM")

    db = Path(db_path) if db_path else Path(DB_PATH)
    db.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        # Ensure table exists (idempotent if schema.init_db already ran)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ccam_prosthetics (
                code TEXT PRIMARY KEY,
                label TEXT,
                is_prosthetic INTEGER NOT NULL,
                materials TEXT,
                basket TEXT
            );
            """
        )
        rows = df.to_dict("records")
        for r in rows:
            cur.execute(
                """
                INSERT INTO ccam_prosthetics (code, label, is_prosthetic, materials, basket)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    label=excluded.label,
                    is_prosthetic=excluded.is_prosthetic,
                    materials=excluded.materials,
                    basket=excluded.basket
                """,
                (
                    r["code"],
                    r["label"],
                    int(r.get("is_prosthetic", 1)),
                    r.get("materials", ""),
                    r.get("basket", ""),
                ),
            )
            written += 1
        conn.commit()
    LOGGER.info("Upserted %d CCAM rows into %s", written, db)
    return written
