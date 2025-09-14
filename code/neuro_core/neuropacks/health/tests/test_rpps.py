# neuro_core/neuropacks/health/tests/test_rpps.py
import os
import sqlite3
import tempfile
import shutil
import pytest

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
# Import the real module under test
from neuro_core.neuropacks.health.utils import rpps_import


@pytest.fixture()
def temp_db(monkeypatch):
    """
    Create an isolated temporary SQLite DB and point rpps_import.DB_PATH to it.
    Populate with a minimal dataset covering active + deregistered variants.
    """
    tmpdir = tempfile.mkdtemp(prefix="rpps_test_")
    db_path = os.path.join(tmpdir, "rpps_test.db")

    # Patch the module-level DB path
    monkeypatch.setattr(rpps_import, "DB_PATH", db_path, raising=True)

    # Create empty table
    rpps_import.create_rpps_table()

    # Insert a few rows directly (fast, controlled)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    rows = [
        # Active
        ("11111111111", "Dr", "Dupont", "Anne", "11", "Médecin", "01", "Généraliste",
         "Actif", "1 Rue A", "75001", "Paris", "2024-01-01", "2024-01-02", "2024-01-03",
         "https://annuaire.sante.fr", "2024-01-xx"),

        # Deregistered (accented)
        ("22222222222", "Dr", "Martin", "Jean", "11", "Médecin", "02", "Cardiologie",
         "Radié", "2 Rue B", "13001", "Marseille", "2024-01-01", "2024-01-02", "2024-01-03",
         "https://annuaire.sante.fr", "2024-01-xx"),

        # Deregistered (unaccented variant)
        ("33333333333", "Dr", "Durand", "Zoé", "11", "Médecin", "03", "Pédiatrie",
         "RADIE", "3 Rue C", "69001", "Lyon", "2024-01-01", "2024-01-02", "2024-01-03",
         "https://annuaire.sante.fr", "2024-01-xx"),

        # Dereferenced (accented)
        ("44444444444", "Pr", "Bernard", "Luc", "11", "Médecin", "04", "Oncologie",
         "Déréférencé", "4 Rue D", "31000", "Toulouse", "2024-01-01", "2024-01-02", "2024-01-03",
         "https://annuaire.sante.fr", "2024-01-xx"),
    ]

    cur.executemany(f"""
        INSERT INTO {rpps_import.TABLE_NAME}
        (rpps_id, title, last_name, first_name, profession_code, profession_label,
         specialty_code, specialty_label, status, practice_address, postal_code, city,
         date_registered, date_updated, date_import, source_url, version_extraction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()

    try:
        yield db_path
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_getRppsByCode_found(temp_db):
    rec = rpps_import.getRppsByCode("11111111111")
    assert rec is not None
    assert rec["last_name"] == "Dupont"
    assert rec["first_name"] == "Anne"


def test_getRppsByCode_not_found(temp_db):
    assert rpps_import.getRppsByCode("99999999999") is None


def test_is_deregistered_status_variants():
    true_variants = [
        "Radié", "radie", "RADIE", "r a d i e", "r a di é",  # mixed/odd spacing still contains "radie"
        "Déréférencé", "dereference", "DEREFERENCE"
    ]
    for v in true_variants:
        assert rpps_import.is_deregistered_status(v) is True

    assert rpps_import.is_deregistered_status("Actif") is False
    assert rpps_import.is_deregistered_status("") is False
    assert rpps_import.is_deregistered_status(None) is False


def test_validateRppsForUse_active_vs_blocked(temp_db, capsys):
    # Active passes
    assert rpps_import.validateRppsForUse("11111111111") is True

    # Deregistered fail
    assert rpps_import.validateRppsForUse("22222222222") is False
    assert rpps_import.validateRppsForUse("33333333333") is False
    assert rpps_import.validateRppsForUse("44444444444") is False

    # Not found fail
    assert rpps_import.validateRppsForUse("00000000000") is False

    # Optional: ensure something was printed/logged (sanity)
    out = capsys.readouterr().out
    assert "Validation" in out
def test_searchRppsByName_modes_toggle(temp_db, monkeypatch):
    """
    Verify results are consistent whether RapidFuzz is used or the substring fallback path is used.
    """
    # Seed: we already inserted Dupont/Anne etc. in temp_db fixture.
    # Search for "dupo" should match "Dupont" in both modes.

    # --- Fallback (substring) path
    monkeypatch.setattr(rpps_import, "_HAS_RAPIDFUZZ", False, raising=True)
    res_fallback = rpps_import.searchRppsByName("dupo", "ann")
    assert any(r["last_name"] == "Dupont" and r["first_name"] == "Anne" for r in res_fallback)

    # --- RapidFuzz path (monkeypatch fuzz.partial_ratio)
    class _FakeFuzz:
        @staticmethod
        def partial_ratio(a, b):
            # simple contains => 100, else 0
            return 100 if a in b else 0

    monkeypatch.setattr(rpps_import, "fuzz", _FakeFuzz, raising=True)
    monkeypatch.setattr(rpps_import, "_HAS_RAPIDFUZZ", True, raising=True)
    res_rf = rpps_import.searchRppsByName("dupo", "ann")
    assert any(r["last_name"] == "Dupont" and r["first_name"] == "Anne" for r in res_rf)

    # Sanity: both modes return same RPPS IDs set
    ids_fallback = {r["rpps_id"] for r in res_fallback}
    ids_rf = {r["rpps_id"] for r in res_rf}
    assert ids_fallback == ids_rf

