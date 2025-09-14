# 🧠 ProtoCheck Roadmap (Health NeuroPack)

## 📌 Project Overview

**ProtoCheck** is a validation engine designed to identify potential fraud, missing billing, and incomplete documentation in dental prosthetics workflows. It analyzes scanned lab sheets, invoices, deleted acts, quotations, and insurance documents using modular Python logic, with a CLI and PyQt6 GUI.

---

## 🧱 Project Structure

```
neuro_core/
└── neuropacks/
    └── health/
        └── protocheck/
            ├── core/
            │   ├── constants.py
            │   ├── logger.py
            │   ├── schema.py
            │   └── adapters/
            │       └── azzem_ccam.py
            ├── ingesters/
            │   ├── ccam.py
            │   ├── invoices.py
            │   ├── deleted.py
            │   ├── quotes.py
            │   └── scans.py
            ├── checks/
            │   ├── feature1_lab_no_billing.py
            │   └── validations.py
            ├── cli/
            │   ├── ccam_load.py
            │   ├── invoices_load.py
            │   ├── deleted_load.py
            │   ├── quotes_load.py
            │   ├── scans_load.py
            │   ├── run_feature1.py
            │   └── run_validations.py
            ├── ui/
            │   └── main_window.py
            ├── tests/
            │   ├── test_schema.py
            │   ├── test_ccam_ingest.py
            │   ├── test_invoices_ingest.py
            │   ├── test_deleted_ingest.py
            │   ├── test_quotes_ingest.py
            │   ├── test_scans_ingest.py
            │   ├── test_feature1_engine.py
            │   └── test_validations.py
            ├── README.md
            └── ROADMAP.md
```

---

## Implemented Features

### Core
- Modular architecture (ingesters, checks, CLI, UI)
- PEP8-compliant naming (PascalCase for classes, snake_case for variables/functions)
- Dual logging: console + `protocheck.log` using `RotatingFileHandler`
- SQLite schema with English column names
- `.gitignore` protects DBs, logs, exports, caches

### Ingesters
- `ccam.py`: Load CCAM prosthetic codes from DOCX
- `deleted.py`: Load deleted acts CSV/XLSX
- `invoices.py`: Load invoices CSV/XLSX
- `quotes.py`: Load proposed/accepted/deleted quotations
- `scans.py`: Load scan index CSV for lab sheets, PECs, insurance docs
- CCAM prosthetic filter applied to all medical acts

### Feature Engine
- `feature1_lab_no_billing.py`
  - Detects lab sheets with no corresponding invoice
  - Cross-checks with deleted acts
  - Flags: `NO_INVOICE`, `DELETED_ACT_FOUND`

---

## Validations

### `validate_deleted_quote_flow`
- Lab sheet + deleted quote + no invoice → `QUOTE_DELETED_NO_INVOICE`
- If invoice exists → `OK_REPLACED`

### `validate_material_mismatch`
- Compares declared material in quote vs lab sheet (tag or OCR)
- → `MATERIAL_MISMATCH`

### `validate_deleted_prosthetic_invoices`
- Detects deleted prosthetic invoices that were never re-issued
- → `DELETED_PROSTHESIS_NO_REPLACEMENT`

### `validate_insurance_coverage`
- Ensures presence of both `insurance_card` and `pec`/`claim` for accepted quotes or invoices
- → `INSURANCE_DOC_MISSING`

---

##  All Flags

| Flag                             | Meaning                                                              |
|----------------------------------|----------------------------------------------------------------------|
| `NO_INVOICE`                     | No invoice found for a lab sheet                                     |
| `DELETED_ACT_FOUND`             | Matching deleted act found near lab sheet date                       |
| `QUOTE_DELETED_NO_INVOICE`      | Quote was deleted, lab sheet exists, no invoice                      |
| `OK_REPLACED`                   | Invoice exists despite deleted quote (valid)                         |
| `MATERIAL_MISMATCH`             | Lab sheet material differs from quote                                |
| `INSURANCE_DOC_MISSING`         | Insurance card and/or PEC/claim missing                              |
| `DELETED_PROSTHESIS_NO_REPLACEMENT` | Prosthetic invoice deleted and not replaced                            |

---

##  Tests (All Green )

- All unit tests stored in `tests/`
- Each major component has a matching test file
- Covered:
  - Schema
  - CCAM ingestion
  - Scans
  - Invoices
  - Deleted acts
  - Quotes
  - Feature 1 logic
  - All validations
- Run via:  
  ```bash
  pytest -q
  ```

---

## CLI Commands

```bash
# Load CCAM codes
python cli/ccam_load.py --docx path/to/file.docx [--verify-with-azzem]

# Load documents
python cli/scans_load.py --csv path/to/scans.csv
python cli/invoices_load.py --csv path/to/invoices.csv
python cli/deleted_load.py --csv path/to/deleted.csv
python cli/quotes_load.py --csv path/to/quotes.csv

# Run Feature 1
python cli/run_feature1.py --start YYYY-MM-DD --end YYYY-MM-DD --out results_feature1.csv

# Run all validations
python cli/run_validations.py --start YYYY-MM-DD --end YYYY-MM-DD --out results_validations.csv
```

---


##  Data Handling

- All input/output files live under:  
  ```
  neuro_core/neuropacks/health/data/
  ```
- Folder tracked via `.keep`, not committed
- `.gitignore` rules ensure:
  ```
  *.db
  *.log
  /data/
  __pycache__/
  .pytest_cache/
  *.tmp
  *.csv~
  *.xlsx~
  *.pdf~
  ```

---


##  Demo Video & Screenshots

- Walkthrough:
  1. Import test files
  2. Run Feature 1
  3. View and filter flags
  4. Open scan from UI
  5. Run all validations
  6. Export CSV
- Screenshots and video available upon request or attached in channel

---

_Last updated by Kennedy Muriuki_
