import os
import sqlite3
import tempfile
import shutil
import pytest

from PyQt6.QtWidgets import QApplication
import sys, os as _os
sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../../../..")))

from neuro_core.neuropacks.health.ui.rpps_consultation import RppsConsultation
from neuro_core.neuropacks.health.utils import rpps_import

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_autocomplete_loads_from_db(app, monkeypatch):
    # Temp DB with a few names
    tmpdir = tempfile.mkdtemp(prefix="rpps_ac_")
    try:
        db_path = os.path.join(tmpdir, "rpps_ac.db")
        monkeypatch.setattr(rpps_import, "DB_PATH", db_path, raising=True)

        rpps_import.create_rpps_table()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        rows = [
            ("55555555555", "Dr", "Alvarez", "Lucie", "11", "Médecin", "01", "Généraliste",
             "Actif", "", "", "", "2024-01-01", "2024-01-02", "2024-01-03",
             "https://annuaire.sante.fr", "2024-01-xx"),
            ("66666666666", "Dr", "Bernard", "Jean", "11", "Médecin", "01", "Généraliste",
             "Actif", "", "", "", "2024-01-01", "2024-01-02", "2024-01-03",
             "https://annuaire.sante.fr", "2024-01-xx"),
        ]
        cur.executemany(f"""
            INSERT INTO {rpps_import.TABLE_NAME}
            (rpps_id, title, last_name, first_name, profession_code, profession_label,
             specialty_code, specialty_label, status, practice_address, postal_code, city,
             date_registered, date_updated, date_import, source_url, version_extraction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit(); conn.close()

        # Build window -> triggers load_autocomplete()
        win = RppsConsultation()

        last_comp = win.nom_input.completer()
        first_comp = win.prenom_input.completer()
        assert last_comp is not None
        assert first_comp is not None

        # Models should have at least the two inserted names
        assert last_comp.model().rowCount() >= 2
        assert first_comp.model().rowCount() >= 2
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
