from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.forgot_password_window import ForgotPasswordWindow
from neuro_core.ui.windows.login_window import LoginWindow


class ForgotPasswordSuccessWindow(ForgotPasswordWindow, QMainWindow):
    def __init__(
        self,
        current_lang: str,
        current_style: str,
    ):
        QMainWindow.__init__(self)

        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"

        self.languages = self.load_languages("forgot_password_success_window")
        self.styles = self.load_styles("forgot_password_success_window")

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
        # Logo
        self.logo_label = QLabel()
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addSpacing(10)

        # Gradient label
        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(10)

        # Instruction label
        self.instruction_label = QLabel()
        self.instruction_label.setFixedSize(250, 50)
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(
            self.instruction_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(10)

        # Success icon
        self.success_icon = QSvgWidget()
        self.success_icon.setFixedSize(45, 45)
        self.layout.addWidget(
            self.success_icon, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(5)

        # Success label
        self.success_label = QLabel()
        self.success_label.setFixedHeight(35)
        self.layout.addWidget(
            self.success_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Message label
        self.message_label = QLabel()
        self.message_label.setFixedHeight(15)
        self.layout.addWidget(
            self.message_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(108)

        # Back button
        self.login_button = QPushButton()
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setFixedSize(320, 48)
        self.login_button.clicked.connect(self.open_login_window)
        self.layout.addWidget(
            self.login_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(10)

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

        # Success icon
        success_icon_path = resource_path(style["success_icon_path"])
        self.success_icon.load(success_icon_path)

        # Success label
        success_style = style["success_label"]
        success_stylesheet = f"""
                    QLabel {{
                        font-family: {success_style["font-family"]};
                        font-weight: {success_style["font-weight"]};
                        color: {success_style["color"]};
                        font-size: {success_style["font-size"]};
                    }}
                """
        self.success_label.setStyleSheet(success_stylesheet)
        self.add_shadow(self.success_label, **success_style["shadow"])

        # Message label
        message_label_style = style["message_label"]
        message_stylesheet = f"""
                    QLabel {{
                        font-family: {message_label_style["font-family"]};
                        font-weight: {message_label_style["font-weight"]};
                        color: {message_label_style["color"]};
                        font-size: {message_label_style["font-size"]};
                    }}
                """
        self.message_label.setStyleSheet(message_stylesheet)
        self.add_shadow(self.message_label, **message_label_style["shadow"])

        # Login button
        login_button_style = style["login_button"]
        login_button_stylesheet = f"""
            QPushButton {{
                background-color: {login_button_style["background-color"]};
                border-width: {login_button_style["border-width"]};
                border-color: {login_button_style["border-color"]};
                border-style: {login_button_style["border-style"]};
                border-radius: {login_button_style["border-radius"]};
                font-family: {login_button_style["font-family"]};
                font-size: {login_button_style["font-size"]};
                font-weight: {login_button_style["font-weight"]};
                color: {login_button_style["color"]};
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

    def open_login_window(self):
        self.login_button.setEnabled(False)
        self.login_window = LoginWindow(self.current_lang, self.current_style)
        self.login_window.show()
        self.close()

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.success_label.setText(self.current_dict["success"])
        self.message_label.setText(self.current_dict["message"])
        self.login_button.setText(self.current_dict["login"])
        self.footer_label.setText(self.current_dict["footer"])
