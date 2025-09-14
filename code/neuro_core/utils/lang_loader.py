import json
from pathlib import Path

def load_translations(lang_code="fr"):
    """
    Load translation JSON file from neuro_core/config/langs/
    """
    base_dir = Path(__file__).resolve().parents[2]  # Points to A:/neuro-core/neuro_core/
    lang_path = Path("neuro_core/config/langs") / f"{lang_code}.json"

    if not lang_path.exists():
        raise FileNotFoundError(f"Language file not found: {lang_path}")

    with open(lang_path, encoding="utf-8") as f:
        return json.load(f)
