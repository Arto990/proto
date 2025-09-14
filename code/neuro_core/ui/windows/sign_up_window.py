import re

import bcrypt
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush, QColor
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QPushButton,
    QButtonGroup,
    QCompleter,
)

from neuro_core.config.config import FULL_LANG_NAMES, mnemo
from neuro_core.tools.utils import resource_path, load_professions
from neuro_core.ui.windows.login_window import LoginWindow


class SignUpWindow(LoginWindow, QMainWindow):
    def __init__(self, current_lang: str, current_style: str):
        QMainWindow.__init__(self)

        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"
        self.username = "N/A"

        self.languages = self.load_languages("sign_up_window")
        self.styles = self.load_styles("sign_up_window")

        self.professions_by_language = load_professions()

        self.current_lang = current_lang
        self.current_style = current_style
        self.current_dict = self.languages[self.current_lang]

        icon_path = resource_path("neuro_core/config/icons/main.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(500, 620)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 15, 0, 0)

        self.setup_ui()
        self.apply_style()
        self.update_texts()

    def setup_ui(self):
        # Logo
        self.logo_label = QLabel()
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addSpacing(7)

        # Gradient label
        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(20)

        # Login and password fields
        login_password_layout = QHBoxLayout()
        login_password_layout.setContentsMargins(40, 0, 40, 0)

        # Login field
        self.username_input = QLineEdit()
        self.username_input.setFixedSize(203, 27)
        login_password_layout.addWidget(
            self.username_input, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Password field
        self.password_input = QLineEdit()
        self.password_input.setFixedSize(203, 27)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_password_layout.addWidget(
            self.password_input, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(login_password_layout)

        # Error login and password fields
        username_password_error_layout = QHBoxLayout()
        username_password_error_layout.setContentsMargins(40, 0, 40, 0)

        # Login error label
        self.username_error_label = QLabel()
        self.username_error_label.setFixedSize(203, 10)
        username_password_error_layout.addWidget(
            self.username_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Password error label
        self.password_error_label = QLabel()
        self.password_error_label.setFixedSize(203, 10)
        username_password_error_layout.addWidget(
            self.password_error_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(username_password_error_layout)

        # First name and last name fields
        firstname_lastname_layout = QHBoxLayout()
        firstname_lastname_layout.setContentsMargins(40, 0, 40, 0)

        # Username field
        self.first_name_input = QLineEdit()
        self.first_name_input.setFixedSize(203, 27)
        firstname_lastname_layout.addWidget(
            self.first_name_input, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Last name field
        self.last_name_input = QLineEdit()
        self.last_name_input.setFixedSize(203, 27)
        firstname_lastname_layout.addWidget(
            self.last_name_input, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(firstname_lastname_layout)

        # Error first name and last name fields
        firstname_lastname_error_layout = QHBoxLayout()
        firstname_lastname_error_layout.setContentsMargins(40, 0, 40, 0)

        # First name error label
        self.firstname_error_label = QLabel()
        self.firstname_error_label.setFixedSize(203, 10)
        firstname_lastname_error_layout.addWidget(
            self.firstname_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Last name error label
        self.lastname_error_label = QLabel()
        self.lastname_error_label.setFixedSize(203, 10)
        firstname_lastname_error_layout.addWidget(
            self.lastname_error_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(firstname_lastname_error_layout)

        # Department and role fields
        departament_role_layout = QHBoxLayout()
        departament_role_layout.setContentsMargins(40, 0, 40, 0)

        # Department field
        self.department_input = QLineEdit()
        self.department_input.setFixedSize(203, 27)
        departament_role_layout.addWidget(
            self.department_input, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.department_input.setCompleter(self.completer)

        # Role combo box
        self.role_combo = QComboBox()
        self.role_combo.setFixedSize(203, 27)
        self.role_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.role_combo.addItem(self.current_dict["role"])
        self.role_combo.model().item(0).setEnabled(False)
        self.role_combo.addItems(self.current_dict["roles"])
        departament_role_layout.addWidget(
            self.role_combo, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(departament_role_layout)

        # Error department and role fields
        department_role_error_layout = QHBoxLayout()
        department_role_error_layout.setContentsMargins(40, 0, 40, 0)

        # Error department label
        self.department_error_label = QLabel()
        self.department_error_label.setFixedSize(203, 10)
        department_role_error_layout.addWidget(
            self.department_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Error role label
        self.role_error_label = QLabel()
        self.role_error_label.setFixedSize(203, 10)
        department_role_error_layout.addWidget(
            self.role_error_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(department_role_error_layout)

        self.layout.addSpacing(5)

        # Optional information label
        self.optional_info_label = QLabel()
        self.optional_info_label.setContentsMargins(40, 0, 40, 0)
        self.optional_info_label.setFixedHeight(15)

        self.layout.addWidget(
            self.optional_info_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Layout for email and phone fields
        email_phone_layout = QHBoxLayout()
        email_phone_layout.setContentsMargins(40, 0, 40, 0)

        # Email field
        self.email_input = QLineEdit()
        self.email_input.setFixedSize(203, 27)
        email_phone_layout.addWidget(
            self.email_input, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Phone field
        self.phone_input = QLineEdit()
        self.phone_input.setFixedSize(203, 27)
        email_phone_layout.addWidget(
            self.phone_input, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(email_phone_layout)

        # Error email and phone fields
        email_phone_error_layout = QHBoxLayout()
        email_phone_error_layout.setContentsMargins(40, 0, 40, 0)

        # Email error label
        self.email_error_label = QLabel()
        self.email_error_label.setFixedSize(203, 10)
        email_phone_error_layout.addWidget(
            self.email_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Phone error label
        self.phone_error_label = QLabel()
        self.phone_error_label.setFixedSize(203, 10)
        email_phone_error_layout.addWidget(
            self.phone_error_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(email_phone_error_layout)

        self.layout.addSpacing(50)

        for field in [
            self.username_input,
            self.password_input,
            self.first_name_input,
            self.last_name_input,
            self.department_input,
            self.role_combo,
            self.email_input,
            self.phone_input,
        ]:
            field.installEventFilter(self)

        # Consent checkbox and privacy policy button
        consent_layout = QHBoxLayout()
        consent_layout.setContentsMargins(40, 0, 40, 0)

        # Consent checkbox
        self.consent_checkbox = QCheckBox()
        self.consent_checkbox.setFixedHeight(20)
        self.consent_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        consent_layout.addWidget(
            self.consent_checkbox, alignment=Qt.AlignmentFlag.AlignLeft
        )

        consent_layout.addSpacing(0)

        # Privacy policy button
        self.privacy_policy_button = QPushButton()
        self.privacy_policy_button.pressed.connect(self.open_privacy_policy)
        self.privacy_policy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.privacy_policy_button.setFixedHeight(20)
        consent_layout.addWidget(
            self.privacy_policy_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        consent_layout.addStretch()
        self.layout.addLayout(consent_layout)

        self.layout.addSpacing(10)

        # Combo box for language and sign up button
        language_sign_up_layout = QHBoxLayout()
        language_sign_up_layout.setContentsMargins(40, 0, 40, 0)

        # Language combo box
        self.language_combo = QComboBox()
        self.language_combo.setFixedSize(150, 27)
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

        language_sign_up_layout.addWidget(
            self.language_combo,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        )

        # Registration button
        self.sign_up_button = QPushButton()
        self.sign_up_button.pressed.connect(self.handle_sign_up)
        self.sign_up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sign_up_button.setFixedSize(220, 40)
        language_sign_up_layout.addWidget(
            self.sign_up_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.layout.addLayout(language_sign_up_layout)

        self.layout.addSpacing(5)

        # Layout for theme selection and login button
        theme_login_layout = QHBoxLayout()
        theme_login_layout.setContentsMargins(40, 0, 40, 0)

        # Theme selection container
        self.theme_container = QWidget()
        self.theme_container.setFixedHeight(24)
        self.theme_switch_layout = QHBoxLayout()
        self.theme_switch_layout.setContentsMargins(4, 0, 4, 0)
        self.theme_switch_layout.setSpacing(1)
        self.theme_container.setLayout(self.theme_switch_layout)

        self.theme_group = QButtonGroup(self)

        for theme in self.styles.keys():
            button = QPushButton(self.current_dict[f"theme_{theme}"])
            button.setFixedHeight(16)
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

        theme_login_layout.addWidget(
            self.theme_container, alignment=Qt.AlignmentFlag.AlignLeft
        )

        theme_login_layout.addStretch()

        # 'Already have an account?' label
        self.login_label = QLabel()
        self.login_label.setFixedHeight(24)

        theme_login_layout.addWidget(
            self.login_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Login button
        self.login_button = QPushButton()
        self.login_button.pressed.connect(self.open_login_window)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setFixedSize(80, 24)

        theme_login_layout.addWidget(
            self.login_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(theme_login_layout)

        self.layout.addSpacing(17)

        # Footer label
        self.footer_label = QLabel()
        self.layout.addWidget(
            self.footer_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addStretch()

        self.phone_input.textChanged.connect(self.check_sign_up_validity)
        self.email_input.textChanged.connect(self.check_sign_up_validity)
        self.role_combo.currentIndexChanged.connect(self.check_sign_up_validity)
        self.department_input.textChanged.connect(self.check_sign_up_validity)
        self.last_name_input.textChanged.connect(self.check_sign_up_validity)
        self.first_name_input.textChanged.connect(self.check_sign_up_validity)
        self.password_input.textChanged.connect(self.check_sign_up_validity)
        self.username_input.textChanged.connect(self.check_sign_up_validity)
        self.consent_checkbox.stateChanged.connect(self.check_sign_up_validity)

    def apply_style(self):
        style = self.styles[self.current_style]

        # Background image
        image_path = resource_path(style["background_image_path"])
        pixmap = QPixmap(image_path).scaled(
            500,
            620,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Logo
        logo_path = resource_path(style["logo_path"])
        pixmap = QPixmap(logo_path).scaled(
            161,
            121,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)

        # Gradient label
        gradient_style = style["gradient_label"]
        gradient_stylesheet = f"""
            QLabel {{
                min-height: {gradient_style["height"]};
                max-height: {gradient_style["height"]};
                font-family: {gradient_style["font-family"]};
                font-weight: {gradient_style["font-weight"]};
                font-size: {gradient_style["font-size"]};
                color: {gradient_style["color"]};
            }}
        """
        self.gradient_label.setStyleSheet(gradient_stylesheet)
        self.add_shadow(self.gradient_label, **gradient_style["shadow"])

        # Input fields
        input_style = style["input"]
        input_stylesheet = self.build_input_stylesheet("border-color", input_style)

        # Input icons
        icons = [
            (self.username_input, input_style["username-image"]),
            (self.password_input, input_style["password-image"]),
            (self.first_name_input, input_style["first-name-image"]),
            (self.last_name_input, input_style["last-name-image"]),
            (self.department_input, input_style["departament-image"]),
            (self.email_input, input_style["email-image"]),
            (self.phone_input, input_style["phone-image"]),
        ]
        for widget, icon_key in icons:
            icon_path = resource_path(icon_key)
            self.set_icon(
                widget,
                QLineEdit.ActionPosition.LeadingPosition,
                icon_path,
                main_icon=True,
            )

        input_widgets = [
            self.username_input,
            self.password_input,
            self.first_name_input,
            self.last_name_input,
            self.department_input,
            self.email_input,
            self.phone_input,
        ]
        for widget in input_widgets:
            widget.setStyleSheet(input_stylesheet)
            if input_style.get("shadow"):
                self.add_shadow(widget, **input_style["shadow"])
            else:
                widget.setGraphicsEffect(None)

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = QPalette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        for widget in input_widgets:
            widget.setPalette(placeholder_palette)

        for label in [
            self.username_error_label,
            self.password_error_label,
            self.firstname_error_label,
            self.lastname_error_label,
            self.department_error_label,
            self.email_error_label,
            self.phone_error_label,
        ]:
            label.setText("")

        # Role combo box
        role_combo_style = style["role_combo"]
        role_icon_path = resource_path(role_combo_style["role-image"])
        self.role_combo.setItemIcon(0, QIcon(role_icon_path))
        role_stylesheet = self.build_combo_stylesheet("border-color", role_combo_style)
        self.role_combo.setStyleSheet(role_stylesheet)
        if role_combo_style.get("shadow"):
            self.add_shadow(self.role_combo, **role_combo_style["shadow"])
        else:
            self.role_combo.setGraphicsEffect(None)
        self.role_error_label.setText("")

        # Optional information label
        optional_info_style = style["optional_info_label"]
        optional_info_stylesheet = f"""
            QLabel {{
                font-family: {optional_info_style["font-family"]};
                font-weight: {optional_info_style["font-weight"]};
                font-size: {optional_info_style["font-size"]};
                color: {optional_info_style["color"]};
            }}
        """
        self.optional_info_label.setStyleSheet(optional_info_stylesheet)
        self.add_shadow(self.optional_info_label, **optional_info_style["shadow"])

        # Consent checkbox
        consent_style = style["consent_checkbox"]
        consent_stylesheet = f"""
            QCheckBox {{
                padding-left: {consent_style["padding-left"]};
                font-family: {consent_style["font-family"]};
                font-weight: {consent_style["font-weight"]};
                font-size: {consent_style["font-size"]};
                color: {consent_style["color"]};
            }}
            QCheckBox::indicator {{
                border: {consent_style["indicator-border"]};
                border-radius: {consent_style["indicator-border-radius"]};
                background-color: {consent_style["indicator-background-color"]};
                width: {consent_style["indicator-width"]};
                height: {consent_style["indicator-height"]};
            }}
            QCheckBox::indicator:checked {{
                background-color: {consent_style["indicator-checked-background-color"]};
                image: url({resource_path(consent_style["checkmark-image"]).replace("\\", "/")});
            }}
        """
        self.consent_checkbox.setStyleSheet(consent_stylesheet)
        self.add_shadow(self.consent_checkbox, **consent_style["shadow"])

        # Privacy policy button
        privacy_style = style["privacy_policy_button"]
        privacy_stylesheet = f"""
            QPushButton {{
                border: {privacy_style["border"]};
                font-family: {privacy_style["font-family"]};
                font-weight: {privacy_style["font-weight"]};
                font-size: {privacy_style["font-size"]};
                color: {privacy_style["color"]};
                text-decoration: {privacy_style["text-decoration"]};
            }}
            QPushButton:hover {{
                color: {privacy_style["hover-color"]};
            }}
        """
        self.privacy_policy_button.setStyleSheet(privacy_stylesheet)
        self.add_shadow(self.privacy_policy_button, **privacy_style["shadow"])

        # Language selection combo box
        language_combo = style["language_combo"]
        language_icon_path = resource_path(language_combo["language-image"])
        self.language_combo.setItemIcon(0, QIcon(language_icon_path))
        language_stylesheet = self.build_combo_stylesheet(
            "border-color", language_combo
        )
        self.language_combo.setStyleSheet(language_stylesheet)
        if language_combo.get("shadow"):
            self.add_shadow(self.language_combo, **language_combo["shadow"])
        else:
            self.language_combo.setGraphicsEffect(None)

        # Sign up button
        self.check_sign_up_validity()

        # Theme switch
        theme_switch = style["theme_switch"]
        container_style = theme_switch["container"]
        button_style = theme_switch["button"]
        container_stylesheet = f"""
            QWidget {{
                border-width: {container_style["border-width"]};
                border-radius: {container_style["border-radius"]};
                border-style: {container_style["border-style"]};
                border-color: {container_style["border-color"]};
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

        # 'Already have an account?' label
        already_have_account_style = style["already_have_account"]
        already_have_account_stylesheet = f"""
            QLabel {{
                font-family: {already_have_account_style["font-family"]};
                font-weight: {already_have_account_style["font-weight"]};
                font-size: {already_have_account_style["font-size"]};
                color: {already_have_account_style["color"]};
            }}
        """
        self.login_label.setStyleSheet(already_have_account_stylesheet)
        self.add_shadow(self.login_label, **already_have_account_style["shadow"])

        # Login button
        login_button_style = style["login_button"]
        login_button_stylesheet = f"""
            QPushButton {{
                background-color: {login_button_style["background-color"]};
                border-width: {login_button_style["border-width"]};
                border-radius: {login_button_style["border-radius"]};
                color: {login_button_style["color"]};
                font-family: {login_button_style["font-family"]};
                font-weight: {login_button_style["font-weight"]};
                font-size: {login_button_style["font-size"]};
                border-style: {login_button_style["border-style"]};
                border-color: {login_button_style["border-color"]};
            }}
            QPushButton:hover {{
                background-color: {login_button_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {login_button_style["pressed-background-color"]};
            }}
        """
        self.login_button.setStyleSheet(login_button_stylesheet)
        self.add_shadow(self.login_button, **login_button_style["shadow"])

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

        # Department popup
        department_style = style["department_input"]
        department_stylesheet = f"""
            QListView {{
                background-color: {department_style["background-color"]};
                border-width: {department_style['border-width']};
                border-radius: {department_style['border-radius']};
                color: {department_style["color"]};
                font-family: {department_style["font-family"]};
                font-weight: {department_style["font-weight"]};
                font-size: {department_style["font-size"]};
                border-style: {department_style['border-style']};
                border-color: {department_style['border-color']};
            }}
            QListView::item {{
                padding-left: {department_style["padding-left"]};
                padding-top: {department_style["padding-top"]};
            }}
            QListView::item:hover {{
                background-color: {department_style.get("hover-background-color")};
            }}
        """
        self.department_input.completer().popup().setStyleSheet(department_stylesheet)

    def handle_sign_up(self):
        style = self.styles[self.current_style]
        error_label_style = style["error_label"]

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        department = self.department_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        input_style = self.styles[self.current_style]["input"]
        role_combo_style = self.styles[self.current_style]["role_combo"]

        not_correct_icon_path = resource_path(input_style["not-correct-image"])

        is_valid = True

        error_label_stylesheet = f"""
            QLabel {{
                color: {error_label_style["color"]};\
                font-family: {error_label_style["font-family"]};
                font-weight: {error_label_style["font-weight"]};
                font-size: {error_label_style["font-size"]};
            }}
        """

        # Login check
        if len(username) < 3:
            self.username_error_label.setText(self.current_dict["three_too_short"])
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.username_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
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
            self.set_icon(
                self.username_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        elif self.from_user_db(username, ["*"]):
            self.username_error_label.setText(self.current_dict["error_username_taken"])
            self.username_error_label.setStyleSheet(error_label_stylesheet)
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.username_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.username_error_label.setText("")
            self.username_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # Password check
        if len(password) < 8:
            self.password_error_label.setText(self.current_dict["eight_too_short"])
            self.password_error_label.setStyleSheet(error_label_stylesheet)
            self.password_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.password_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.password_error_label.setText("")
            self.password_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # First name
        if len(first_name) < 3:
            self.firstname_error_label.setText(self.current_dict["three_too_short"])
            self.firstname_error_label.setStyleSheet(error_label_stylesheet)
            self.first_name_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.first_name_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        elif not first_name.isalpha():
            self.firstname_error_label.setText(self.current_dict["error_only_letters"])
            self.firstname_error_label.setStyleSheet(error_label_stylesheet)
            self.first_name_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.first_name_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.firstname_error_label.setText("")
            self.first_name_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # Last name check
        if len(last_name) < 3:
            self.lastname_error_label.setText(self.current_dict["three_too_short"])
            self.lastname_error_label.setStyleSheet(error_label_stylesheet)
            self.last_name_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.last_name_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        elif not last_name.isalpha():
            self.lastname_error_label.setText(self.current_dict["error_only_letters"])
            self.lastname_error_label.setStyleSheet(error_label_stylesheet)
            self.last_name_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.last_name_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.lastname_error_label.setText("")
            self.last_name_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # Department check
        if len(department) < 3:
            self.department_error_label.setText(self.current_dict["three_too_short"])
            self.department_error_label.setStyleSheet(error_label_stylesheet)
            self.department_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.department_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.department_error_label.setText("")
            self.department_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # Role check
        if not self.role_combo.currentIndex() != 0:
            self.role_error_label.setText(self.current_dict["error_role"])
            self.role_error_label.setStyleSheet(error_label_stylesheet)
            self.role_combo.setStyleSheet(
                self.build_combo_stylesheet("error-border-color", role_combo_style)
            )
            is_valid = False
        else:
            self.role_error_label.setText("")
            self.role_combo.setStyleSheet(
                self.build_combo_stylesheet("border-color", role_combo_style)
            )

        # Email check
        if email != "" and not bool(
            re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email)
        ):
            self.email_error_label.setText(self.current_dict["error_email"])
            self.email_error_label.setStyleSheet(error_label_stylesheet)
            self.email_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.email_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.email_error_label.setText("")
            self.email_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # Phone check
        if phone != "" and not bool(re.fullmatch(r"[+()\d\s-]{10,}", phone)):
            self.phone_error_label.setText(self.current_dict["error_phone"])
            self.phone_error_label.setStyleSheet(error_label_stylesheet)
            self.phone_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            self.set_icon(
                self.phone_input,
                QLineEdit.ActionPosition.TrailingPosition,
                not_correct_icon_path,
            )
            is_valid = False
        else:
            self.phone_error_label.setText("")
            self.phone_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.username_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.username_input.setPalette(placeholder_palette)
        self.password_input.setPalette(placeholder_palette)
        self.first_name_input.setPalette(placeholder_palette)
        self.last_name_input.setPalette(placeholder_palette)
        self.department_input.setPalette(placeholder_palette)
        self.email_input.setPalette(placeholder_palette)
        self.phone_input.setPalette(placeholder_palette)

        if not is_valid:
            return

        # If all checks passed, proceed with registration
        recovery_phrase = mnemo.generate(strength=128)
        # TODO: delete this line after testing
        recovery_phrase = (
            "dog cat fish milk bread apple banana orange grape peach ball ball"
        )
        recovery_phrase_hash = bcrypt.hashpw(recovery_phrase.encode(), bcrypt.gensalt())
        recovery_phrase_hash_str = recovery_phrase_hash.decode()

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        password_hash_str = password_hash.decode()

        self.to_user_db(
            username=username,
            password=password_hash_str,
            fullname=f"{first_name} {last_name}",
            role=self.role_combo.currentText(),
            department=department,
            modules=["neuro_core"],
            account_state="active",
            access_level="base",
            recovery_code=recovery_phrase_hash_str,
            email=email if email else None,
            phone_number=phone if phone else None,
        )

        self.write_log(
            log_file=self.log_file_path,
            module_name=self.module_name,
            action="WELCOME_USER_REGISTERED",
            username=username,
            state="INFO",
            message="New person registered",
        )

        from neuro_core.ui.windows.sign_up_success_window import SignUpSuccessWindow

        self.sign_up_button.setEnabled(False)
        self.sign_up_window = SignUpSuccessWindow(
            self.current_lang, self.current_style, recovery_phrase.split()
        )
        self.sign_up_window.show()
        self.close()

    def check_sign_up_validity(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        department = self.department_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        sign_up_button_style = self.styles[self.current_style]["sign_up_button"]
        input_style = self.styles[self.current_style]["input"]

        is_username_valid = len(username) >= 3 and bool(
            re.fullmatch(r"[a-zA-Z0-9_.@-]+", username)
        )
        is_password_valid = len(password) >= 8
        is_first_name_valid = len(first_name) >= 3 and first_name.isalpha()
        is_last_name_valid = len(last_name) >= 3 and last_name.isalpha()
        is_department_valid = len(department) >= 3
        is_role_valid = self.role_combo.currentIndex() != 0
        is_email_valid = email == "" or bool(
            re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email)
        )
        is_phone_valid = phone == "" or bool(re.fullmatch(r"[+()\d\s-]{10,}", phone))

        correct_icon_path = resource_path(input_style["correct-image"])

        if is_username_valid:
            self.set_icon(
                self.username_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.username_input, QLineEdit.ActionPosition.TrailingPosition, None
            )
        if is_password_valid:
            self.set_icon(
                self.password_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.password_input, QLineEdit.ActionPosition.TrailingPosition, None
            )
        if is_first_name_valid:
            self.set_icon(
                self.first_name_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.first_name_input, QLineEdit.ActionPosition.TrailingPosition, None
            )
        if is_last_name_valid:
            self.set_icon(
                self.last_name_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.last_name_input, QLineEdit.ActionPosition.TrailingPosition, None
            )
        if is_department_valid:
            self.set_icon(
                self.department_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.department_input, QLineEdit.ActionPosition.TrailingPosition, None
            )
        if is_email_valid:
            self.set_icon(
                self.email_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.email_input, QLineEdit.ActionPosition.TrailingPosition, None
            )
        if is_phone_valid:
            self.set_icon(
                self.phone_input,
                QLineEdit.ActionPosition.TrailingPosition,
                correct_icon_path,
            )
        else:
            self.set_icon(
                self.phone_input, QLineEdit.ActionPosition.TrailingPosition, None
            )

        if not self.consent_checkbox.isChecked():
            self.sign_up_button.setEnabled(False)
        else:
            self.sign_up_button.setEnabled(True)

        sign_up_valid = (
            is_username_valid
            and is_password_valid
            and is_first_name_valid
            and is_last_name_valid
            and is_department_valid
            and is_email_valid
            and is_phone_valid
            and self.consent_checkbox.isChecked()
            and is_role_valid
        )

        if sign_up_valid:
            sign_up_stylesheet = f"""
                QPushButton {{
                    background-color: {sign_up_button_style['background-color']};
                    border-width: {sign_up_button_style['border-width']};
                    border-radius: {sign_up_button_style['border-radius']};
                    color: {sign_up_button_style['color']};
                    font-family: {sign_up_button_style['font-family']};
                    font-weight: {sign_up_button_style['font-weight']};
                    font-size: {sign_up_button_style['font-size']};
                    border-style: {sign_up_button_style['border-style']};
                    border-color: {sign_up_button_style['border-color']};
                }}
                QPushButton:hover {{
                    background-color: {sign_up_button_style['hover-background-color']};
                }} 
                QPushButton:pressed {{
                    background-color: {sign_up_button_style['pressed-background-color']};
                }}
            """
            shadow = sign_up_button_style["shadow"]
        else:
            sign_up_stylesheet = f"""
                QPushButton {{
                    background-color: {sign_up_button_style['disabled-background-color']};
                    border: {sign_up_button_style['disabled-border']};
                    border-radius: {sign_up_button_style['border-radius']};
                    color: {sign_up_button_style['disabled-color']};
                    font-family: {sign_up_button_style['font-family']};
                    font-weight: {sign_up_button_style['font-weight']};
                    font-size: {sign_up_button_style['font-size']};
                }}
                QPushButton:hover {{
                    background-color: {sign_up_button_style['disabled-hover-background-color']};
                }}
                QPushButton:pressed {{
                    background-color: {sign_up_button_style['disabled-pressed-background-color']};
                }}
            """
            shadow = sign_up_button_style["disabled-shadow"]

        self.sign_up_button.setStyleSheet(sign_up_stylesheet)
        self.add_shadow(self.sign_up_button, **shadow)

    def open_privacy_policy(self):
        from neuro_core.ui.windows.privacy_policy_window import PrivacyPolicyWindow

        self.privacy_policy_window = PrivacyPolicyWindow(
            self.current_lang, self.current_style
        )
        self.privacy_policy_window.exec()

    def eventFilter(self, source, event):
        if isinstance(source, (QLineEdit, QComboBox)):
            if isinstance(source, QLineEdit):
                style = self.styles[self.current_style]["input"]
            else:
                style = self.styles[self.current_style]["role_combo"]

            if event.type() in (event.Type.FocusIn, event.Type.Enter):
                if not style.get("hover-shadow"):
                    source.setGraphicsEffect(None)
                else:
                    self.add_shadow(source, **style["hover-shadow"])
            elif (
                event.type() in (event.Type.FocusOut, event.Type.Leave)
                and not source.hasFocus()
            ):
                if not style.get("shadow"):
                    source.setGraphicsEffect(None)
                else:
                    self.add_shadow(source, **style["shadow"])
        return super().eventFilter(source, event)

    @staticmethod
    def build_input_stylesheet(border_color_key, input_style):
        return f"""
                    QLineEdit {{
                        background-color: {input_style["background-color"]};
                        border-width: {input_style["border-width"]};
                        border-radius: {input_style["border-radius"]};
                        padding-left: {input_style["padding-left"]};
                        color: {input_style["color"]};
                        font-family: {input_style["font-family"]};
                        font-weight: {input_style["font-weight"]};
                        font-size: {input_style["font-size"]};
                        border-style: {input_style["border-style"]};
                        border-color: {input_style[border_color_key]};
                    }}
                    QLineEdit::hover {{
                        background-color: {input_style["hover-background-color"]};
                    }}
                """

    def open_login_window(self):
        self.login_button.setEnabled(False)
        self.login_window = LoginWindow(self.current_lang, self.current_style)
        self.login_window.show()
        self.close()

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])

        self.username_input.setPlaceholderText(self.current_dict["username"])
        self.password_input.setPlaceholderText(self.current_dict["password"])
        self.first_name_input.setPlaceholderText(self.current_dict["first_name"])
        self.last_name_input.setPlaceholderText(self.current_dict["last_name"])
        self.department_input.setPlaceholderText(self.current_dict["department"])
        model = QStringListModel(
            self.professions_by_language.get(self.current_lang, [])
        )
        self.completer.setModel(model)
        self.email_input.setPlaceholderText(self.current_dict["email"])
        self.phone_input.setPlaceholderText(self.current_dict["phone"])
        self.role_combo.setItemText(0, self.current_dict["role"])
        for i in range(1, self.role_combo.count()):
            self.role_combo.setItemText(i, self.current_dict["roles"][i - 1])

        input_style = self.styles[self.current_style]["input"]
        input_stylesheet = self.build_input_stylesheet("border-color", input_style)
        self.username_input.setStyleSheet(input_stylesheet)
        self.password_input.setStyleSheet(input_stylesheet)
        self.first_name_input.setStyleSheet(input_stylesheet)
        self.last_name_input.setStyleSheet(input_stylesheet)
        self.department_input.setStyleSheet(input_stylesheet)
        self.email_input.setStyleSheet(input_stylesheet)
        self.phone_input.setStyleSheet(input_stylesheet)
        role_combo_style = self.styles[self.current_style]["role_combo"]
        role_stylesheet = self.build_combo_stylesheet("border-color", role_combo_style)
        self.role_combo.setStyleSheet(role_stylesheet)

        self.username_error_label.setText("")
        self.password_error_label.setText("")
        self.firstname_error_label.setText("")
        self.lastname_error_label.setText("")
        self.department_error_label.setText("")
        self.email_error_label.setText("")
        self.phone_error_label.setText("")
        self.role_error_label.setText("")

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.username_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.username_input.setPalette(placeholder_palette)
        self.password_input.setPalette(placeholder_palette)
        self.first_name_input.setPalette(placeholder_palette)
        self.last_name_input.setPalette(placeholder_palette)
        self.department_input.setPalette(placeholder_palette)
        self.email_input.setPalette(placeholder_palette)
        self.phone_input.setPalette(placeholder_palette)

        self.optional_info_label.setText(self.current_dict["optional_info"])
        self.consent_checkbox.setText(self.current_dict["agree"])
        self.privacy_policy_button.setText(self.current_dict["privacy_policy"])
        self.language_combo.setItemText(0, self.current_dict["language"])
        self.sign_up_button.setText(self.current_dict["sign_up"])
        self.check_sign_up_validity()
        for theme, button in zip(self.styles, self.theme_group.buttons()):
            button.setText(self.current_dict[f"theme_{theme}"])
        self.login_label.setText(self.current_dict["already_have_account"])
        self.login_button.setText(self.current_dict["login"])
        self.footer_label.setText(self.current_dict["footer"])
