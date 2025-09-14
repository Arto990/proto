# ProtoCheck — Health NeuroPack

## Overview

**ProtoCheck** is a fraud detection and billing validation engine tailored for dental prosthetics workflows. It parses data from scanned lab sheets, invoices, deleted acts, quotations, and insurance documents to flag inconsistencies such as missing invoices, mismatched materials, and incomplete insurance records. The system supports both CLI and PyQt6 GUI usage, and is designed to be modular, extensible, and vendor-agnostic.

---

## Features

-  Load and validate CCAM prosthetic codes
-  Import deleted acts, issued invoices, quotations, and scan indexes
-  Filter procedures using CCAM prosthetics reference
-  Detect unbilled prosthetic lab sheets (Feature 1)
-  Validate:
  - Deleted quote scenarios
  - Material mismatch between quote and lab sheet
  - Missing insurance documentation
  - Deleted prosthetic invoices
-  Export results as CSV
-  Fully tested and PEP8-compliant

---

## Directory Structure

```
protocheck/
├── core/         # Constants, logger, schema, adapters
├── ingesters/    # CSV/DOCX data loaders
├── checks/       # Feature engine and validation logic
├── cli/          # Command-line scripts
├── ui/           # PyQt6 GUI
├── tests/        # Unit tests
├── README.md     # Project documentation
└── ROADMAP.md    # Development roadmap
```

---

## Installation

1. Clone the repository:
```bash
cd neuro_core/neuropacks/health/protocheck
```

2. Set up a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

> Note: Dependencies include `pandas`, `openpyxl`, `PyQt6`, and `python-docx`.

---

## Data Files

Place all data files (CCAM docx, CSVs, etc.) in:

```
neuro_core/neuropacks/health/data/
```

This folder is **not committed**. Use `.keep` to track it in Git.

---

## CLI Usage

### Load CCAM Reference

```bash
python cli/ccam_load.py --docx path/to/file.docx
```

### Load Scans Index

```bash
python cli/scans_load.py --csv path/to/scans.csv
```

### Load Invoices, Deleted Acts, Quotes

```bash
python cli/invoices_load.py --csv path/to/invoices.csv
python cli/deleted_load.py --csv path/to/deleted.csv
python cli/quotes_load.py --csv path/to/quotes.csv
```

### Run Feature 1 (No Billing)

```bash
python cli/run_feature1.py --start YYYY-MM-DD --end YYYY-MM-DD --out results_feature1.csv
```

### Run All Validations

```bash
python cli/run_validations.py --start YYYY-MM-DD --end YYYY-MM-DD --out results_validations.csv
```

---


## Validation Flags

| Flag                             | Meaning                                                              |
|----------------------------------|----------------------------------------------------------------------|
| `NO_INVOICE`                     | No invoice found for a lab sheet                                     |
| `DELETED_ACT_FOUND`              | Matching deleted act found near lab sheet date                       |
| `QUOTE_DELETED_NO_INVOICE`       | Quote was deleted, lab sheet exists, no invoice                      |
| `OK_REPLACED`                    | Invoice exists despite deleted quote (valid)                         |
| `MATERIAL_MISMATCH`              | Lab sheet material differs from quote                                |
| `INSURANCE_DOC_MISSING`          | Insurance card and/or PEC/claim missing                              |
| `DELETED_PROSTHESIS_NO_REPLACEMENT` | Prosthetic invoice deleted and not replaced                          |

---

## Logging

- Console and file logs using `RotatingFileHandler`
- Log file: `protocheck.log`
- All logs follow this format:
  ```
  [timestamp] | LEVEL | module | message
  ```

---

## Testing

Run all tests with:

```bash
pytest -q
```

All test files are located under `tests/` and mirror feature modules.

---

## License

MIT License

---

## Author

Kennedy Muriuki
