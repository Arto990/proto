import json
import os
import sys
import csv


def load_full_lang_names() -> dict:
    language_file = resource_path("neuro_core/config/full_lang_names.json")
    with open(language_file, "r", encoding="utf-8") as f:
        return json.load(f)


def resource_path(relative_path: str):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_professions() -> dict:
    professions_by_language = {}
    csv_path = resource_path("neuro_core/config/professions/professions.csv")

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for language, profession in row.items():
                if language not in professions_by_language:
                    professions_by_language[language] = []
                if profession not in professions_by_language[language]:
                    professions_by_language[language].append(profession)

    return professions_by_language
