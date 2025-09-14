import sqlite3
from neuro_core.neuropacks.health.protocheck.core.schema import init_db

def test_protocheck_tables_exist(tmp_path):
    db = tmp_path / "protocheck_test.db"
    path = init_db(str(db))
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()
        for t in ("ccam_prosthetics", "deleted_acts", "invoices", "scans", "quotes"):
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
            assert cur.fetchone() is not None, f"missing table: {t}"
