from mnemonic import Mnemonic
import os

from neuro_core.tools.utils import load_full_lang_names


os.makedirs("neuro_core/data", exist_ok=True)
os.makedirs("neuro_core/logs/reception", exist_ok=True)
FULL_LANG_NAMES = load_full_lang_names()
mnemo = Mnemonic("english")
