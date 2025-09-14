# neuro_core/neuropacks/health/tests/test_scans_ingest.py

import pandas as pd
import sqlite3
import tempfile
from pathlib import Path
from neuro_core.neuropacks.health.protocheck.ingesters.scans import load_scans_index, upsert_scans
from neuro_core.neuropacks.health.protocheck.core.constants import DB_PATH, DOC_TYPE_LAB_SHEET

def test_load_valid_scans(tmp_path):
    sample_data = {
        "patient_id": ["P001", "P002"],
        "doc_type": ["lab_sheet", "insurance_card"],
        "file_path": ["scan1.pdf", "scan2.pdf"],
        "date": ["2025-08-10", "2025-08-11"]
    }
    df = pd.DataFrame(sample_data)
    csv_path = tmp_path / "scans.csv"
    df.to_csv(csv_path, index=False)

    loaded_df = load_scans_index(str(csv_path))
    assert len(loaded_df) == 2
    assert all(loaded_df["doc_type"].isin([DOC_TYPE_LAB_SHEET, "insurance_card"]))


def test_load_invalid_doc_type(tmp_path):
    df = pd.DataFrame({
        "patient_id": ["P003"],
        "doc_type": ["invalid_type"],
        "file_path": ["badscan.pdf"],
        "date": ["2025-08-12"]
    })
    csv_path = tmp_path / "bad_scans.csv"
    df.to_csv(csv_path, index=False)

    try:
        load_scans_index(str(csv_path))
        assert False, "Should have raised ValueError for invalid doc_type"
    except ValueError as e:
        assert "Invalid doc_type" in str(e)


def test_upsert_scans_inserts_rows(tmp_path):
    db_path = tmp_path / "test.db"
    df = pd.DataFrame({
        "patient_id": ["P001"],
        "doc_type": ["lab_sheet"],
        "file_path": ["sheet.pdf"],
        "date": ["2025-08-01"]
    })
    upsert_scans(df, db_path=db_path)

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM scans").fetchall()
        assert len(rows) == 1
