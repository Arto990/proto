import sqlite3
import pandas as pd
from neuro_core.neuropacks.health.protocheck.ingesters.deleted import load_deleted_from_file
from neuro_core.neuropacks.health.protocheck.core.utils.prosthetics_filter import filter_prosthetics

def test_deleted_filter(tmp_path):
    test_file = tmp_path / "deleted.csv"
    test_file.write_text("""date,patient_id,patient_name,doctor_id,doctor_name,code,label,amount,source_file
2025-08-01,P123,John Doe,D456,Dr. Smith,HBGD004,Prosthetic X,150.0,file1
""")

    # Create a temp test db
    test_db = tmp_path / "test.db"
    conn = sqlite3.connect(test_db)
    conn.execute("CREATE TABLE ccam_prosthetics (code TEXT)")
    conn.execute("INSERT INTO ccam_prosthetics (code) VALUES ('HBGD004')")
    conn.commit()
    conn.close()

    df = load_deleted_from_file(str(test_file))
    filtered = filter_prosthetics(df, test_db)

    assert not filtered.empty
    assert filtered.iloc[0]["code"] == "HBGD004"
