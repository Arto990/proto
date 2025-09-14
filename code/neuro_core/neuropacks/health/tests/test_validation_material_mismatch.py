import pandas as pd
from neuro_core.neuropacks.health.protocheck.checks.validations import validate_material_mismatch

def test_material_mismatch():
    quotes_df = pd.DataFrame([
        {
            "quote_id": "Q100",
            "patient_id": "P001",
            "declared_material": "zirconia"
        }
    ])

    scans_df = pd.DataFrame([
        {
            "patient_id": "P001",
            "doc_type": "lab_sheet",
            "file_path": "neuro_core/neuropacks/health/data/lab_sheet_test1.jpg",
            "date": "2025-08-21"
        }
    ])

    result = validate_material_mismatch(quotes_df, scans_df)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert result.iloc[0]["flag"] == "MATERIAL_MISMATCH"
