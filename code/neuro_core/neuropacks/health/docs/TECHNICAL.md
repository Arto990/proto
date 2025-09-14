# RPPS – Technical Documentation

## Structure
- `utils/rpps_import.py` – schema, import, quality checks, business functions.
- `ui/rpps_consultation.py` – PyQt6 GUI using functions from `rpps_import.py`.
- SQLite DB path: `neuro_core/data/rpps.db`.

## Schema
Table: `referentiel_rpps`
- `rpps_id` (VARCHAR(11), UNIQUE), `title`, `last_name`, `first_name`
- `profession_code`, `profession_label`
- `specialty_code`, `specialty_label`
- `status`
- `practice_address`, `postal_code`, `city`
- `date_registered`, `date_updated`, `date_import`
- `source_url`, `version_extraction`

Indexes (created after import): `rpps_id`, `status`, `profession_code`.

## Import
- Chunked `read_csv` with `chunksize=1000`.
- Validates RPPS format (11 digits).
- `INSERT OR IGNORE` + UNIQUE constraint to prevent duplicates.
- Batch inserts via `executemany`.
- Logs totals, invalid rows, duration, file metadata.
- Stores import file metadata (size/hash/date) in `import_documents`.

## Quality checks
- DB total vs `COUNT(DISTINCT rpps_id)`
- File “valid & unique IDs” vs DB distinct
- Critical fields non-empty (last/first/profession)
- UTF-8 encode validation
- Distributions (profession/status)
- Missing addresses, deregistered count

## Business functions
- `getRppsByCode(rpps_id)`
- `searchRppsByName(nom, prenom)` – fuzzy if `rapidfuzz` present; otherwise normalized substring
- `checkRppsStatus(rpps_id)` – deregister check via `is_deregistered_status`
- `validateRppsForUse(rpps_id)`

## Status normalization
`is_deregistered_status(text)` normalizes accents and lowercases before checking for “radie” or “dereference”.

## GUI notes
- Uses backend functions; autocomplete for names; filters by status/profession.
- **TODO:** switch literal status checks to `is_deregistered_status()` for full consistency.

## Running
- Import: `python -m neuro_core.neuropacks.health.utils.rpps_import`
- GUI:   `python -m neuro_core.neuropacks.health.ui.rpps_consultation`

## Tests
- `pytest` from repo root.
- Basic unit/contract tests exist; comparison with live site is out of scope for now.

## Manual update procedure
1. Download the latest extraction files from annuaire.sante.fr.
2. Place them in `neuro_core/data/`.
3. Update `IMPORT_FILE`/version in `rpps_import.py` if needed.
4. Re-run the import module.
5. Review the quality check outputs.
