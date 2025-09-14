from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QComboBox,
    QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from pathlib import Path
import sys
import csv
import sqlite3
from datetime import datetime

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import QSize

from neuro_core.neuropacks.health.protocheck.checks.feature1_lab_no_billing import run_feature1_lab_no_billing
from neuro_core.utils.lang_loader import load_translations  # utility to load langs/*.json
from neuro_core.neuropacks.health.protocheck.core.constants import DB_FILE as DB_PATH



class ProtoCheckWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProtoCheck")
        self.setStyleSheet("background-color: #f2e6dc;")
        self.current_tab = "materiaux"
        self.lang = load_translations("fr")  # Load French translation for now

        self.table_headers = {
            "materiaux": [
                self.lang["header_patient"],
                self.lang["header_invoice_deleted"],
                self.lang["header_quote_deleted"],
                self.lang["header_lab_sheet"],
                self.lang["header_match_status"],
                self.lang["header_actions"]
            ],
            "factures": [
                self.lang["header_patient"],
                self.lang["header_date"],
                self.lang["header_invoice"],
                self.lang["header_pec"],
                self.lang["header_quote"],
                self.lang["header_status"],
                self.lang["header_actions"]
            ]
        }

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(self.lang["title"])
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

       # Tabs Row
        tabs_layout = QHBoxLayout()

        self.btn_materiaux = QPushButton(f"🌿 {self.lang['tab_materials']}")
        self.btn_factures = QPushButton(f"📄 {self.lang['tab_deleted_invoices']}")

        # 🌿 Matériaux button style — dark caramel background, white text
        self.btn_materiaux.setStyleSheet("""
            QPushButton {
                background-color: #b5835a;
                color: white;
                border-radius: 10px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a06d48;
            }
        """)

        # 📄 Factures Supprimées button style — lighter background
        self.btn_factures.setStyleSheet("""
            QPushButton {
                background-color: #e0c3a3;
                color: black;
                border-radius: 10px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d4af86;
            }
        """)

        self.btn_materiaux.clicked.connect(self.switch_to_materiaux)
        self.btn_factures.clicked.connect(self.switch_to_factures)

        tabs_layout.addWidget(self.btn_materiaux)
        tabs_layout.addWidget(self.btn_factures)

        for label in [
            self.lang["label_coherence"],
            self.lang["label_workflow"],
            self.lang["label_checklist"],
            self.lang["label_traceability"]
        ]:
            l = QLabel(label)
            l.setFont(QFont("Arial", 11))
            l.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            tabs_layout.addWidget(l)

        main_layout.addLayout(tabs_layout)

        # Bottom Buttons (top-right aligned)
        self.bottom_buttons = QHBoxLayout()
        self.bottom_buttons.addStretch()  # Push buttons to the right
        self.update_bottom_buttons()
        main_layout.addLayout(self.bottom_buttons)

        # Dropdown
        dropdown_layout = QHBoxLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItem(self.lang["dropdown_all"])
        self.dropdown.setStyleSheet("padding: 5px;")
        dropdown_layout.addWidget(self.dropdown)
        main_layout.addLayout(dropdown_layout)

        # Table
        self.table = QTableWidget()
        self.update_table_for_tab()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QHeaderView::section {
                background-color: #e6d3be;
                padding: 4px;
                font-weight: bold;
            }
        """)
        self.load_data_from_backend()
        main_layout.addWidget(self.table)

        

    def update_table_for_tab(self):
        headers = self.table_headers[self.current_tab]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(0)

    def update_bottom_buttons(self):
        for i in reversed(range(self.bottom_buttons.count())):
            btn = self.bottom_buttons.itemAt(i).widget()
            if btn:
                self.bottom_buttons.removeWidget(btn)
                btn.deleteLater()

        btn_justify = QPushButton(self.lang["btn_justify_selection"])
        btn_export = QPushButton(self.lang["btn_export_selection"])

        for b in [btn_justify, btn_export]:
            b.setStyleSheet("""
                QPushButton {
                    background-color: #b38b6d;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a1765e;
                }
            """)
            self.bottom_buttons.addWidget(b)

        btn_justify.clicked.connect(self.justify_selection)
        btn_export.clicked.connect(self.export_selection_to_csv)

    def load_data_from_backend(self):
        try:
            df = run_feature1_lab_no_billing(
                conn_or_path=DB_PATH,
                start_date="2023-01-01",
                end_date="2025-12-31"
            )

            self.table.setRowCount(len(df))

            last_name = None  # Track the last non-empty name

            for row_idx, row in df.iterrows():
                raw_name = row.get("patient_name", "").strip()
                display_name = raw_name if raw_name else "—"
                self.table.setItem(row_idx, 0, QTableWidgetItem(display_name))

                # 2. Facture Supprimée (✓ Prothèse in red)
                label_invoice = QLabel("✓ Prothèse")
                label_invoice.setStyleSheet("color: #c2625c; font-weight: bold;")
                self.table.setCellWidget(row_idx, 1, label_invoice)

                # 3. Devis Supprimé (✓ or ✗)
                quote_label = QLabel()
                if row.get("flags", "").startswith("NO_INVOICE"):
                    quote_label.setText("✗ Absent")
                    quote_label.setStyleSheet("color: #803c3c; font-weight: bold;")
                else:
                    quote_label.setText("✓ Supprimé")
                    quote_label.setStyleSheet("color: #d17858; font-weight: bold;")
                self.table.setCellWidget(row_idx, 2, quote_label)

                # 4. Fiche Lab (Scannée in green)
                scan_label = QLabel("✓ Scannée" if row.get("scan_path") else "❌")
                scan_label.setStyleSheet("color: #3aa65c; font-weight: bold;" if row.get("scan_path") else "color: red;")
                self.table.setCellWidget(row_idx, 3, scan_label)

                # 5. Statut Match (badge-like label)
                status = row.get("flags", "")
                badge = QLabel()

                if "NO_INVOICE" in status:
                    badge.setText("📌 POSÉE NON FACTURÉE")
                    badge.setStyleSheet("""
                        background-color: #e06767;
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-weight: bold;
                    """)
                else:
                    badge.setText("🔒 FACTURE SEULE")
                    badge.setStyleSheet("""
                        background-color: #f1d180;
                        color: black;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-weight: bold;
                    """)
                self.table.setCellWidget(row_idx, 4, badge)

                # 6. Actions (folder icon button)
                folder_btn = QPushButton("📁")
                folder_btn.setFixedSize(28, 28)
                folder_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d9c3a4;
                        border-radius: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c2a98e;
                    }
                """)
                self.table.setCellWidget(row_idx, 5, folder_btn)

        except Exception as e:
            print(f"Error: {e}")
            self.table.setRowCount(0)

    def load_data_for_factures(self):
        query = """
            SELECT patient_name, invoice_date, invoice_amount, pec_status, quote_amount, compliance_status
            FROM factures_supp
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                display_row = list(row) + ["📞📝"]
                for col_idx, value in enumerate(display_row):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)

        except Exception as e:
            print(f"Error loading factures: {e}")
            self.table.setRowCount(0)

    def switch_to_materiaux(self):
        self.current_tab = "materiaux"
        self.update_table_for_tab()
        self.update_bottom_buttons()
        self.load_data_from_backend()

    def switch_to_factures(self):
        self.current_tab = "factures"
        self.update_table_for_tab()
        self.update_bottom_buttons()
        self.load_data_for_factures()

    def justify_selection(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.lang["no_selection"], self.lang["select_row_to_justify"])
            return

        rows = list(set(item.row() for item in selected_items))
        summary = "\n".join(self.lang["line_selected"].replace("{n}", str(r + 1)) for r in rows)
        QMessageBox.information(self, self.lang["justification"], self.lang["you_selected"] + ":\n" + summary)

    def export_selection_to_csv(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.lang["no_selection"], self.lang["select_row_to_export"])
            return

        rows = sorted(set(item.row() for item in selected_items))
        filepath, _ = QFileDialog.getSaveFileName(self, self.lang["save_as"], "", "CSV Files (*.csv)")
        if not filepath:
            return

        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)

                for row in rows:
                    row_data = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
                    writer.writerow(row_data)

            QMessageBox.information(self, self.lang["export_success"], self.lang["export_success_message"])
        except Exception as e:
            QMessageBox.critical(self, self.lang["error"], self.lang["export_error"] + f":\n{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # ✅ Set global font and widget style
    app.setStyleSheet("""
        QWidget {
            font-family: Arial;
            font-size: 13px;
        }
    """)

    window = ProtoCheckWindow()
    window.showMaximized()
    sys.exit(app.exec())
