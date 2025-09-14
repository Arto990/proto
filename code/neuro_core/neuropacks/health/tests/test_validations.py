import pytest
import sqlite3
from neuro_core.neuropacks.health.protocheck.core.schema import DDL
from neuro_core.neuropacks.health.protocheck.checks.validations import validate_deleted_quote_flow

@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(":memory:")

    # Apply schema
    cur = conn.cursor()
    for stmt in DDL:
        cur.execute(stmt)
    conn.commit()

    yield conn
    conn.close()

def test_validate_deleted_quote_flow_missing_invoice(monkeypatch, in_memory_db):
    # Patch sqlite3.connect to always return our test DB
    monkeypatch.setattr("sqlite3.connect", lambda _: in_memory_db)

    # Insert test data: deleted quote and lab scan, but no invoice
    in_memory_db.execute("""
        INSERT INTO quotes VALUES (
            'q1', 'deleted', '2024-01-01', 'P001', 'D001',
            'HBMD001', 120.0, 'Ceramic', 'source.csv'
        );
    """)
    in_memory_db.execute("""
        INSERT INTO scans VALUES (
            'P001', 'lab_sheet', '/path/to/scan.pdf', '2024-01-01'
        );
    """)
    in_memory_db.commit()

    results = validate_deleted_quote_flow()
    assert any(r["flag"] == "QUOTE_DELETED_NO_INVOICE" for r in results)

def test_validate_deleted_quote_flow_with_invoice(monkeypatch, in_memory_db):
    # Patch sqlite3.connect to always return our test DB
    monkeypatch.setattr("sqlite3.connect", lambda _: in_memory_db)

    # Insert test data: deleted quote and matching invoice
    in_memory_db.execute("""
        INSERT INTO quotes VALUES (
            'q1', 'deleted', '2024-01-01', 'P001', 'D001',
            'HBMD001', 120.0, 'Ceramic', 'source.csv'
        );
    """)
    in_memory_db.execute("""
        INSERT INTO scans VALUES (
            'P001', 'lab_sheet', '/path/to/scan.pdf', '2024-01-01'
        );
    """)
    in_memory_db.execute("""
        INSERT INTO invoices VALUES (
            'INV001', '2024-01-02', 'P001', 'John Doe', 'D001', 'Dr. Smith',
            'HBMD001', 1, 120.0, 'FSE123', 'inv.csv'
        );
    """)
    in_memory_db.commit()

    results = validate_deleted_quote_flow()
    assert any(r["flag"] == "OK_REPLACED" for r in results)
