# RPPS Consultation – Quick Training

## Goals
- Find a health professional by RPPS ID or by name.
- Recognize if a professional is deregistered.
- Read the key data needed for back-office validation.

## Steps
1. Launch the app:
    python -m neuro_core.neuropacks.health.ui.rpps_consultation
2. **RPPS ID search:** paste the 11-digit ID → *Search*.
3. **Name search:** type last name (and optionally first name), choose Status/Profession filters → *Search*.
4. **Read results:**
- Green status: active (OK)
- Red status: deregistered (do not use for billing/linking)
- Address, city, profession, specialty shown in the table.

## Tips
- If nothing shows, try relaxing filters or correcting spelling.
- Autocomplete can help avoid typos.
- Contact operations if the status looks inconsistent with the official site.

## Limits (current version)
- Source file must be updated manually by operations.
- Live comparison to annuaire.sante.fr is not automated.