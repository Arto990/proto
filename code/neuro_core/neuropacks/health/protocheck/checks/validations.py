import sqlite3
import pandas as pd
import re
from neuro_core.neuro_ai.ocr.main import ocr_from_file


from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE
from neuro_core.neuropacks.health.protocheck.core.logger import get_logger

logger = get_logger(__name__)


def validate_deleted_quote_flow(db_path: str = DB_FILE) -> list[dict]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
        SELECT q.quote_id, q.patient_id, q.doctor_id, q.code, q.status, q.date AS quote_date,
               s.file_path AS scan_path, i.invoice_no, i.fse_no, i.date AS invoice_date
        FROM quotes q
        LEFT JOIN scans s ON q.patient_id = s.patient_id AND s.doc_type = 'lab_sheet'
        LEFT JOIN invoices i ON q.patient_id = i.patient_id AND q.code = i.code
        WHERE q.status = 'deleted'
        """
        rows = c.execute(query).fetchall()

    results = []
    for row in rows:
        quote_id, patient_id, doctor_id, code, status, quote_date, scan_path, invoice_no, fse_no, invoice_date = row

        if invoice_no or fse_no:
            flag = "OK_REPLACED"
        else:
            flag = "QUOTE_DELETED_NO_INVOICE"

        results.append({
            "quote_id": quote_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "code": code,
            "status": status,
            "quote_date": quote_date,
            "scan_path": scan_path,
            "invoice_no": invoice_no,
            "fse_no": fse_no,
            "invoice_date": invoice_date,
            "flag": flag
        })

    logger.info("Validation: %d deleted quotes processed.", len(results))
    return results


# Validation 2 — Material Mismatch
def extract_material_from_ocr(path: str) -> str:
    try:
        texts = ocr_from_file(path)
        for text in texts:
            match = re.search(r"(zirconia|ceramic|resin|metal)", text, re.IGNORECASE)
            if match:
                return match.group(1).lower()
    except Exception as e:
        logger.warning("OCR failed for %s: %s", path, str(e))
    return "unknown"


def validate_material_mismatch(quotes_df: pd.DataFrame, scans_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    lab_scans = scans_df[scans_df["doc_type"] == "lab_sheet"]

    for _, quote in quotes_df.iterrows():
        patient_id = quote["patient_id"]
        declared = quote.get("declared_material", "").strip().lower()
        matching_scan = lab_scans[lab_scans["patient_id"] == patient_id]

        if matching_scan.empty:
            continue

        scan_path = matching_scan.iloc[0]["file_path"]
        lab_material = extract_material_from_ocr(scan_path)

        if declared and lab_material != "unknown" and declared != lab_material:
            results.append({
                "patient_id": patient_id,
                "quote_id": quote["quote_id"],
                "declared_material": declared,
                "lab_material": lab_material,
                "doc_path": scan_path,
                "flag": "MATERIAL_MISMATCH"
            })

    logger.info("Validation: %d material mismatches detected.", len(results))
    return pd.DataFrame(results)

def validate_deleted_prosthetic_invoices(deleted_df: pd.DataFrame) -> pd.DataFrame:
    df = deleted_df[deleted_df["is_prosthetic"] == 1].copy()
    df["flag"] = "DELETED_PROSTHESIS"
    logger.info("Validation: %d deleted prosthetic acts found.", len(df))
    return df[["patient_id", "doctor_name", "code", "label", "date", "source_file", "flag"]]

def validate_insurance_coverage(quotes_df: pd.DataFrame, invoices_df: pd.DataFrame, scans_df: pd.DataFrame) -> pd.DataFrame:
    grouped = scans_df.groupby(["patient_id", "doc_type"])
    results = []

    def has_scan(pid, doc_type):
        return (pid, doc_type) in grouped.groups

    records = pd.concat([
        quotes_df[quotes_df["status"] == "accepted"],
        invoices_df
    ], ignore_index=True)

    for _, row in records.iterrows():
        pid = row["patient_id"]
        quote_id = row.get("quote_id", "")
        invoice_id = row.get("invoice_no") or row.get("fse_no") or ""
        missing = []

        if not has_scan(pid, "insurance_card"):
            missing.append("insurance_card")
        if not (has_scan(pid, "pec") or has_scan(pid, "insurance_claim")):
            missing.append("pec_or_claim")

        if missing:
            results.append({
                "patient_id": pid,
                "quote_id": quote_id,
                "invoice_id": invoice_id,
                "missing_type": ",".join(missing),
                "flag": "INSURANCE_DOC_MISSING"
            })

    logger.info("Validation: %d insurance document issues found.", len(results))
    return pd.DataFrame(results)


def validate_duplicate_quotes_after_deletion(db_path: str = DB_FILE) -> list[dict]:
    """
    Detects if a quote was deleted and then another with the same tooth and material
    was created later for the same patient and doctor.
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM quotes WHERE status IN ('deleted', 'proposed', 'accepted')", conn)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(by="date")

    results = []
    grouped = df.groupby(["patient_id", "doctor_id", "code", "tooth_number", "declared_material"])

    for _, group in grouped:
        statuses = group["status"].tolist()
        if "deleted" in statuses and ("proposed" in statuses or "accepted" in statuses):
            deleted_rows = group[group["status"] == "deleted"]
            new_rows = group[group["status"].isin(["proposed", "accepted"])]
            for _, new_row in new_rows.iterrows():
                results.append({
                    "patient_id": new_row["patient_id"],
                    "doctor_id": new_row["doctor_id"],
                    "code": new_row["code"],
                    "tooth_number": new_row.get("tooth_number", ""),
                    "material": new_row.get("declared_material", ""),
                    "new_quote_date": new_row["date"],
                    "flag": "RECREATED_QUOTE_AFTER_DELETION"
                })

    logger.info("Validation: %d duplicate quotes after deletion detected.", len(results))
    return results