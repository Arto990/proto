import pandas as pd
from neuro_core.neuropacks.health.protocheck.checks.validations import validate_insurance_coverage

def test_missing_insurance_docs():
    quotes_df = pd.DataFrame([
        {
            "quote_id": "Q200",
            "patient_id": "P004",
            "status": "accepted"
        }
    ])

    invoices_df = pd.DataFrame([])  # Not testing invoices in this case

    scans_df = pd.DataFrame([
        {
            "patient_id": "P004",
            "doc_type": "insurance_card",
            "file_path": "scan_card.jpg",
            "date": "2025-08-20"
        }
    ])  # Missing PEC/claim

    result = validate_insurance_coverage(quotes_df, invoices_df, scans_df)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert result.iloc[0]["flag"] == "INSURANCE_DOC_MISSING"
    assert "pec_or_claim" in result.iloc[0]["missing_type"]
