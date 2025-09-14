import pandas as pd
from neuro_core.neuropacks.health.protocheck.checks.validations import validate_duplicate_deleted_quotes

def test_duplicate_deleted_quotes_flagged():
    # Create mock quotes data
    data = [
        {
            "quote_id": "Q1",
            "status": "deleted",
            "date": "2024-01-01",
            "patient_id": "P001",
            "doctor_id": "D001",
            "code": "C123",
            "amount": 100.0,
            "declared_material": "zirconia",
            "tooth_number": "24",
            "source_file": "file1.csv"
        },
        {
            "quote_id": "Q2",
            "status": "proposed",
            "date": "2024-02-01",
            "patient_id": "P001",
            "doctor_id": "D001",
            "code": "C123",
            "amount": 100.0,
            "declared_material": "zirconia",
            "tooth_number": "24",
            "source_file": "file2.csv"
        },
        {
            "quote_id": "Q3",
            "status": "proposed",
            "date": "2024-02-01",
            "patient_id": "P001",
            "doctor_id": "D001",
            "code": "C123",
            "amount": 100.0,
            "declared_material": "resin",  # different material
            "tooth_number": "24",
            "source_file": "file3.csv"
        },
        {
            "quote_id": "Q4",
            "status": "deleted",
            "date": "2024-01-10",
            "patient_id": "P002",
            "doctor_id": "D002",
            "code": "C456",
            "amount": 80.0,
            "declared_material": "ceramic",
            "tooth_number": "12",
            "source_file": "file4.csv"
        },
        {
            "quote_id": "Q5",
            "status": "accepted",
            "date": "2024-01-15",
            "patient_id": "P002",
            "doctor_id": "D002",
            "code": "C456",
            "amount": 80.0,
            "declared_material": "ceramic",
            "tooth_number": "12",
            "source_file": "file5.csv"
        }
    ]

    df = pd.DataFrame(data)

    results = validate_duplicate_deleted_quotes(df)

    assert isinstance(results, pd.DataFrame)
    assert len(results) == 2  # Q1→Q2 and Q4→Q5 should be flagged
    flags = set(results["flag"].unique())
    assert "DUPLICATE_AFTER_DELETION" in flags

    # Check fields
    for _, row in results.iterrows():
        assert row["patient_id"] in ["P001", "P002"]
        assert row["deleted_quote_id"].startswith("Q")
        assert row["duplicate_quote_id"].startswith("Q")
        assert row["tooth_number"] == "24" or row["tooth_number"] == "12"
        assert row["material"] in ["zirconia", "ceramic"]
