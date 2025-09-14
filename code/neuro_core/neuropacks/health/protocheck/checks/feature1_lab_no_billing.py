# neuro_core/neuropacks/health/protocheck/checks/feature1_lab_no_billing.py

from datetime import datetime, timedelta
import pandas as pd
from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE
from neuro_core.neuropacks.health.protocheck.core.logger import get_logger
import sqlite3
from pathlib import Path

# Configurable date range tolerance in days
INVOICE_DATE_TOLERANCE = 7

def _load_table(table_name: str, conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

def run_feature1_lab_no_billing(conn_or_path, start_date: str, end_date: str) -> pd.DataFrame:
    print("Received DB path or conn:", conn_or_path)
    if isinstance(conn_or_path, (str, Path)):
        conn = sqlite3.connect(str(conn_or_path))  # Convert Path to str if needed
        should_close = True
    else:
        conn = conn_or_path
        should_close = False

    logger = get_logger(__name__)
    logger.info("Running Feature 1: Lab Sheet Without Billing")

    try:
        # Normalize dates
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        scans_df = _load_table("scans", conn)
        ccam_df = _load_table("ccam_prosthetics", conn)
        invoices_df = _load_table("invoices", conn)
        deleted_df = _load_table("deleted_acts", conn)

        lab_sheets = scans_df[scans_df["doc_type"] == "lab_sheet"].copy()
        lab_sheets["date"] = pd.to_datetime(lab_sheets["date"])
        filtered_sheets = lab_sheets[(lab_sheets["date"] >= start_date) & (lab_sheets["date"] <= end_date)]

        results = []

        for _, sheet in filtered_sheets.iterrows():
            patient_id = sheet["patient_id"]
            sheet_date = pd.to_datetime(sheet["date"])
            path = sheet["file_path"]

            for _, prosth in ccam_df.iterrows():
                ccam_code = prosth["code"]
                label = prosth["label"]

                start_range = sheet_date - timedelta(days=INVOICE_DATE_TOLERANCE)
                end_range = sheet_date + timedelta(days=INVOICE_DATE_TOLERANCE)

                # 🔧 Modified: ensure at least one of invoice_no or fse_no is present
                matching_invoice = invoices_df[
                    (invoices_df["patient_id"] == patient_id) &
                    (invoices_df["code"] == ccam_code) &
                    (pd.to_datetime(invoices_df["date"]).between(start_range, end_range)) &
                    (
                        invoices_df["invoice_no"].notna() | invoices_df["fse_no"].notna()
                    )
                ]

                if not matching_invoice.empty:
                    # Invoice found → Controlled + Validated + Conforme
                    for _, inv in matching_invoice.iterrows():
                        results.append({
                            "Patient": inv["patient_name"] or "—",
                            "Date": sheet_date.strftime("%Y-%m-%d"),
                            "Matériau Devis": label or "—",
                            "Matériau Fiche LABO": label or "—",  # 🔧 placeholder until LABO parsing
                            "Contrôlé": "Contrôlé",
                            "Validé": "Validé",
                            "Statut": "Conforme"
                        })
                else:
                    # No invoice → check deleted acts
                    deleted_match = deleted_df[
                        (deleted_df["patient_id"] == patient_id) &
                        (deleted_df["code"] == ccam_code)
                    ]

                    if not deleted_match.empty:
                        results.append({
                            "Patient": deleted_match.iloc[0]["patient_name"] or "—",
                            "Date": sheet_date.strftime("%Y-%m-%d"),
                            "Matériau Devis": label or "—",
                            "Matériau Fiche LABO": label or "—",
                            "Contrôlé": "Non contrôlé",
                            "Validé": "Supprimé",
                            "Statut": "Incohérent"
                        })
                    else:
                        results.append({
                            "Patient": "—",
                            "Date": sheet_date.strftime("%Y-%m-%d"),
                            "Matériau Devis": label or "—",
                            "Matériau Fiche LABO": label or "—",
                            "Contrôlé": "Non contrôlé",
                            "Validé": "—",
                            "Statut": "Incohérent"
                        })

        df = pd.DataFrame(results)

        return df

    finally:
        if should_close:
            conn.close()
