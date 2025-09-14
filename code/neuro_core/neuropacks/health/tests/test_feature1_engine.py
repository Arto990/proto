# test_feature1_engine.py

import sqlite3
import pandas as pd
import pytest
from datetime import date

from neuro_core.neuropacks.health.protocheck.checks.feature1_lab_no_billing import run_feature1_lab_no_billing
from neuro_core.neuropacks.health.protocheck.core.schema import DDL


@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(":memory:")

    # Apply schema
    cur = conn.cursor()
    for stmt in DDL:
        cur.execute(stmt)
    conn.commit()

    # Add required prosthetic code
    conn.execute(
        "INSERT INTO ccam_prosthetics (code, label, is_prosthetic) VALUES (?, ?, ?)",
        ("HBMD001", "Crown on molar", 1)
    )
    conn.commit()

    yield conn
    conn.close()


def insert_scan(conn, patient_id, doc_type, file_path, date_):
    conn.execute(
        "INSERT INTO scans (patient_id, doc_type, file_path, date) VALUES (?, ?, ?, ?)",
        (patient_id, doc_type, file_path, date_),
    )
    conn.commit()


def insert_invoice(conn, invoice_no, date_, patient_id, doctor_id, code, qty, amount):
    conn.execute(
        """INSERT INTO invoices (
            invoice_no, date, patient_id, patient_name, doctor_id, doctor_name,
            code, qty, amount, fse_no, source_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            invoice_no, date_, patient_id, "John Doe", doctor_id, "Dr. Smith",
            code, qty, amount, "FSE123", "invoice.csv"
        ),
    )
    conn.commit()


def insert_deleted_act(conn, date_, patient_id, doctor_id, code, label, amount):
    conn.execute(
        """INSERT INTO deleted_acts (
            id, date, patient_id, patient_name, doctor_id, doctor_name,
            code, label, amount, source_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            None, date_, patient_id, "John Doe", doctor_id, "Dr. Smith",
            code, label, amount, "deleted.csv"
        ),
    )
    conn.commit()


def test_invoice_exists(in_memory_db):
    insert_scan(in_memory_db, "P001", "lab_sheet", "scan1.pdf", "2023-01-10")
    insert_invoice(in_memory_db, "INV001", "2023-01-09", "P001", "D001", "HBMD001", 1, 150.0)

    df = run_feature1_lab_no_billing(in_memory_db, date(2023, 1, 1), date(2023, 1, 31))
    assert len(df) == 1
    assert df["flags"].iloc[0] == ""


def test_no_invoice_found(in_memory_db):
    insert_scan(in_memory_db, "P002", "lab_sheet", "scan2.pdf", "2023-01-15")

    df = run_feature1_lab_no_billing(in_memory_db, date(2023, 1, 1), date(2023, 1, 31))
    assert len(df) == 1
    assert "NO_INVOICE" in df["flags"].iloc[0]


def test_no_invoice_but_deleted_act_found(in_memory_db):
    insert_scan(in_memory_db, "P003", "lab_sheet", "scan3.pdf", "2023-01-20")
    insert_deleted_act(
        in_memory_db,
        "2023-01-21", "P003", "D003", "HBMD001", "Molar crown", 130.0
    )

    df = run_feature1_lab_no_billing(in_memory_db, date(2023, 1, 1), date(2023, 1, 31))
    assert len(df) == 1
    assert "NO_INVOICE" in df["flags"].iloc[0]
    assert "DELETED_ACT_FOUND" in df["flags"].iloc[0]
