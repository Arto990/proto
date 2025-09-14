import sys
import sqlite3
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTabWidget, QCompleter,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# Import existing logic and logger
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from neuro_core.neuropacks.health.utils import rpps_import

DB_PATH = rpps_import.DB_PATH
TABLE_NAME = rpps_import.TABLE_NAME
logger = rpps_import.logger  # Reuse the shared logger


class RppsConsultation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPPS Consultation Interface")
        self.setGeometry(100, 100, 1000, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_search_by_code_tab()
        self.init_search_by_name_tab()

    def init_search_by_code_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter RPPS ID (11 digits)")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_by_code)

        search_layout.addWidget(QLabel("RPPS ID:"))
        search_layout.addWidget(self.code_input)
        search_layout.addWidget(search_btn)

        # Results table
        self.code_results = QTableWidget()
        self.code_results.setColumnCount(10)
        self.code_results.setHorizontalHeaderLabels([
            "RPPS ID", "Title", "Last Name", "First Name",
            "Profession", "Specialty", "Status (Active/Deregistered)",
            "Practice Address", "Postal Code", "City"
        ])
        self.code_results.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(search_layout)
        layout.addWidget(self.code_results)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Search by RPPS ID")

    def init_search_by_name_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Input fields
        input_layout = QHBoxLayout()
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Last Name")

        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("First Name")

        # Filters
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Deregistered"])

        self.profession_filter = QComboBox()
        self.profession_filter.addItem("All")
        self.load_professions()

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_by_name)

        input_layout.addWidget(QLabel("Last Name:"))
        input_layout.addWidget(self.nom_input)
        input_layout.addWidget(QLabel("First Name:"))
        input_layout.addWidget(self.prenom_input)
        input_layout.addWidget(QLabel("Status:"))
        input_layout.addWidget(self.status_filter)
        input_layout.addWidget(QLabel("Profession:"))
        input_layout.addWidget(self.profession_filter)
        input_layout.addWidget(search_btn)

        # Autocomplete setup
        self.load_autocomplete()

        # Results table
        self.name_results = QTableWidget()
        self.name_results.setColumnCount(10)
        self.name_results.setHorizontalHeaderLabels([
            "RPPS ID", "Title", "Last Name", "First Name",
            "Profession", "Specialty", "Status (Active/Deregistered)",
            "Practice Address", "Postal Code", "City"
        ])
        self.name_results.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(input_layout)
        layout.addWidget(self.name_results)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Search by Name")

    def load_professions(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(f"SELECT DISTINCT profession_label FROM {TABLE_NAME} ORDER BY profession_label")
            professions = [row[0] for row in cur.fetchall() if row[0]]
            for profession in professions:
                self.profession_filter.addItem(profession)
            conn.close()
        except Exception as e:
            logger.error(f"[GUI] Error loading professions: {e}")

    def load_autocomplete(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Autocomplete for last names
            cur.execute(f"SELECT DISTINCT last_name FROM {TABLE_NAME} WHERE last_name IS NOT NULL")
            last_names = [row[0] for row in cur.fetchall()]

            completer_nom = QCompleter(last_names)
            completer_nom.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.nom_input.setCompleter(completer_nom)

            # Autocomplete for first names
            cur.execute(f"SELECT DISTINCT first_name FROM {TABLE_NAME} WHERE first_name IS NOT NULL")
            first_names = [row[0] for row in cur.fetchall()]

            completer_prenom = QCompleter(first_names)
            completer_prenom.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.prenom_input.setCompleter(completer_prenom)

            conn.close()
        except Exception as e:
            logger.error(f"[GUI] Error loading autocomplete: {e}")

    def search_by_code(self):
        rpps_id = self.code_input.text().strip()
        if not rpps_import.is_valid_rpps(rpps_id):
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid 11-digit RPPS ID.")
            return

        logger.info(f"[GUI] Search by RPPS ID: {rpps_id}")
        record = rpps_import.getRppsByCode(rpps_id)
        self.code_results.setRowCount(0)

        if not record:
            QMessageBox.information(self, "Not Found", f"No professional found with RPPS ID {rpps_id}.")
            logger.info(f"[GUI] No record found for RPPS ID {rpps_id}")
            return

        self.code_results.setRowCount(1)
        self.populate_row(self.code_results, 0, record)

    def search_by_name(self):
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        status_filter = self.status_filter.currentText()
        profession_filter = self.profession_filter.currentText()

        logger.info(f"[GUI] Search by Name: {nom} {prenom}, Status={status_filter}, Profession={profession_filter}")
        results = rpps_import.searchRppsByName(nom, prenom)
        filtered = []
        for r in results:
            status_raw = str(r.get("status") or "")
            profession = r.get("profession_label", "")

            is_dereg = rpps_import.is_deregistered_status(status_raw)

            if status_filter == "Active" and is_dereg:
                continue
            if status_filter == "Deregistered" and not is_dereg:
                continue
            if profession_filter != "All" and profession != profession_filter:
                continue

            filtered.append(r)

        self.name_results.setRowCount(0)

        if not filtered:
            QMessageBox.information(self, "No Results", "No professionals found with the given criteria.")
            logger.info(f"[GUI] No results found for {nom} {prenom}")
            return

        self.name_results.setRowCount(len(filtered))
        for i, record in enumerate(filtered):
            self.populate_row(self.name_results, i, record)
    def populate_row(self, table, row_idx, record):
        fields = [
            "rpps_id", "title", "last_name", "first_name",
            "profession_label", "specialty_label", "status",
            "practice_address", "postal_code", "city"
        ]

        for col, field in enumerate(fields):
            value = record.get(field, "")

            # Sanitize None/nan values
            clean_value = "" if value in (None, "nan", "nan nan", "NaN", "None") else str(value).strip()

            # Provide graceful fallbacks for key fields
            if field == "practice_address" and not clean_value:
                clean_value = "Address not available"
            if field == "postal_code" and not clean_value:
                clean_value = "N/A"
            if field == "city" and not clean_value:
                clean_value = "N/A"
            if field == "profession_label" and not clean_value:
                clean_value = "Unknown profession"

            item = QTableWidgetItem(clean_value)

            if field == "status":
                val = clean_value or ""
                if rpps_import.is_deregistered_status(val):
                    item.setBackground(QColor("red"))
                    item.setForeground(QColor("white"))
                elif val.strip():
                    item.setBackground(QColor("green"))
                    item.setForeground(QColor("white"))
                else:
                    item.setBackground(QColor("lightgray"))
                    item.setForeground(QColor("black"))

            table.setItem(row_idx, col, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RppsConsultation()
    window.show()
    sys.exit(app.exec())
