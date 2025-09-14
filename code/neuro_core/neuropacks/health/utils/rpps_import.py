import os
import sqlite3
import logging
from datetime import datetime
import time
import pandas as pd
import unicodedata

# Fuzzy search
try:
    from rapidfuzz import fuzz
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False

# === CONFIGURATION ===
DATA_DIR = os.path.join("neuro_core", "data")
RPPS_STAGE = os.getenv("RPPS_STAGE", "dev")  # default ok for local
DB_PATH = os.path.join(DATA_DIR, f"rpps_{RPPS_STAGE}.db")

TABLE_NAME = "referentiel_rpps"
IMPORT_FILE = os.path.join(DATA_DIR, "PS_LibreAcces_Personne_activite_202507290829.txt")

# Optional companion files from the official site
DIPLOMA_FILE = os.path.join(DATA_DIR, "PS_LibreAcces_Dipl_AutExerc.txt")
SAVOIR_FAIRE_FILE = os.path.join(DATA_DIR, "PS_LibreAcces_SavoirFaire.txt")

os.makedirs(DATA_DIR, exist_ok=True)

# === LOGGING SETUP (console + file) ===
logger = logging.getLogger("rpps_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(os.path.join(DATA_DIR, "rpps_import.log"), encoding="utf-8")
console_handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Note fuzzy availability once, early
logger.info("Fuzzy search: %s", "rapidfuzz enabled (partial_ratio, min_score=80)" if _HAS_RAPIDFUZZ else "fallback to normalized substring (rapidfuzz not installed)")

# === SCHEMA CREATION ===
def create_rpps_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rpps_id VARCHAR(11) UNIQUE,
        title VARCHAR(20),
        last_name VARCHAR(100),
        first_name VARCHAR(100),
        profession_code VARCHAR(20),
        profession_label VARCHAR(100),
        specialty_code VARCHAR(20),
        specialty_label VARCHAR(100),
        status VARCHAR(50),
        practice_address VARCHAR(255),
        postal_code VARCHAR(20),
        city VARCHAR(100),
        date_registered DATE,
        date_updated DATE,
        date_import DATE,
        source_url VARCHAR(255),
        version_extraction VARCHAR(50)
    );
    """)
    conn.commit()
    conn.close()
    logger.info("RPPS table created successfully (indexes will be added after import).")
    print("RPPS table created successfully (indexes will be added after import).")

def create_rpps_indexes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_rpps_id ON {TABLE_NAME}(rpps_id);")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_status ON {TABLE_NAME}(status);")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_profession_code ON {TABLE_NAME}(profession_code);")
    conn.commit()
    conn.close()
    logger.info("Indexes created successfully after data import.")
    print("Indexes created successfully after data import.")

# === DOCUMENT STORAGE FUNCTION ===
def store_import_document(file_path: str):
    """
    Store metadata of the imported RPPS document in a dedicated table.
    Saves file name, size (MB), SHA-256 hash, and import date.
    """
    if not os.path.exists(file_path):
        logger.error(f"Document not found: {file_path}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS import_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_size_mb REAL,
            sha256 TEXT,
            import_date DATE
        )
    """)

    import hashlib
    with open(file_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    stats = os.stat(file_path)
    file_size_mb = round(stats.st_size / (1024 * 1024), 2)

    cur.execute("""
        INSERT INTO import_documents (file_name, file_size_mb, sha256, import_date)
        VALUES (?, ?, ?, ?)
    """, (
        os.path.basename(file_path),
        file_size_mb,
        sha256,
        datetime.now().date()
    ))

    conn.commit()
    conn.close()
    logger.info(f"Document metadata stored for {file_path}")
    print(f"Document metadata stored for {file_path}")

# === RPPS ID VALIDATION ===
def is_valid_rpps(rpps_id: str) -> bool:
    return isinstance(rpps_id, str) and rpps_id.isdigit() and len(rpps_id) == 11

def normalize_text(text: str) -> str:
    """Remove accents and normalize case for search/flags."""
    if not text:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

# centralized status check with accent-insensitivity
def is_deregistered_status(text: str) -> bool:
    s = normalize_text(text)
    # remove all whitespace to catch variants like "r a d i e"
    s = ''.join(s.split())
    return ("radie" in s) or ("dereference" in s)

# === IMPORT FUNCTION ===
def import_rpps_data(file_path: str):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    start_time = time.time()
    conn = sqlite3.connect(DB_PATH)
    total_rows, invalid_rows = 0, 0

    insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} 
        (rpps_id, title, last_name, first_name, profession_code, profession_label,
         specialty_code, specialty_label, status, practice_address, 
         postal_code, city, date_registered, date_updated, date_import,
         source_url, version_extraction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        for chunk in pd.read_csv(file_path, sep="|", dtype=str, chunksize=1000, encoding="utf-8"):
            batch_data = []
            for _, row in chunk.iterrows():
                total_rows += 1
                rpps_id = str(row.get("Identifiant PP", "")).strip()

                if not is_valid_rpps(rpps_id):
                    invalid_rows += 1
                    logger.warning(f"Invalid RPPS ID skipped: {rpps_id}")
                    continue

                practice_address = " ".join([
                    str(row.get("Numéro Voie (coord. structure)", "")).strip(),
                    str(row.get("Libellé Voie (coord. structure)", "")).strip()
                ]).strip()

                batch_data.append((
                    rpps_id,
                    row.get("Libellé civilité d'exercice", ""),
                    row.get("Nom d'exercice", ""),
                    row.get("Prénom d'exercice", ""),
                    row.get("Code profession", ""),
                    row.get("Libellé profession", ""),
                    row.get("Code savoir-faire", ""),
                    row.get("Libellé savoir-faire", ""),
                    row.get("Libellé rôle", ""),
                    practice_address,
                    row.get("Code postal (coord. structure)", ""),
                    row.get("Libellé commune (coord. structure)", ""),
                    datetime.now().date(),
                    datetime.now().date(),
                    datetime.now().date(),
                    "https://annuaire.sante.fr/web/site-pro/extractions-publiques",
                    "2025-07-29"
                ))

            if batch_data:
                try:
                    conn.executemany(insert_sql, batch_data)
                except Exception as e:
                    logger.error(f"Batch insert failed: {e}")

        conn.commit()
        duration = round(time.time() - start_time, 2)
        logger.info(f"Import complete. Rows processed: {total_rows}, Invalid RPPS: {invalid_rows}, Duration: {duration}s")
        print(f" Import complete. Rows processed: {total_rows}, Invalid RPPS: {invalid_rows}, Duration: {duration}s")
    finally:
        conn.close()

# === QUALITY CHECKS ===
def perform_quality_checks(file_path: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # DB: total vs distinct rpps_id
    cur.execute(f"SELECT COUNT(*), COUNT(DISTINCT rpps_id) FROM {TABLE_NAME}")
    db_total, db_distinct = cur.fetchone()
    dup_in_db = db_total - db_distinct
    if dup_in_db > 0:
        logger.warning(f"DB duplicates detected: total={db_total}, distinct={db_distinct}, duplicates={dup_in_db}")
        print(f"DB duplicates detected: total={db_total}, distinct={db_distinct}, duplicates={dup_in_db}")
    else:
        logger.info(f"No DB duplicates. distinct={db_distinct}")
        print(f"No DB duplicates. distinct={db_distinct}")

    # File: count only valid and unique RPPS
    file_total_rows = 0
    file_valid = 0
    valid_unique_ids = set()
    try:
        for chunk in pd.read_csv(file_path, sep="|", dtype=str, chunksize=100000, encoding="utf-8"):
            file_total_rows += len(chunk)
            ids = chunk.get("Identifiant PP", pd.Series([], dtype=str)).astype(str).str.strip()
            for rid in ids:
                if is_valid_rpps(rid):
                    file_valid += 1
                    valid_unique_ids.add(rid)
    except Exception as e:
        logger.error(f"Error while scanning file for valid/unique counts: {e}")
        print(f"Error while scanning file for valid/unique counts: {e}")

    file_valid_unique = len(valid_unique_ids)
    logger.info(f"File counts -> total_rows={file_total_rows}, valid={file_valid}, valid_unique={file_valid_unique}")
    print(f"File counts -> total_rows={file_total_rows}, valid={file_valid}, valid_unique={file_valid_unique}")

    # Compare valid_unique (file) vs distinct (DB)
    if file_valid_unique != db_distinct:
        logger.warning(f"Row count mismatch (valid_unique file vs distinct DB): file={file_valid_unique}, db={db_distinct}")
        print(f"Row count mismatch (valid_unique file vs distinct DB): file={file_valid_unique}, db={db_distinct}")
    else:
        logger.info("Row count matches between file(valid_unique) and DB(distinct).")
        print("Row count matches between file(valid_unique) and DB(distinct).")

    # Missing critical fields
    cur.execute(f"""
        SELECT COUNT(*) FROM {TABLE_NAME}
        WHERE (last_name IS NULL OR last_name = '')
           OR (first_name IS NULL OR first_name = '')
           OR (profession_code IS NULL OR profession_code = '')
    """)
    missing_critical = cur.fetchone()[0]
    if missing_critical > 0:
        logger.warning(f"{missing_critical} records have missing critical fields.")
        print(f"{missing_critical} records have missing critical fields.")
    else:
        logger.info("All critical fields are filled.")
        print("All critical fields are filled.")

    # UTF-8 validation
    try:
        cur.execute(f"SELECT rpps_id, last_name, first_name, profession_label, specialty_label FROM {TABLE_NAME}")
        rows = cur.fetchall()
        invalid_utf8 = 0
        for row in rows:
            for value in row[1:]:
                if value:
                    try:
                        value.encode("utf-8")
                    except UnicodeEncodeError:
                        invalid_utf8 += 1
        if invalid_utf8 > 0:
            logger.warning(f"{invalid_utf8} fields failed UTF-8 validation.")
            print(f"{invalid_utf8} fields failed UTF-8 validation.")
        else:
            logger.info("UTF-8 validation passed for all checked fields.")
            print("UTF-8 validation passed for all checked fields.")
    except Exception as e:
        logger.error(f"Error during UTF-8 validation: {e}")
        print(f"Error during UTF-8 validation: {e}")

    # Distributions and sanity checks
    print("\n--- Distribution by Profession (top 10) ---")
    cur.execute(f"""
        SELECT profession_label, COUNT(*)
        FROM {TABLE_NAME}
        GROUP BY profession_label
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    for profession, count in cur.fetchall():
        print(f"{profession}: {count}")

    print("\n--- Distribution by Status ---")
    cur.execute(f"SELECT status, COUNT(*) FROM {TABLE_NAME} GROUP BY status ORDER BY COUNT(*) DESC")
    for status, count in cur.fetchall():
        print(f"{status}: {count}")

    # Deregistered count with diacritic-insensitive check
    cur.execute(f"SELECT status FROM {TABLE_NAME}")
    statuses = [row[0] or "" for row in cur.fetchall()]
    deregistered = sum(1 for s in statuses if is_deregistered_status(s))
    if deregistered > 0:
        logger.info(f"{deregistered} deregistered professionals found.")
        print(f"{deregistered} deregistered professionals found.")
    else:
        logger.info("No deregistered professionals detected.")
        print("No deregistered professionals detected.")

    # Missing addresses
    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE practice_address IS NULL OR practice_address = ''")
    missing_address = cur.fetchone()[0]
    if missing_address > 0:
        logger.warning(f"{missing_address} records missing practice address.")
        print(f"{missing_address} records missing practice address.")
    else:
        logger.info("All records have a practice address.")
        print("All records have a practice address.")

    conn.close()

# === BUSINESS FUNCTIONS ===
def getRppsByCode(rpps_id: str):
    """
    Retrieve a professional's record by RPPS ID.
    Returns a dictionary with details if found, otherwise None.
    """
    if not is_valid_rpps(rpps_id):
        logger.warning(f"Invalid RPPS ID format: {rpps_id}")
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE rpps_id = ?", (rpps_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        logger.info(f"Record found for RPPS ID {rpps_id}")
        return dict(row)
    else:
        logger.info(f"No record found for RPPS ID {rpps_id}")
        return None

def searchRppsByName(nom: str, prenom: str = ""):
    """
    Search for professionals by last name and optionally first name.
    Uses fuzzy matching when rapidfuzz is available; otherwise falls back to normalized substring match.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    q_nom = normalize_text(nom)
    q_pre = normalize_text(prenom) if prenom else ""
    min_score = 80

    results = []
    try:
        cur.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cur.fetchall()

        if _HAS_RAPIDFUZZ:
            for row in rows:
                db_nom = normalize_text(row["last_name"])
                db_pre = normalize_text(row["first_name"])

                score_nom = 100 if not q_nom else fuzz.partial_ratio(q_nom, db_nom)
                score_pre = 100 if not q_pre else fuzz.partial_ratio(q_pre, db_pre)

                if score_nom >= min_score and score_pre >= min_score:
                    results.append(dict(row))
            logger.info(f"Fuzzy search results for {nom} {prenom}: {len(results)} found (min_score={min_score})")
        else:
            for row in rows:
                db_nom = normalize_text(row["last_name"])
                db_pre = normalize_text(row["first_name"])
                if (q_nom in db_nom) and (q_pre in db_pre if q_pre else True):
                    results.append(dict(row))
            logger.info(f"Substring search results for {nom} {prenom}: {len(results)} found (rapidfuzz not installed)")
    finally:
        conn.close()

    return results

def checkRppsStatus(rpps_id: str):
    """
    Check the status of a professional by RPPS ID.
    Returns a dictionary with RPPS ID, name, and status.
    Raises an alert if not found or deregistered.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE rpps_id = ?", (rpps_id,))
        row = cur.fetchone()

        if not row:
            logger.warning(f"RPPS ID {rpps_id} not found.")
            return {"rpps_id": rpps_id, "status": "NOT_FOUND", "alert": True}

        status = row["status"] or ""
        if is_deregistered_status(status):  # accent-insensitive check
            logger.warning(f"RPPS ID {rpps_id} is deregistered.")
            return {
                "rpps_id": rpps_id,
                "name": f"{row['first_name']} {row['last_name']}",
                "status": row["status"],
                "alert": True
            }

        return {
            "rpps_id": rpps_id,
            "name": f"{row['first_name']} {row['last_name']}",
            "status": row["status"],
            "alert": False
        }
    finally:
        conn.close()

def validateRppsForUse(rpps_id: str) -> bool:
    """
    Validate if a professional can be used for billing or linking.
    Returns True if valid, False if not.
    Logs and raises alerts if RPPS not found or deregistered.
    """
    result = checkRppsStatus(rpps_id)

    if result.get("alert", False):
        logger.error(f"Validation failed for RPPS {rpps_id}: {result['status']}")
        print(f"Validation failed: RPPS {rpps_id} - {result['status']}")
        return False

    logger.info(f"Validation passed for RPPS {rpps_id}: {result['status']}")
    print(f"Validation passed: RPPS {rpps_id} - {result['status']}")
    return True

# === MAIN EXECUTION ===
if __name__ == "__main__":
    logger.info("Starting RPPS schema creation...")
    create_rpps_table()
    logger.info("Schema ready. Beginning import...")

    # Log source file metadata
    try:
        file_stats = os.stat(IMPORT_FILE)
        file_size_mb = round(file_stats.st_size / (1024 * 1024), 2)
        last_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"Source file: {IMPORT_FILE}")
        logger.info(f"File size: {file_size_mb} MB")
        logger.info(f"Last modified: {last_modified}")

        print(f"Source file: {IMPORT_FILE}")
        print(f"File size: {file_size_mb} MB")
        print(f"Last modified: {last_modified}")
    except Exception as e:
        logger.error(f"Could not read source file metadata: {e}")
        print(f"Could not read source file metadata: {e}")

    # Store document metadata for all three official files (present or not)
    store_import_document(IMPORT_FILE)
    store_import_document(DIPLOMA_FILE)
    store_import_document(SAVOIR_FAIRE_FILE)

    import_rpps_data(IMPORT_FILE)

    # Create indexes AFTER import 
    create_rpps_indexes()

    # Perform quality checks after import
    perform_quality_checks(IMPORT_FILE)

    logger.info("RPPS import process finished.")
    print(" RPPS import process finished.")
