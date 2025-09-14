from pathlib import Path

# Project anchors
HEALTH_ROOT = Path(__file__).resolve().parents[2]  # .../neuropacks/health
DATA_DIR = HEALTH_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "protocheck.db"

# Ensure dirs exist at import time 
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Formats / enums
DATE_FMT = "%Y-%m-%d"

# Document types (fixed English names)
DOC_TYPE_LAB_SHEET = "lab_sheet"
DOC_TYPE_SIGNED_QUOTE = "signed_quote"
DOC_TYPE_PEC = "pec"
DOC_TYPE_INSURANCE_CARD = "insurance_card"
DOC_TYPE_INSURANCE_CLAIM = "insurance_claim"

DB_FILE = DB_PATH