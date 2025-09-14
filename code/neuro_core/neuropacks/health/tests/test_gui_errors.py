# neuro_core/neuropacks/health/tests/test_gui_errors.py
import pytest
import sys, os

pytest.importorskip("PyQt6")  # skip entire module if PyQt6 isn't installed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from PyQt6.QtWidgets import QApplication
from neuro_core.neuropacks.health.ui import rpps_consultation
from neuro_core.neuropacks.health.ui.rpps_consultation import RppsConsultation
from neuro_core.neuropacks.health.utils import rpps_import


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_invalid_rpps_shows_warning(app, monkeypatch):
    """
    When an invalid RPPS (not 11 digits) is searched by code,
    the UI should show a QMessageBox.warning with the expected title/message.
    """
    window = RppsConsultation()

    calls = []
    def fake_warning(parent, title, message):
        calls.append((title, message))
        return 0

    # Patch the exact symbol used inside the UI module
    monkeypatch.setattr(
        "neuro_core.neuropacks.health.ui.rpps_consultation.QMessageBox.warning",
        fake_warning,
        raising=True,
    )

    # Enter an invalid RPPS (too short)
    window.code_input.setText("123")
    window.search_by_code()

    assert len(calls) == 1, "Expected one warning dialog"
    title, message = calls[0]
    assert title == "Invalid Input"
    assert "11-digit RPPS ID" in message
    # No row should be added
    assert window.code_results.rowCount() == 0


def test_no_results_shows_information(app, monkeypatch):
    """
    When a name search yields no rows, the UI should show a QMessageBox.information
    with 'No Results'.
    """
    window = RppsConsultation()

    # Force search to return no results
    monkeypatch.setattr(rpps_import, "searchRppsByName", lambda n, p="": [], raising=True)

    calls = []
    def fake_info(parent, title, message):
        calls.append((title, message))
        return 0

    monkeypatch.setattr(
        "neuro_core.neuropacks.health.ui.rpps_consultation.QMessageBox.information",
        fake_info,
        raising=True,
    )

    window.nom_input.setText("NoSuchLastName")
    window.prenom_input.setText("NoSuchFirstName")
    window.status_filter.setCurrentText("All")
    window.profession_filter.setCurrentText("All")

    window.search_by_name()

    assert len(calls) == 1, "Expected one information dialog"
    title, message = calls[0]
    assert title == "No Results"
    assert "No professionals found" in message
    assert window.name_results.rowCount() == 0
