# neuro_core/neuropacks/health/tests/test_ccam_ingest.py

import sqlite3
from pathlib import Path

import pandas as pd

from neuro_core.neuropacks.health.protocheck.core.schema import init_db
from neuro_core.neuropacks.health.protocheck.ingesters.ccam import (
    load_ccam_from_csv,
    load_ccam_from_txt,
    upsert_ccam,
)
from neuro_core.neuropacks.health.protocheck.core.adapters.azzem_ccam import (
    AzzemCcamAdapter,
)


def test_ccam_ingest_csv_and_upsert(tmp_path):
    # Create a tiny CSV including a duplicate code to test dedupe
    csv_path = tmp_path / "ccam_ref.csv"
    csv_path.write_text(
        "code,label,materials,basket\n"
        "HBLD001,Crown metal-ceramic,Alloy; Ceramic,Basket A\n"
        "HBLD002,Bridge 3 units,Metal,Basket B\n"
        "HBLD001,Crown metal-ceramic (dup),Alloy; Ceramic,Basket A\n",
        encoding="utf-8",
    )

    df = load_ccam_from_csv(csv_path)
    # Ensure normalization
    assert list(df.columns) == ["code", "label", "is_prosthetic", "materials", "basket"]
    assert (df["is_prosthetic"] == 1).all()
    assert df["code"].str.isupper().all()

    # Upsert into temp DB
    db = tmp_path / "protocheck_test.db"
    init_db(str(db))
    written = upsert_ccam(df, str(db))
    # Duplicate should not increase unique rows
    assert written == len(df)

    # Verify rows exist
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM ccam_prosthetics")
        (count,) = cur.fetchone()
        # unique codes expected = 2 (HBLD001, HBLD002)
        assert count == 2
        cur.execute(
            "SELECT code, label, is_prosthetic, materials, basket "
            "FROM ccam_prosthetics WHERE code='HBLD001'"
        )
        row = cur.fetchone()
        assert row is not None
        code, label, is_prosthetic, materials, basket = row
        assert code == "HBLD001"
        assert is_prosthetic == 1
        assert "Crown" in label
        assert "Alloy" in materials
        assert basket == "Basket A"


def test_ccam_ingest_txt(tmp_path):
    # Semicolon-delimited TXT
    txt_path = tmp_path / "ccam_ref.txt"
    txt_path.write_text(
        "Code;Label;Materials;Basket\n"
        "HBLA010;Inlay core;Alloy;Basket C\n",
        encoding="utf-8",
    )
    df = load_ccam_from_txt(txt_path, delimiter=";")
    assert "HBLA010" in df["code"].values
    assert (df["is_prosthetic"] == 1).all()


def test_azzem_adapter_stub_skips_gracefully():
    adapter = AzzemCcamAdapter()
    assert adapter.ping() is False
    assert adapter.fetch_by_code("HBLD001") is None
