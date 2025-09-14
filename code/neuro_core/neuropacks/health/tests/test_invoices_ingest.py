import sqlite3
from neuro_core.neuropacks.health.protocheck.ingesters.invoices import load_invoices_from_file
from neuro_core.neuropacks.health.protocheck.core.utils.prosthetics_filter import filter_prosthetics

def test_invoice_filter(tmp_path):
    # Create test CSV
    test_file = tmp_path / "invoice.csv"
    test_file.write_text("""invoice_no,date,patient_id,patient_name,doctor_id,doctor_name,code,qty,amount,fse_no,source_file
INV001,2025-08-01,P123,John Doe,D456,Dr. Smith,HBGD004,1,150.0,FSE001,file2
""")

    # Create temp DB file with prosthetics table
    test_db = tmp_path / "test.db"
    conn = sqlite3.connect(test_db)
    conn.execute("CREATE TABLE ccam_prosthetics (code TEXT)")
    conn.execute("INSERT INTO ccam_prosthetics (code) VALUES ('HBGD004')")
    conn.commit()
    conn.close()

    # Run logic
    df = load_invoices_from_file(str(test_file))
    filtered = filter_prosthetics(df, test_db)

    # Assert result
    assert not filtered.empty
    assert filtered.iloc[0]["code"] == "HBGD004"
