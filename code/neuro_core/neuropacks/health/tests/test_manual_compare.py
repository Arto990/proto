# neuro_core/neuropacks/health/tests/test_manual_compare.py
import os
import csv
import pytest

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from neuro_core.neuropacks.health.utils import rpps_import

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, "live_expectations.csv")


def normalize(s):
    return (s or "").strip().lower()


@pytest.mark.skipif(not os.path.exists(CSV_PATH), reason="No live expectations CSV provided")
def test_compare_with_live_site_snapshot():
    """
    Manual verification harness:
    - Reads expected records from live_expectations.csv
    - Looks them up in the local DB via getRppsByCode
    - Compares names (case-insensitive)
    """
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rpps_id = row.get("rpps_id", "").strip()
            exp_last = normalize(row.get("expected_last_name"))
            exp_first = normalize(row.get("expected_first_name"))

            rec = rpps_import.getRppsByCode(rpps_id)
            assert rec is not None, f"RPPS {rpps_id} not found in local DB"

            got_last = normalize(rec.get("last_name"))
            got_first = normalize(rec.get("first_name"))

            assert got_last == exp_last, f"RPPS {rpps_id}: last_name mismatch: {got_last} vs {exp_last}"
            assert got_first == exp_first, f"RPPS {rpps_id}: first_name mismatch: {got_first} vs {exp_first}"