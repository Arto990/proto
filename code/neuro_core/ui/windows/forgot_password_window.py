from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QButtonGroup,
)

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.login_window import LoginWindow


class ForgotPasswordWindow(LoginWindow, QMainWindow):
    def __init__(self, current_lang: str, current_style: str, username: str):
        QMainWindow.__init__(self)

        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"
        self.username = username

        self.languages = self.load_languages("forgot_password_window")
        self.styles = self.load_styles("forgot_password_window")

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

        self.layout.addSpacing(10)

        # кнопка фрази
        self.phrase_button = QPushButton()
        self.phrase_button.clicked.connect(self.open_forgot_password_phrase_window)
        self.phrase_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.phrase_button.setFixedSize(320, 40)
        self.layout.addWidget(
            self.phrase_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(10)

        self.scan_qr_button = QPushButton()
        self.scan_qr_button.clicked.connect(self.open_forgot_password_qr_window)
        self.scan_qr_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_qr_button.setFixedSize(320, 40)
        self.layout.addWidget(
            self.scan_qr_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(85)

        # Створюємо контейнер для перемикача тем
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

        # Кнопка назад
        self.back_button = QPushButton()
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setFixedSize(320, 48)
        self.back_button.clicked.connect(self.open_login_window)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.layout.addSpacing(10)

        # Напис унікальності дизайну
        self.footer_label = QLabel()
        self.layout.addWidget(
            self.footer_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addStretch()

    def apply_style(self):
        style = self.styles[self.current_style]

        # Фонове зображення
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

        # Стиль логотипу
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

        # Стиль градієнтного тексту
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

        # Інструкція
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

        # Кнопка фрази
        phrase_method_style = style["phrase_method_button"]
        phrase_method_icon = resource_path(phrase_method_style["icon-path"])
        self.phrase_button.setIcon(QIcon(phrase_method_icon))
        phrase_method_stylesheet = f"""
            QPushButton {{
                background-color: {phrase_method_style["background-color"]};
                border-width: {phrase_method_style["border-width"]};
                border-color: {phrase_method_style["border-color"]};
                border-style: {phrase_method_style["border-style"]};
                border-radius: {phrase_method_style["border-radius"]};
                padding-left: {phrase_method_style["padding-left"]};
                font-family: {phrase_method_style["font-family"]};
                font-weight: {phrase_method_style["font-weight"]};
                font-size: {phrase_method_style["font-size"]};   
                text-align: {phrase_method_style["text-align"]};
                color: {phrase_method_style["color"]};
            }}
            QPushButton:hover {{
                background-color: {phrase_method_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {phrase_method_style["pressed-background-color"]};
            }}
        """
        self.phrase_button.setStyleSheet(phrase_method_stylesheet)
        self.add_shadow(self.phrase_button, **phrase_method_style["shadow"])

        # Кнопка QR
        qr_method_style = style["qr_method_button"]
        qr_method_icon = resource_path(qr_method_style["icon-path"])
        self.scan_qr_button.setIcon(QIcon(qr_method_icon))
        qr_method_stylesheet = f"""
            QPushButton {{
                background-color: {qr_method_style["background-color"]};
                border-width: {qr_method_style["border-width"]};
                border-color: {qr_method_style["border-color"]};
                border-style: {qr_method_style["border-style"]};
                border-radius: {qr_method_style["border-radius"]};
                padding-left: {qr_method_style["padding-left"]};
                font-family: {qr_method_style["font-family"]};
                font-weight: {qr_method_style["font-weight"]};
                font-size: {qr_method_style["font-size"]};   
                text-align: {qr_method_style["text-align"]};
                color: {qr_method_style["color"]};
            }}
            QPushButton:hover {{
                background-color: {qr_method_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {qr_method_style["pressed-background-color"]};
            }}
        """
        self.scan_qr_button.setStyleSheet(qr_method_stylesheet)
        self.add_shadow(self.scan_qr_button, **qr_method_style["shadow"])

        # Перемикач тем
        # Стиль для перемикача тем
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

        # Кнопка    назад
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

        # Стиль для підпису
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

    def open_forgot_password_qr_window(self):
        self.scan_qr_button.setEnabled(False)
        from neuro_core.ui.windows.forgot_password_qr_window import (
            ForgotPasswordQRWindow,
        )

        self.forgot_password_qr_window = ForgotPasswordQRWindow(
            self.current_lang, self.current_style, self.username
        )
        self.forgot_password_qr_window.show()
        self.close()

    def open_login_window(self):
        self.back_button.setEnabled(False)
        self.login_window = LoginWindow(self.current_lang, self.current_style)
        self.login_window.show()
        self.close()

    def open_forgot_password_phrase_window(self):
        self.phrase_button.setEnabled(False)
        from neuro_core.ui.windows.forgot_password_phrase_window import (
            ForgotPasswordPhraseWindow,
        )

        self.forgot_password_phrase_window = ForgotPasswordPhraseWindow(
            self.current_lang, self.current_style, self.username
        )
        self.forgot_password_phrase_window.show()
        self.close()

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.instruction_label.setText(self.current_dict["instruction"])
        self.phrase_button.setText(self.current_dict["phrase_method"])
        self.scan_qr_button.setText(self.current_dict["qr_method"])
        for theme, button in zip(self.styles, self.theme_group.buttons()):
            button.setText(self.current_dict[f"theme_{theme}"])
        self.back_button.setText(self.current_dict["back"])
        self.footer_label.setText(self.current_dict["footer"])
