# neuro_core/neuropacks/health/protocheck/ui/run_gui.py

import sys
from PyQt6.QtWidgets import QApplication
from .main_window import ProtoCheckWindow

from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE
print("Resolved DB_FILE:", DB_FILE)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtoCheckWindow()
    window.show()
    sys.exit(app.exec())
