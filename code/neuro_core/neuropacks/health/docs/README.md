# RPPS Consultation – User Guide

## What this tool does
- Imports the public RPPS extraction (manual download).
- Lets you search professionals by RPPS ID or by name.
- Shows profession, specialty, status, and main practice address.

## Prerequisites
- Place the RPPS file under `neuro_core/data/` and update `IMPORT_FILE` in `rpps_import.py` if needed.
- Run the import once to build the local SQLite database `rpps.db`.

## How to import
1. Open a terminal at the repo root.
2. Run:
    python -m neuro_core.neuropacks.health.utils.rpps_import
3. Watch the console/log for:
- Rows processed, invalid IDs skipped
- Duplicates check
- UTF-8 validation
- Distributions by profession/status
## How to run the UI
From repo root:
    python -m neuro_core.neuropacks.health.ui.rpps_consultation
## Searching
- **By RPPS ID:** enter 11 digits → Search.
- **By name:** enter last name (and optionally first name), pick filters for Status/Profession → Search.
- Autocomplete is available for names.
- Status cell colors:
  - **Green:** active (non-deregistered)
  - **Red:** deregistered
  - **Gray:** unknown/empty

## Notes
- The source file is not downloaded automatically; it must be placed manually.
- Fuzzy name search is used if `rapidfuzz` is installed; otherwise a normalized substring match is used.