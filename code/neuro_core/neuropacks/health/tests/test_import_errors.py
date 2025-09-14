import os
import pytest
import sys, os as _os
sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../../../..")))
from neuro_core.neuropacks.health.utils import rpps_import

def test_import_rpps_data_nonexistent_file_logs_error(caplog):
    caplog.set_level("INFO")
    bogus = os.path.join("neuro_core", "data", "no_such_file.txt")
    rpps_import.import_rpps_data(bogus)
    # Look for our specific error message
    assert any("File not found" in rec.message for rec in caplog.records)
