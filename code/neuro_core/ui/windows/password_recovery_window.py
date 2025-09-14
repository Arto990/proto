import logging
import sqlite3

import bcrypt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QIcon,
    QPalette,
    QPixmap,
    QBrush,
    QColor,
)
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QButtonGroup,
)
from neuro_core.ui.windows.forgot_password_window import ForgotPasswordWindow
from neuro_core.ui.windows.login_window import LoginWindow

from neuro_core.tools.utils import resource_path


class PasswordRecoveryWindow(ForgotPasswordWindow, QMainWindow):
    def __init__(self, current_lang: str, current_style: str, username: str):
        QMainWindow.__init__(self)
        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"
        self.username = username
        self.write_log(
            self.log_file_path,
            self.module_name,
            "WELCOME_MODULE_LAUNCHED",
            self.username,
            "INFO",
            "Interface launched",
        )

        self.load_fonts()
        self.languages = self.load_languages("password_recovery_window")
        self.styles = self.load_styles("password_recovery_window")

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
        # Logo
        self.logo_label = QLabel()
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addSpacing(10)

        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(10)

        # Password Label
        self.password_label = QLabel()
        self.layout.addWidget(
            self.password_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(10)

        # New password field
        self.new_password_input = QLineEdit()
        self.new_password_input.setFixedSize(320, 40)
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.textChanged.connect(self.check_new_password_validity)
        self.layout.addWidget(
            self.new_password_input, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(2)

        # New password error
        self.new_password_error_label = QLabel()
        self.new_password_error_label.setFixedHeight(10)
        self.new_password_error_label.setContentsMargins(40, 0, 0, 0)
        self.layout.addWidget(
            self.new_password_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Confirm new password field
        self.confirm_new_password_input = QLineEdit()
        self.confirm_new_password_input.setFixedSize(320, 40)
        self.confirm_new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_new_password_input.textChanged.connect(
            self.check_new_password_validity
        )
        self.layout.addWidget(
            self.confirm_new_password_input, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(2)

        # Confirm new password error
        self.confirm_new_password_error_label = QLabel()
        self.confirm_new_password_error_label.setFixedHeight(10)
        self.confirm_new_password_error_label.setContentsMargins(40, 0, 0, 0)
        self.layout.addWidget(
            self.confirm_new_password_error_label, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.layout.addSpacing(88)

        # Theme selection button
        self.theme_layout = QHBoxLayout()
        self.theme_layout.setContentsMargins(50, 0, 50, 0)

        # Creating a container for the theme switcher
        self.theme_container = QWidget()  # New widget container
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
            self.theme_switch_layout.addWidget(button)  # Adding a button to the layout

        # Add a container with theme buttons to the main layout
        self.theme_layout.addWidget(
            self.theme_container, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addLayout(self.theme_layout)
        self.layout.addSpacing(10)

        # Create a horizontal layout for Register and Login buttons
        self.reg_login_layout = QHBoxLayout()
        self.reg_login_layout.setContentsMargins(40, 0, 40, 0)

        # Back button
        self.back_button = QPushButton()
        self.back_button.setFixedSize(160, 48)
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self.open_forgot_password_window)
        self.reg_login_layout.addWidget(
            self.back_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Reset Password button
        self.reset_password_button = QPushButton()
        self.reset_password_button.setFixedSize(160, 48)
        self.reset_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_password_button.clicked.connect(self.handle_reset_password)
        self.reg_login_layout.addWidget(
            self.reset_password_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Add the horizontal button layout to the main vertical layout
        self.layout.addLayout(self.reg_login_layout)
        self.layout.addSpacing(8)

        # Design uniqueness inscription
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

        # Logo style
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

        # Gradient text style
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

        # Styles of password label
        password_label_style = style["password_label"]
        password_label_stylesheet = f"""
            QLabel {{
                color: {password_label_style["color"]};
                font-family: {password_label_style["font-family"]};
                font-size: {password_label_style["font-size"]};
            }}
        """
        self.password_label.setStyleSheet(password_label_stylesheet)

        # Styles for input fields
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
        self.new_password_input.setStyleSheet(input_stylesheet)
        self.confirm_new_password_input.setStyleSheet(input_stylesheet)

        if input_style.get("shadow"):
            self.add_shadow(self.new_password_input, **input_style["shadow"])
            self.add_shadow(self.confirm_new_password_input, **input_style["shadow"])
        else:
            self.new_password_input.setGraphicsEffect(None)
            self.confirm_new_password_input.setGraphicsEffect(None)

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.new_password_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.new_password_input.setPalette(placeholder_palette)
        self.confirm_new_password_input.setPalette(placeholder_palette)

        # Input icons
        icons = [
            (self.new_password_input, input_style["password-image"]),
            (self.confirm_new_password_input, input_style["password-image"]),
        ]
        for widget, icon_key in icons:
            icon_path = resource_path(icon_key)
            self.set_icon(
                widget,
                QLineEdit.ActionPosition.LeadingPosition,
                icon_path,
                main_icon=True,
            )

        # Style for the back button
        back_button_style = style["back_button"]
        back_button_stylesheet = f"""
            QPushButton {{
                background-color: {back_button_style["background-color"]};
                border-width: {back_button_style["border-width"]};
                border-radius: {back_button_style["border-radius"]};
                height: {back_button_style["height"]};
                min-width: {back_button_style["min-width"]};
                color: {back_button_style["color"]};
                font-family: {back_button_style["font-family"]};
                font-weight: {back_button_style["font-weight"]};
                font-size: {back_button_style["font-size"]};
                border-style: {back_button_style["border-style"]};
                border-color: {back_button_style["border-color"]};
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

        # Theme switcher style
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

        # Style for the login button
        self.check_new_password_validity()

        # Signature style
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

        # Removing error messages
        self.new_password_error_label.setText("")
        self.confirm_new_password_error_label.setText("")

    def open_forgot_password_window(self):
        self.back_button.setEnabled(False)

        self.forgot_password_window = ForgotPasswordWindow(
            self.current_lang, self.current_style, self.username
        )
        self.forgot_password_window.show()
        self.close()

    def open_login_window(self):
        self.reset_password_button.setEnabled(False)

        self.login_window = LoginWindow(self.current_lang, self.current_style)
        self.login_window.show()
        self.close()

    def handle_reset_password(self):
        style = self.styles[self.current_style]
        input_style = style["input"]
        error_label_style = style["error_label"]

        new_password = self.new_password_input.text().strip()
        confirm_new_password = self.confirm_new_password_input.text().strip()

        is_valid = True

        error_label_stylesheet = f"""
            QLabel {{
                color: {error_label_style["color"]};\
                font-family: {error_label_style["font-family"]};
                font-weight: {error_label_style["font-weight"]};
                font-size: {error_label_style["font-size"]};
            }}
        """

        # Validate new password length
        if len(new_password) < 8:
            self.new_password_error_label.setText(
                self.current_dict["password_too_short"]
            )
            self.new_password_error_label.setStyleSheet(error_label_stylesheet)
            self.new_password_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        else:
            self.new_password_error_label.setText("")
            self.new_password_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        # Validate password match
        if new_password != confirm_new_password:
            self.confirm_new_password_error_label.setText(
                self.current_dict["passwords_do_not_match"]
            )
            self.confirm_new_password_error_label.setStyleSheet(error_label_stylesheet)
            self.confirm_new_password_input.setStyleSheet(
                self.build_input_stylesheet("error-border-color", input_style)
            )
            is_valid = False
        else:
            self.confirm_new_password_error_label.setText("")
            self.confirm_new_password_input.setStyleSheet(
                self.build_input_stylesheet("border-color", input_style)
            )

        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.new_password_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.new_password_input.setPalette(placeholder_palette)
        self.confirm_new_password_input.setPalette(placeholder_palette)

        self.new_password_error_label.setContentsMargins(40, 0, 0, 0)
        self.confirm_new_password_error_label.setContentsMargins(40, 0, 0, 0)

        if not is_valid:
            return

        # Hash the password
        new_password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        new_password_hash_str = new_password_hash.decode()

        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_password_hash_str, self.username),
            )
            conn.commit()
            conn.close()

            # Log the password reset
            self.write_log(
                log_file=self.log_file_path,
                module_name=self.module_name,
                action="RESET_PASSWORD",
                username=self.username,
                state="INFO",
                message="Password was reset successfully.",
            )

        except Exception as e:
            logging.error(f"Error occurred while resetting password: {e}")
            self.password_error_label.setText("Something went wrong. Please try again.")

        # ===== Success =====
        self.open_login_window()

    def check_new_password_validity(self):
        password = self.new_password_input.text().strip()
        confirm_new_password = self.confirm_new_password_input.text().strip()

        reset_password_button_style = self.styles[self.current_style][
            "reset_password_button"
        ]

        # Check if both passwords are valid and match
        is_valid_length = len(password) >= 8 and len(confirm_new_password) >= 8
        passwords_match = password == confirm_new_password

        valid = is_valid_length and passwords_match

        if valid:
            login_stylesheet = f"""
                QPushButton {{
                    background-color: {reset_password_button_style['background-color']};
                    border-width: {reset_password_button_style['border-width']};
                    border-radius: {reset_password_button_style['border-radius']};
                    color: {reset_password_button_style['color']};
                    font-family: {reset_password_button_style['font-family']};
                    font-weight: {reset_password_button_style['font-weight']};
                    font-size: {reset_password_button_style['font-size']};
                    border-style: {reset_password_button_style['border-style']};
                    border-color: {reset_password_button_style['border-color']};
                }}
                QPushButton:hover {{
                    background-color: {reset_password_button_style['hover-background-color']};
                }} 
                QPushButton:pressed {{
                    background-color: {reset_password_button_style['pressed-background-color']};
                }}
            """
            shadow = reset_password_button_style["shadow"]
        else:
            login_stylesheet = f"""
                QPushButton {{
                    background-color: {reset_password_button_style['disabled-background-color']};
                    border-width: {reset_password_button_style['border-width']};
                    border-radius: {reset_password_button_style['border-radius']};
                    color: {reset_password_button_style['disabled-color']};
                    font-family: {reset_password_button_style['font-family']};
                    font-weight: {reset_password_button_style['font-weight']};
                    font-size: {reset_password_button_style['font-size']};
                }}
                QPushButton:hover {{
                    background-color: {reset_password_button_style['disabled-hover-background-color']};
                }}
                QPushButton:pressed {{
                    background-color: {reset_password_button_style['disabled-pressed-background-color']};
                }}
            """
            shadow = reset_password_button_style["disabled-shadow"]

        self.reset_password_button.setStyleSheet(login_stylesheet)
        self.add_shadow(self.reset_password_button, **shadow)

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.password_label.setText(self.current_dict["create_new_password"])
        self.new_password_input.setPlaceholderText(self.current_dict["new_password"])
        self.confirm_new_password_input.setPlaceholderText(
            self.current_dict["confirm_new_password"]
        )
        self.back_button.setText(self.current_dict["back"])
        for theme, button in zip(self.styles, self.theme_group.buttons()):
            button.setText(self.current_dict[f"theme_{theme}"])
        self.reset_password_button.setText(self.current_dict["reset_password"])
        self.footer_label.setText(self.current_dict["footer"])
        self.new_password_error_label.setText("")
        self.confirm_new_password_error_label.setText("")
        style = self.styles[self.current_style]
        input_style = style["input"]
        input_stylesheet = self.build_input_stylesheet("border-color", input_style)
        self.new_password_input.setStyleSheet(input_stylesheet)
        self.confirm_new_password_input.setStyleSheet(input_stylesheet)
        placeholder_color = QColor(input_style["color"])
        placeholder_palette = self.new_password_input.palette()
        placeholder_palette.setColor(
            QPalette.ColorRole.PlaceholderText, placeholder_color
        )
        self.new_password_input.setPalette(placeholder_palette)
        self.confirm_new_password_input.setPalette(placeholder_palette)
