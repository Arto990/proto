import json
import locale
import logging
import os
import re
import sqlite3
from datetime import datetime

import bcrypt
import langcodes
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush, QColor, QFontDatabase, QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QButtonGroup,
    QGraphicsDropShadowEffect,
)

from neuro_core.config.config import FULL_LANG_NAMES
from neuro_core.tools.utils import resource_path


class LoginWindow(QMainWindow):
    def __init__(self, current_lang: str = None, current_style: str = None):
        super().__init__()
        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"
        self.username = "N/A"
        self.write_log(
            self.log_file_path,
            self.module_name,
            "WELCOME_MODULE_LAUNCHED",
            self.username,
            "INFO",
            "Interface launched",
        )

        self.load_fonts()
        self.languages = self.load_languages("login_window")
        self.styles = self.load_styles("login_window")

        self.current_lang = (
            self.get_default_lang() if not current_lang else current_lang
        )
        self.current_dict = self.languages[self.current_lang]
        self.current_style = "dark" if not current_style else current_style

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
        self.layout.addSpacing(5)

        # Dedication label
        self.dedication1_label = QLabel()
        self.layout.addWidget(
            self.dedication1_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        # self.dedication2_label = QLabel()
        # self.layout.addWidget(
        #     self.dedication2_label, alignment=Qt.AlignmentFlag.AlignHCenter
        # )
        self.dedication2_label = QLabel()
        self.layout.addWidget(
            self.dedication2_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(5)

        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(5)

        # Поле логіну
        self.username_input = QLineEdit()
        self.username_input.textChanged.connect(self.check_login_validity)
        self.layout.addWidget(
            self.username_input, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(5)

        self.username_error_label = QLabel()
        self.username_error_label.setFixedHeight(10)
        self.username_error_label.setContentsMargins(40, 0, 0, 0)
        self.layout.addWidget(
            self.username_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Поле паролю
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self.check_login_validity)
        self.layout.addWidget(
            self.password_input, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Повідомдення про помилку та Кнопка "Mot de passe oublié"
        pass_error_and_forgot_layout = QHBoxLayout()
        pass_error_and_forgot_layout.setContentsMargins(40, 0, 40, 0)

        self.password_error_label = QLabel()
        pass_error_and_forgot_layout.addWidget(
            self.password_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        pass_error_and_forgot_layout.addStretch()

        self.forgot_password_button = QPushButton()
        self.forgot_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot_password_button.clicked.connect(self.handle_forgot_password)
        pass_error_and_forgot_layout.addWidget(self.forgot_password_button)
        self.layout.addLayout(pass_error_and_forgot_layout)
        self.layout.addSpacing(10)

        # Кнопка зміни мови
        self.language_combo = QComboBox()
        self.language_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.language_combo.addItem(self.current_dict["language"])
        self.language_combo.model().item(0).setEnabled(False)
        self.language_combo.addItems(FULL_LANG_NAMES.keys())
        self.language_combo.currentTextChanged.connect(
            lambda lang: self.change_language(
                lang,
                self.log_file_path,
                self.module_name,
                f"LANG_{lang}".upper(),
                self.username,
                "INFO",
                f"Interface language: {lang.upper()}",
            )
        )
        self.layout.addWidget(
            self.language_combo, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(10)

        # Кнопка реєстрації та вибору теми
        self.reg_theme_layout = QHBoxLayout()
        self.reg_theme_layout.setContentsMargins(40, 0, 40, 0)

        self.reg_button = QPushButton()
        self.reg_button.clicked.connect(self.open_sign_up_window)
        self.reg_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reg_theme_layout.addWidget(
            self.reg_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Створюємо контейнер для перемикача тем
        self.theme_container = QWidget()  # Новий віджет-контейнер
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
            self.theme_switch_layout.addWidget(button)  # Додаємо кнопку до макета

        # Додаємо контейнер із кнопками тем до основного макета
        self.reg_theme_layout.addWidget(
            self.theme_container, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(self.reg_theme_layout)
        self.layout.addSpacing(23)

        # Кнопка входу
        self.login_button = QPushButton()
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        self.layout.addWidget(
            self.login_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(15)

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

        # Dedication text style
        dedication_style = style["dedication_label"]
        dedication_stylesheet = f"""
            QLabel {{
                min-height: {dedication_style["height"]};
                max-height: {dedication_style["height"]};
                font-family: {dedication_style["font-family"]};
                font-weight: {dedication_style["font-weight"]};
                color: {dedication_style["color"]};
                font-size: {dedication_style["font-size"]};
            }}
        """
        self.dedication1_label.setStyleSheet(dedication_stylesheet)
        self.add_shadow(self.dedication1_label, **dedication_style["shadow"])

        self.dedication2_label.setStyleSheet(dedication_stylesheet)
        self.add_shadow(self.dedication2_label, **dedication_style["shadow"])

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

        # Стилі для полів вводу
        input_style = style["input"]
        input_stylesheet = f"""
            QLineEdit {{
                background-color: {input_style["background-color"]};
                border-width: {input_style["border-width"]};
                border-radius: {input_style["border-radius"]};
                padding: {input_style["padding"]};
                color: {input_style["color"]};
                font-family: {input_style["font-family"]};
                font-weight: {input_style["font-weight"]};
                font-size: {input_style["font-size"]};
                border-style: {input_style["border-style"]};
                border-color: {input_style["border-color"]};
            }}
        """
        self.username_input.setFixedSize(320, 40)
        self.username_input.setStyleSheet(input_stylesheet)
        self.password_input.setFixedSize(320, 40)
        self.password_input.setStyleSheet(input_stylesheet)

        if input_style.get("shadow"):
            self.add_shadow(self.username_input, **input_style["shadow"])
            self.add_shadow(self.password_input, **input_style["shadow"])
        else:
            self.username_input.setGraphicsEffect(None)
            self.password_input.setGraphicsEffect(None)

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.username_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.username_input.setPalette(placeholder_palette)
        self.password_input.setPalette(placeholder_palette)

        # Стиль кнопки "Mot de passe oublié"
        forgot_style = style["forgot_password"]
        button_stylesheet = f"""
            QPushButton {{
                border: {forgot_style["border"]};
                color: {forgot_style["color"]};
                font-family: {forgot_style["font-family"]};
                font-weight: {forgot_style["font-weight"]};
                font-size: {forgot_style["font-size"]};
                padding: {forgot_style["padding"]};
                height: {forgot_style["height"]};
            }}
            QPushButton:hover {{
                color: {forgot_style["hover-color"]};
            }}
        """
        self.forgot_password_button.setStyleSheet(button_stylesheet)
        self.add_shadow(self.forgot_password_button, **forgot_style["shadow"])

        # Стиль для комбобоксу
        language_combo = style["language_combo"]
        language_stylesheet = self.build_combo_stylesheet(
            "border-color", language_combo
        )
        language_stylesheet += f"""
            QComboBox {{
                font-family: {language_combo["font-family"]};
                font-weight: {language_combo["font-weight"]};
            }}
        """
        self.language_combo.setFixedSize(320, 40)
        self.language_combo.setStyleSheet(language_stylesheet)
        if language_combo.get("shadow"):
            self.add_shadow(self.language_combo, **language_combo["shadow"])
        else:
            self.language_combo.setGraphicsEffect(None)

        # Стиль для кнопки реєстрації
        reg_button_style = style["register_button"]
        reg_button_stylesheet = f"""
            QPushButton {{
                background-color: {reg_button_style["background-color"]};
                border-width: {reg_button_style["border-width"]};
                border-radius: {reg_button_style["border-radius"]};
                padding-left: {reg_button_style["padding-left"]};
                padding-right: {reg_button_style["padding-right"]};
                height: {reg_button_style["height"]};
                min-width: {reg_button_style["min-width"]};
                color: {reg_button_style["color"]};
                font-family: {reg_button_style["font-family"]};
                font-weight: {reg_button_style["font-weight"]};
                font-size: {reg_button_style["font-size"]};
                border-style: {reg_button_style["border-style"]};
                border-color: {reg_button_style["border-color"]};  
            }}
            QPushButton:hover {{
                background-color: {reg_button_style["hover-background-color"]};  
            }}
            QPushButton:pressed {{
                background-color: {reg_button_style["pressed-background-color"]};
            }}
        """
        self.reg_button.setStyleSheet(reg_button_stylesheet)
        self.add_shadow(self.reg_button, **reg_button_style["shadow"])

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
                font-weight: {button_style["font-weight"]};
                border-color: {button_style["border-color"]};
                border-radius: {button_style["border-radius"]};
                font-size: {button_style["font-size"]};
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

        # Стиль для кнопки входу
        self.check_login_validity()
        self.login_button.setFixedSize(320, 48)

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

        # Прибираємо повідомлення про помилки
        self.username_error_label.setText("")
        self.password_error_label.setText("")

    def open_sign_up_window(self):
        from neuro_core.ui.windows.sign_up_window import SignUpWindow

        self.reg_button.setEnabled(False)
        self.sign_up_window = SignUpWindow(self.current_lang, self.current_style)
        self.sign_up_window.show()
        self.close()

    def handle_login(self):
        style = self.styles[self.current_style]
        input_style = style["input"]
        error_label_style = style["error_label"]

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        is_valid = True

        error_label_stylesheet = f"""
            QLabel {{
                color: {error_label_style["color"]};\
                font-family: {error_label_style["font-family"]};
                font-weight: {error_label_style["font-weight"]};
                font-size: {error_label_style["font-size"]};
            }}
        """

        # ===== Перевірка логіну =====
        if len(username) < 3:
            self.username_error_label.setText(self.current_dict["username_too_short"])
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        elif not re.fullmatch(r"[a-zA-Z0-9_.@-]+", username):
            self.username_error_label.setText(
                self.current_dict["username_invalid_chars"]
            )
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        else:
            self.username_error_label.setText("")
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # ===== Перевірка паролю =====
        if len(password) < 8:
            self.password_error_label.setText(self.current_dict["password_too_short"])
            self.password_error_label.setStyleSheet(error_label_stylesheet)
            self.password_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        else:
            self.password_error_label.setText("")
            self.password_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.username_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.username_input.setPalette(placeholder_palette)
        self.password_input.setPalette(placeholder_palette)

        self.username_error_label.setContentsMargins(40, 0, 0, 0)

        if not is_valid:
            return

        # ===== Перевірка користувача =====
        user_password = self.from_user_db(username, ["password"])
        if not user_password or not bcrypt.checkpw(
            password.encode(), user_password[0].encode()
        ):
            self.write_log(
                self.log_file_path,
                self.module_name,
                "WELCOME_USER_UNKNOWN",
                self.username,
                "INFO",
                "Unknown user",
            )
            self.password_error_label.setText(self.current_dict["invalid_credentials"])
            self.password_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.password_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )

            placeholder_color = QColor(input_style["color"])
            placeholder_palette = self.username_input.palette()
            placeholder_palette.setColor(
                QPalette.ColorRole.PlaceholderText, placeholder_color
            )
            self.username_input.setPalette(placeholder_palette)
            self.password_input.setPalette(placeholder_palette)

            self.username_error_label.setContentsMargins(40, 0, 0, 0)
            return

        # ===== Успіх =====
        print("Login successful")
        print()
        print(f"User data: {self.from_user_db(username, ['*'])}")

        self.write_log(
            self.log_file_path,
            self.module_name,
            "WELCOME_USER_IDENTIFIED",
            username,
            "INFO",
            "Person recognized",
        )

    def handle_forgot_password(self):
        style = self.styles[self.current_style]
        input_style = style["input"]
        error_label_style = style["error_label"]

        username = self.username_input.text().strip()

        is_valid = True

        error_label_stylesheet = f"""
                    QLabel {{
                        color: {error_label_style["color"]};\
                        font-family: {error_label_style["font-family"]};
                        font-size: {error_label_style["font-size"]};
                        font-weight: {error_label_style["font-weight"]};
                    }}
                """

        # ===== Перевірка логіну =====
        if len(username) < 3:
            self.username_error_label.setText(self.current_dict["username_too_short"])
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        elif not re.fullmatch(r"[a-zA-Z0-9_.@-]+", username):
            self.username_error_label.setText(
                self.current_dict["username_invalid_chars"]
            )
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        elif not self.from_user_db(username, ["username"]):
            self.write_log(
                self.log_file_path,
                self.module_name,
                "WELCOME_USER_UNKNOWN",
                self.username,
                "INFO",
                "Unknown user",
            )
            self.username_error_label.setText(self.current_dict["user_not_found"])
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        else:
            self.username_error_label.setText("")
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.username_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.username_input.setPalette(placeholder_palette)
        self.username_error_label.setContentsMargins(40, 0, 0, 0)

        if not is_valid:
            return

        from neuro_core.ui.windows.forgot_password_window import ForgotPasswordWindow

        self.forgot_password_button.setEnabled(False)
        self.forgot_password_window = ForgotPasswordWindow(
            self.current_lang, self.current_style, username
        )
        self.forgot_password_window.show()
        self.close()

    def check_login_validity(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        login_button_style = self.styles[self.current_style]["login_button"]

        is_username_valid = len(username) >= 3 and bool(
            re.fullmatch(r"[a-zA-Z0-9_.@-]+", username)
        )
        is_password_valid = len(password) >= 8

        login_valid = is_username_valid and is_password_valid

        if login_valid:
            login_stylesheet = f"""
                QPushButton {{
                    background-color: {login_button_style['background-color']};
                    border-width: {login_button_style['border-width']};
                    border-radius: {login_button_style['border-radius']};
                    color: {login_button_style['color']};
                    font-family: {login_button_style['font-family']};
                    font-weight: {login_button_style['font-weight']};
                    font-size: {login_button_style['font-size']};
                    border-style: {login_button_style['border-style']};
                    border-color: {login_button_style['border-color']};
                }}
                QPushButton:hover {{
                    background-color: {login_button_style['hover-background-color']};
                }} 
                QPushButton:pressed {{
                    background-color: {login_button_style['pressed-background-color']};
                }}
            """
            shadow = login_button_style["shadow"]
        else:
            login_stylesheet = f"""
                QPushButton {{
                    background-color: {login_button_style['disabled-background-color']};
                    border: {login_button_style['disabled-border']};
                    border-radius: {login_button_style['border-radius']};
                    color: {login_button_style['disabled-color']};
                    font-family: {login_button_style['font-family']};
                    font-weight: {login_button_style['font-weight']};
                    font-size: {login_button_style['font-size']};
                }}
                QPushButton:hover {{
                    background-color: {login_button_style['disabled-hover-background-color']};
                }}
                QPushButton:pressed {{
                    background-color: {login_button_style['disabled-pressed-background-color']};
                }}
            """
            shadow = login_button_style["disabled-shadow"]

        self.login_button.setStyleSheet(login_stylesheet)
        self.add_shadow(self.login_button, **shadow)

    def get_default_lang(self):
        locale.setlocale(locale.LC_ALL, "")
        lang = locale.getlocale()[0]

        if lang is not None:
            lang = lang.split("_")[0].lower()

            if not langcodes.Language(lang).is_valid():
                try:
                    lang = langcodes.find(lang).language
                except LookupError:
                    lang = "en"
        else:
            lang = "en"

        if lang not in self.languages:
            lang = "en"

        fullname_lang = next((k for k, v in FULL_LANG_NAMES.items() if v == lang), None)

        self.write_log(
            self.log_file_path,
            "Welcome",
            f"LANG_{lang}".upper(),
            self.username,
            "INFO",
            f"Set default language: {fullname_lang.upper() if fullname_lang else lang.upper()}",
        )

        return lang

    @staticmethod
    def write_log(
        log_file: str,
        module_name: str,
        action: str,
        username: str,
        state: str,
        message: str,
    ):
        now = datetime.now()
        log_file = log_file.replace("<date>", now.strftime("%Y-%m-%d"))
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(message)s",
            datefmt="%Y-%m-%d_%H:%M:%S",
            handlers=[logging.FileHandler(log_file, encoding="utf-8")],
        )
        log_message = f"{module_name} | {action} | {username} | {state} | {message}"
        logging.info(log_message)

    def from_user_db(self, username: str, fields: list[str]):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    fullname TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT NOT NULL,
                    lang TEXT NOT NULL,
                    style TEXT NOT NULL,
                    modules TEXT NOT NULL,
                    email TEXT,
                    phone_number TEXT,
                    account_state TEXT DEFAULT 'active',
                    access_level TEXT NOT NULL,
                    recovery_code TEXT NOT NULL,
                    created_at DATE DEFAULT CURRENT_DATE
                )
            """
        )

        cursor.execute(
            f"SELECT {", ".join(fields)} FROM users WHERE username = ?", (username,)
        )
        user_data = cursor.fetchone()
        conn.commit()
        conn.close()
        return user_data

    def to_user_db(
        self,
        username: str,
        password: str,
        fullname: str,
        role: str,
        department: str,
        modules: list,
        account_state: str,
        access_level: str,
        recovery_code: str,
        email: str = None,
        phone_number: str = None,
    ):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    fullname TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT NOT NULL,
                    lang TEXT NOT NULL,
                    style TEXT NOT NULL,
                    modules TEXT NOT NULL,
                    email TEXT,
                    phone_number TEXT,
                    account_state TEXT DEFAULT 'active',
                    access_level TEXT NOT NULL,
                    recovery_code TEXT NOT NULL,
                    created_at DATE DEFAULT CURRENT_DATE
                )
            """
        )
        modules = ",".join(modules)
        cursor.execute(
            """
                INSERT INTO users (username, password, fullname, role, department, lang, style, modules, email, phone_number, account_state, access_level, recovery_code)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                username,
                password,
                fullname,
                role,
                department,
                self.current_lang,
                self.current_style,
                modules,
                email,
                phone_number,
                account_state,
                access_level,
                recovery_code,
            ),
        )
        conn.commit()
        conn.close()

    def change_language(
        self,
        lang: str,
        log_file: str,
        module_name: str,
        action: str,
        username: str,
        state: str,
        message: str,
    ):
        self.current_lang = FULL_LANG_NAMES[lang]
        self.current_dict = self.languages[self.current_lang]
        self.update_texts()
        self.write_log(log_file, module_name, action, username, state, message)

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])

        self.dedication1_label.setText(self.current_dict["dedication1"])
        self.dedication2_label.setText(self.current_dict["dedication2"])

        self.gradient_label.setText(self.current_dict["slogan"])
        self.username_input.setPlaceholderText(self.current_dict["username"])
        self.password_input.setPlaceholderText(self.current_dict["password"])
        self.forgot_password_button.setText(self.current_dict["forgot_password"])
        self.language_combo.setItemText(0, self.current_dict["language"])
        self.reg_button.setText(self.current_dict["register"])
        for theme, button in zip(self.styles, self.theme_group.buttons()):
            button.setText(self.current_dict[f"theme_{theme}"])
        self.login_button.setText(self.current_dict["login"])
        self.footer_label.setText(self.current_dict["footer"])
        self.username_error_label.setText("")
        self.password_error_label.setText("")
        style = self.styles[self.current_style]
        input_style = style["input"]
        input_stylesheet = self.build_input_stylesheet("border-color", input_style)
        self.username_input.setStyleSheet(input_stylesheet)
        self.password_input.setStyleSheet(input_stylesheet)
        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.username_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.username_input.setPalette(placeholder_palette)
        self.password_input.setPalette(placeholder_palette)

    def change_theme(
        self,
        theme: str,
        log_file: str,
        module_name: str,
        action: str,
        username: str,
        state: str,
        message: str,
    ):
        self.current_style = theme.lower()
        self.apply_style()
        self.write_log(log_file, module_name, action, username, state, message)

    @staticmethod
    def add_shadow(
        widget,
        x_offset: int,
        y_offset: int,
        color: list[int],
        blur: int = 8,
    ):
        color = QColor(*color)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(x_offset, y_offset)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def load_languages(window_name: str) -> dict:
        languages = {}
        lang_dir = resource_path("neuro_core/config/langs")
        for filename in os.listdir(lang_dir):
            if filename.endswith(".json"):
                lang_key = filename.split(".")[0]
                with open(os.path.join(lang_dir, filename), "r", encoding="utf-8") as f:
                    languages[lang_key] = json.load(f)[window_name]
        return languages

    @staticmethod
    def load_styles(window_name: str) -> dict:
        styles = {}
        style_dir = resource_path(f"neuro_core/config/styles/{window_name}")
        for filename in os.listdir(style_dir):
            if filename.endswith(".json"):
                style_key = filename.split(".")[0]
                with open(
                    os.path.join(style_dir, filename), "r", encoding="utf-8"
                ) as f:
                    styles[style_key] = json.load(f)
        return styles

    @staticmethod
    def build_input_stylesheet(border_color_key: str, input_style: dict):
        return f"""
                QLineEdit {{
                    background-color: {input_style["background-color"]};
                    border-width: {input_style["border-width"]};
                    border-radius: {input_style["border-radius"]};
                    padding: {input_style["padding"]};
                    color: {input_style["color"]};
                    font-family: {input_style["font-family"]};
                    font-weight: {input_style["font-weight"]};
                    font-size: {input_style["font-size"]};
                    border-style: {input_style["border-style"]};
                    border-color: {input_style[border_color_key]};
                }}
            """

    @staticmethod
    def build_combo_stylesheet(border_color_key, combo_style):
        return f"""
                    QComboBox {{
                        background-color: {combo_style["background-color"]};
                        border-width: {combo_style["border-width"]};
                        border-radius: {combo_style["border-radius"]};
                        padding-left: {combo_style["padding-left"]};
                        color: {combo_style["color"]};
                        font-family: {combo_style["font-family"]};
                        font-weight: {combo_style["font-weight"]};
                        font-size: {combo_style["font-size"]};
                        border-style: {combo_style["border-style"]};
                        border-color: {combo_style[border_color_key]};
                    }}
                    QComboBox::drop-down {{
                        subcontrol-origin: {combo_style["drop-down-origin"]};
                        subcontrol-position: {combo_style["drop-down-position"]};
                        width: {combo_style["drop-down-width"]};
                        border: {combo_style["drop-down-border"]};
                    }}
                    QComboBox::down-arrow {{
                        image: url({resource_path(combo_style["arrow-image-path"]).replace("\\", "/")});
                        width: {combo_style["arrow-width"]};
                        height: {combo_style["arrow-height"]};
                    }}
                    QComboBox QAbstractItemView {{
                        background-color: {combo_style["drop-background-color"]};
                        color: {combo_style["color"]};
                        selection-color: {combo_style["color"]};
                        padding: {combo_style["drop-padding"]};
                        border-width: {combo_style["drop-border-width"]};
                        border-radius: {combo_style["drop-border-radius"]};
                        border-style: {combo_style["border-style"]};
                        border-color: {combo_style[border_color_key]};
                    }}
                    QComboBox::hover {{
                        background-color: {combo_style["hover-background-color"]};
                    }}
                """

    def load_fonts(self):
        fonts_dir = resource_path("neuro_core/config/fonts")
        for font in os.listdir(fonts_dir):
            if font.endswith(".ttf"):
                font_path = os.path.join(fonts_dir, font)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    self.write_log(
                        self.log_file_path,
                        self.module_name,
                        "FONT_ERROR",
                        self.username,
                        "ERROR",
                        f"Failed to load font: {font}",
                    )
                else:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    self.write_log(
                        self.log_file_path,
                        self.module_name,
                        "FONT_LOADED",
                        self.username,
                        "INFO",
                        f"Font loaded: {font}, Families: {families}",
                    )

    @staticmethod
    def set_icon(lineedit, position, icon_path=None, main_icon=False):
        i = 0 if main_icon else 1
        for action in lineedit.actions()[i:]:
            lineedit.removeAction(action)
        if icon_path:
            action = QAction(QIcon(icon_path), "", lineedit)
            lineedit.addAction(action, position)
