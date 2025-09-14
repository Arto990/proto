#neuro_core/neuropacks/health/tests/test_gui_contract.py
import os
import pytest

pytest.importorskip("PyQt6")  # Skip the whole module if PyQt6 not installed

from PyQt6.QtWidgets import QApplication, QTableWidget
from PyQt6.QtGui import QColor
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from neuro_core.neuropacks.health.ui.rpps_consultation import RppsConsultation
from neuro_core.neuropacks.health.utils import rpps_import


@pytest.fixture(scope="module")
def app():
    # Create a single QApplication for these tests
    app = QApplication.instance() or QApplication([])
    return app


def test_filter_and_highlight_with_accent_insensitive_check(app, monkeypatch):
    """
    Monkeypatch searchRppsByName to return crafted rows and assert:
    - 'Active' filter removes deregistered and keeps active
    - 'Deregistered' filter keeps only deregistered
    - Status cell coloring matches logic using is_deregistered_status
    """
    window = RppsConsultation()

    sample = [
        {"rpps_id": "1", "title": "Dr", "last_name": "Dupont", "first_name": "Anne",
         "profession_label": "Médecin", "specialty_label": "Généraliste",
         "status": "Actif", "practice_address": "", "postal_code": "", "city": ""},
        {"rpps_id": "2", "title": "Dr", "last_name": "Martin", "first_name": "Jean",
         "profession_label": "Médecin", "specialty_label": "Cardio",
         "status": "RADIE", "practice_address": "", "postal_code": "", "city": ""},
        {"rpps_id": "3", "title": "Dr", "last_name": "Durand", "first_name": "Zoé",
         "profession_label": "Médecin", "specialty_label": "Pédiatrie",
         "status": "Déréférencé", "practice_address": "", "postal_code": "", "city": ""},
    ]

    # Always return our sample for any name query
    monkeypatch.setattr(rpps_import, "searchRppsByName", lambda n, p="": sample)

    # --- Active filter
    window.nom_input.setText("")
    window.prenom_input.setText("")
    window.status_filter.setCurrentText("Active")
    window.profession_filter.setCurrentText("All")
    window.search_by_name()

    # Only the active one should remain
    assert window.name_results.rowCount() == 1
    status_item = window.name_results.item(0, 6)  # "Status" column
    # Should be green background (active)
    assert status_item.background().color() == QColor("green")

    # --- Deregistered filter
    window.status_filter.setCurrentText("Deregistered")
    window.search_by_name()
    assert window.name_results.rowCount() == 2

    # Check first dereg row color is red
    status_item_0 = window.name_results.item(0, 6)
    status_item_1 = window.name_results.item(1, 6)
    assert status_item_0.background().color() == QColor("red")
    assert status_item_1.background().color() == QColor("red")
def test_profession_filter_trims_rows(app, monkeypatch):
    window = RppsConsultation()

    sample = [
        {"rpps_id": "1", "title": "Dr", "last_name": "Dupont", "first_name": "Anne",
         "profession_label": "Médecin", "specialty_label": "Généraliste",
         "status": "Actif", "practice_address": "", "postal_code": "", "city": ""},
        {"rpps_id": "2", "title": "Dr", "last_name": "Martin", "first_name": "Jean",
         "profession_label": "Dentiste", "specialty_label": "Ortho",
         "status": "Actif", "practice_address": "", "postal_code": "", "city": ""},
        {"rpps_id": "3", "title": "Dr", "last_name": "Durand", "first_name": "Zoé",
         "profession_label": "Infirmier", "specialty_label": "",
         "status": "Actif", "practice_address": "", "postal_code": "", "city": ""},
    ]
    monkeypatch.setattr(rpps_import, "searchRppsByName", lambda n, p="": sample)

    # Select profession Médecin
    window.profession_filter.clear()
    window.profession_filter.addItems(["All", "Médecin", "Dentiste", "Infirmier"])
    window.profession_filter.setCurrentText("Médecin")
    window.status_filter.setCurrentText("All")

    window.search_by_name()
    assert window.name_results.rowCount() == 1
    prof_item = window.name_results.item(0, 4)  # "Profession" column
    assert prof_item.text() == "Médecin"

