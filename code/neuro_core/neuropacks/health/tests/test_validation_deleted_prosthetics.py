import pandas as pd
from neuro_core.neuropacks.health.protocheck.checks.validations import validate_deleted_prosthetic_invoices

def test_deleted_prosthetics_flagged():
    deleted_df = pd.DataFrame([
        {
            "patient_id": "P002",
            "doctor_name": "Dr. Y",
            "code": "HBFD001",
            "label": "Bridge Resin",
            "date": "2025-08-18",
            "source_file": "deleted_prosthetics.csv",
            "is_prosthetic": 1
        },
        {
            "patient_id": "P003",
            "doctor_name": "Dr. Z",
            "code": "HBGD002",
            "label": "Cavity",
            "date": "2025-08-18",
            "source_file": "deleted_treatments.csv",
            "is_prosthetic": 0
        }
    ])

    result = validate_deleted_prosthetic_invoices(deleted_df)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(result["flag"] == "DELETED_PROSTHESIS")
    assert (result["patient_id"] == "P002").any()
