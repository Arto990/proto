import bcrypt
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt6.QtWidgets import (
    QGridLayout,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QButtonGroup,
)

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.forgot_password_window import ForgotPasswordWindow
from neuro_core.ui.windows.password_recovery_window import PasswordRecoveryWindow


class ForgotPasswordPhraseWindow(ForgotPasswordWindow, QMainWindow):
    def __init__(self, current_lang: str, current_style: str, username: str):
        QMainWindow.__init__(self)

        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"
        self.username = username

        self.languages = self.load_languages("forgot_password_phrase_window")
        self.styles = self.load_styles("forgot_password_phrase_window")

        self.current_lang = current_lang
        self.current_style = current_style
        self.current_dict = self.languages[self.current_lang]

        icon_path = resource_path("neuro_core/config/icons/main.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(400, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 21, 0, 0)

        self.setup_ui()
        self.apply_style()
        self.update_texts()

    def setup_ui(self):
        # Логотип
        self.logo_label = QLabel()
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addSpacing(10)

        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(10)

        self.instruction_label = QLabel()
        self.instruction_label.setFixedSize(250, 50)
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(
            self.instruction_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(3)

        # GridLayout for recovery phrase

        self.button_width = 85
        self.button_height = 32
        self.num_cols = 3
        self.num_rows = 4

        self.col_spacing = 12
        self.row_spacing = 12

        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(self.col_spacing)
        self.grid_layout.setVerticalSpacing(self.row_spacing)

        self.recovery_labels = []

        # Add QLineEdit widgets to the grid layout
        for idx in range(self.num_rows * self.num_cols):
            label = QLineEdit("", self.central_widget)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(self.button_width, self.button_height)
            self.recovery_labels.append(label)

            row = idx // self.num_cols
            col = idx % self.num_cols
            self.grid_layout.addWidget(label, row, col)

        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        self.layout.addWidget(grid_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        for label in self.recovery_labels:
            label.textChanged.connect(self.continue_validation)

        # Error label
        self.error_label = QLabel()
        self.error_label.setFixedHeight(10)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Container for theme switch buttons
        self.theme_container = QWidget()
        self.theme_switch_layout = QHBoxLayout()
        self.theme_switch_layout.setContentsMargins(4, 0, 4, 0)
        self.theme_switch_layout.setSpacing(1)
        self.theme_container.setLayout(self.theme_switch_layout)

        self.theme_group = QButtonGroup(self)

        for theme in self.styles.keys():
            button = QPushButton(self.current_dict[f"theme_{theme}"])
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            if theme == self.current_style:
                button.setChecked(True)
            button.clicked.connect(
                lambda checked, t=theme: self.change_theme(
                    t,
                    self.log_file_path,
                    self.module_name,
                    f"THEME_{t}".upper(),
                    self.username,
                    "INFO",
                    f"{t} mode enabled",
                )
            )
            self.theme_group.addButton(button)
            self.theme_switch_layout.addWidget(button)

        self.layout.addWidget(
            self.theme_container, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(7)

        # Back and Continue buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(40, 0, 40, 0)

        # Back button
        self.back_button = QPushButton()
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setFixedSize(150, 48)
        self.back_button.clicked.connect(self.open_forgot_password_window)
        self.button_layout.addWidget(
            self.back_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Continue button
        self.continue_button = QPushButton(self.current_dict["continue"])
        self.continue_button.clicked.connect(self.handle_continue)
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.setFixedSize(150, 48)
        self.button_layout.addWidget(
            self.continue_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(self.button_layout)

        # Footer label
        self.footer_label = QLabel()
        self.layout.addWidget(
            self.footer_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addStretch()

    def apply_style(self):
        style = self.styles[self.current_style]

        # Background image
        image_path = resource_path(style["background_image_path"])
        pixmap = QPixmap(image_path).scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Logo
        logo_path = resource_path(style["logo_path"])
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(
            191,
            151,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_label.setPixmap(scaled_pixmap)
        self.logo_label.setScaledContents(True)

        # Gradient label
        gradient_style = style["gradient_label"]
        gradient_stylesheet = f"""
            QLabel {{
                min-height: {gradient_style["height"]};
                max-height: {gradient_style["height"]};
                font-family: {gradient_style["font-family"]};
                font-weight: {gradient_style["font-weight"]};
                color: {gradient_style["color"]};
                font-size: {gradient_style["font-size"]};
            }}
        """
        self.gradient_label.setStyleSheet(gradient_stylesheet)
        self.add_shadow(self.gradient_label, **gradient_style["shadow"])

        # Instruction label
        instruction_style = style["instruction_label"]
        instruction_stylesheet = f"""
                    QLabel {{
                        font-family: {instruction_style["font-family"]};
                        font-weight: {instruction_style["font-weight"]};
                        font-size: {instruction_style["font-size"]};
                        color: {instruction_style["color"]};
                    }}
                """
        self.instruction_label.setStyleSheet(instruction_stylesheet)
        self.add_shadow(self.instruction_label, **instruction_style["shadow"])

        # Recovery phrase labels
        phrase_label_style = style["phrase_label"]
        phrase_label_stylesheet = self.build_phrase_stylesheet(
            phrase_label_style, "border-color"
        )
        for label in self.recovery_labels:
            label.setStyleSheet(phrase_label_stylesheet)
            if phrase_label_style.get("shadow"):
                self.add_shadow(label, **phrase_label_style["shadow"])
            else:
                label.setGraphicsEffect(None)

        # Theme switch buttons
        theme_switch = style["theme_switch"]
        container_style = theme_switch["container"]
        button_style = theme_switch["button"]

        container_stylesheet = f"""
                QWidget {{
                    border-width: {container_style["border-width"]};
                    border-radius: {container_style["border-radius"]};
                    border-style: {container_style["border-style"]};
                    border-color: {container_style["border-color"]};
                    max-height: {container_style["height"]};
                    min-height: {container_style["height"]};
                }}
            """
        self.theme_container.setStyleSheet(container_stylesheet)
        self.add_shadow(self.theme_container, **container_style["shadow"])

        button_stylesheet = f"""
                        QPushButton {{
                            color: {button_style["color"]};
                            font-family: {button_style["font-family"]};
                            border-color: {button_style["border-color"]};
                            border-radius: {button_style["border-radius"]};
                            font-size: {button_style["font-size"]};
                            font-weight: {button_style["font-weight"]};
                            padding-left: {button_style["padding-left"]};
                            padding-right: {button_style["padding-right"]};
                            max-height: {button_style["height"]};
                            min-height: {button_style["height"]};
                        }}
                        QPushButton:hover {{
                            background-color: {button_style["hover-background-color"]};
                        }}
                        QPushButton:checked {{
                            color: {button_style["checked-color"]};
                            background-color: {button_style["checked-background-color"]};
                            border-style: {button_style["checked-border-style"]};
                            border-color: {button_style["checked-border-color"]};
                        }}
                    """
        for button in self.theme_group.buttons():
            button.setStyleSheet(button_stylesheet)

        # Back button
        back_button_style = style["back_button"]
        back_button_stylesheet = f"""
                QPushButton {{
                    background-color: {back_button_style["background-color"]};
                    border-width: {back_button_style["border-width"]};
                    border-color: {back_button_style["border-color"]};
                    border-style: {back_button_style["border-style"]};
                    border-radius: {back_button_style["border-radius"]};
                    font-family: {back_button_style["font-family"]};
                    font-size: {back_button_style["font-size"]};   
                    font-weight: {back_button_style["font-weight"]};
                    text-align: {back_button_style["text-align"]};
                    color: {back_button_style["color"]};
                }}
                QPushButton:hover {{
                    background-color: {back_button_style["hover-background-color"]};
                }}
                QPushButton:pressed {{
                    background-color: {back_button_style["pressed-background-color"]};
                }}
            """
        self.back_button.setStyleSheet(back_button_stylesheet)
        self.add_shadow(self.back_button, **back_button_style["shadow"])

        # Continue button
        self.continue_validation()

        # Footer label
        footer_style = style["footer"]
        footer_stylesheet = f"""
                        QLabel {{
                            color: {footer_style["color"]};
                            font-family: {footer_style["font-family"]};
                            font-weight: {footer_style["font-weight"]};
                            font-size: {footer_style["font-size"]};
                        }}
                """

        self.footer_label.setStyleSheet(footer_stylesheet)

        self.error_label.setText("")

    def continue_validation(self):
        self.continue_button.setEnabled(False)
        continue_button_style = self.styles[self.current_style]["continue_button"]
        continue_stylesheet = f"""
                            QPushButton {{
                                background-color: {continue_button_style['disabled-background-color']};
                                border: {continue_button_style['disabled-border']};
                                border-radius: {continue_button_style['border-radius']};
                                color: {continue_button_style['disabled-color']};
                                font-family: {continue_button_style['font-family']};
                                font-weight: {continue_button_style['font-weight']};
                                font-size: {continue_button_style['font-size']};
                            }}
                            QPushButton:hover {{
                                background-color: {continue_button_style['disabled-hover-background-color']};
                            }}
                            QPushButton:pressed {{
                                background-color: {continue_button_style['disabled-pressed-background-color']};
                            }}
                        """
        shadow = continue_button_style["disabled-shadow"]

        empty = False
        for label in self.recovery_labels:
            if not label.text().strip():
                empty = True
            phrases = [text.strip() for text in label.text().split() if text.strip()]
            if len(phrases) == 12:
                empty = False
                for phrase, phrase_label in zip(phrases, self.recovery_labels):
                    phrase_label.setText(phrase)
                break

        if not empty:
            self.continue_button.setEnabled(True)
            continue_stylesheet = f"""
                                QPushButton {{
                                    background-color: {continue_button_style['background-color']};
                                    border-width: {continue_button_style['border-width']};
                                    border-radius: {continue_button_style['border-radius']};
                                    color: {continue_button_style['color']};
                                    font-family: {continue_button_style['font-family']};
                                    font-weight: {continue_button_style['font-weight']};
                                    font-size: {continue_button_style['font-size']};
                                    border-style: {continue_button_style['border-style']};
                                    border-color: {continue_button_style['border-color']};
                                }}
                                QPushButton:hover {{
                                    background-color: {continue_button_style['hover-background-color']};
                                }} 
                                QPushButton:pressed {{
                                    background-color: {continue_button_style['pressed-background-color']};
                                }}
                            """
            shadow = continue_button_style["shadow"]

        self.continue_button.setStyleSheet(continue_stylesheet)
        self.add_shadow(self.continue_button, **shadow)

    def handle_continue(self):
        input_phrase = [
            label.text().strip()
            for label in self.recovery_labels
            if label.text().strip()
        ]
        user_phrase = self.from_user_db(self.username, ["recovery_code"])
        if (
            len(input_phrase) != 12
            or not user_phrase
            or not bcrypt.checkpw(
                " ".join(input_phrase).encode(), user_phrase[0].encode()
            )
        ):
            error_label_style = self.styles[self.current_style]["error_label"]
            phrase_label_style = self.styles[self.current_style]["phrase_label"]
            self.error_label.setText(self.current_dict["error"])
            error_label_stylesheet = f"""
                        QLabel {{
                            color: {error_label_style["color"]};
                            font-family: {error_label_style["font-family"]};
                            font-weight: {error_label_style["font-weight"]};
                            font-size: {error_label_style["font-size"]};
                        }}
                    """
            phrase_label_stylesheet = self.build_phrase_stylesheet(
                phrase_label_style, "error-border-color"
            )
            self.error_label.setStyleSheet(error_label_stylesheet)
            for label in self.recovery_labels:
                label.setStyleSheet(phrase_label_stylesheet)
            return

        self.open_password_recovery_window()

    def open_password_recovery_window(self):
        self.continue_button.setEnabled(False)
        self.back_button.setEnabled(False)

        self.password_recovery_window = PasswordRecoveryWindow(
            self.current_lang, self.current_style, self.username
        )
        self.password_recovery_window.show()
        self.close()

    def open_forgot_password_window(self):
        self.back_button.setEnabled(False)
        self.forgot_password_window = ForgotPasswordWindow(
            self.current_lang, self.current_style, self.username
        )
        self.forgot_password_window.show()
        self.close()

    @staticmethod
    def build_phrase_stylesheet(phrase_label_style: dict, border_color_key: str):
        return f"""
                    QLineEdit {{
                        background-color: {phrase_label_style["background-color"]};
                        border-width: {phrase_label_style["border-width"]};
                        border-radius: {phrase_label_style["border-radius"]};
                        color: {phrase_label_style["color"]};
                        font-size: {phrase_label_style["font-size"]};
                        font-family: {phrase_label_style["font-family"]};
                        font-weight: {phrase_label_style["font-weight"]};
                        border-style: {phrase_label_style["border-style"]};
                        border-color: {phrase_label_style[border_color_key]};           
                    }}
                """

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.instruction_label.setText(self.current_dict["instruction"])
        for theme, button in zip(self.styles, self.theme_group.buttons()):
            button.setText(self.current_dict[f"theme_{theme}"])
        self.back_button.setText(self.current_dict["back"])
        self.continue_button.setText(self.current_dict["continue"])
        self.footer_label.setText(self.current_dict["footer"])
        self.error_label.setText("")
