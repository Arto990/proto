from PyQt6.QtCore import Qt, QTimer
import bcrypt
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.forgot_password_qr_window import ForgotPasswordQRWindow
from neuro_core.ui.windows.forgot_password_window import ForgotPasswordWindow
from neuro_core.ui.windows.password_recovery_window import PasswordRecoveryWindow


class ForgotPasswordQRLoadingWindow(ForgotPasswordWindow, QMainWindow):
    def __init__(
        self, current_lang: str, current_style: str, username: str, recovery_code: str
    ):
        QMainWindow.__init__(self)

        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"
        self.username = username
        self.recovery_code = recovery_code

        self.languages = self.load_languages("forgot_password_qr_loading_window")
        self.styles = self.load_styles("forgot_password_qr_loading_window")

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

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.check_recovery_code)
        self.timer.start(5300)

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

        # QR icon
        self.qr_icon = QWebEngineView()
        self.qr_icon.setFixedSize(200, 200)
        self.layout.addWidget(self.qr_icon, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.layout.addSpacing(10)

        # Message label
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setFixedSize(320, 35)
        self.layout.addWidget(
            self.message_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(35)

        # Back button
        self.back_button = QPushButton()
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setFixedSize(320, 48)
        self.back_button.clicked.connect(self.open_forgot_password_qr_window)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.layout.addSpacing(10)

        # Footer label
        self.footer_label = QLabel()
        self.layout.addWidget(
            self.footer_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addStretch()

    def apply_style(self):
        style = self.styles[self.current_style]

        # Background
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

        # Lоgo
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

        # QR icon
        qr_icon_path = resource_path(style["qr_path"])
        with open(qr_icon_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        html = f"""
            <html>
            <head>
            <style>
                svg {{
                    width: 100%;
                    height: 100%;
                }}
            </style>
            </head>
            <body>
            {svg_content}
            </body>
            </html>
            """
        self.qr_icon.setHtml(html)
        self.qr_icon.page().setBackgroundColor(Qt.GlobalColor.transparent)

        # Message label
        message_style = style["message_label"]
        message_stylesheet = f"""
                    QLabel {{
                        font-family: {message_style["font-family"]};
                        font-weight: {message_style["font-weight"]};
                        color: {message_style["color"]};
                        font-size: {message_style["font-size"]};
                    }}
                """
        self.message_label.setStyleSheet(message_stylesheet)
        self.add_shadow(self.message_label, **message_style["shadow"])

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

    def open_forgot_password_qr_window(self, error: bool = False):
        self.back_button.setEnabled(False)

        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        self.forgot_password_qr_window = ForgotPasswordQRWindow(
            self.current_lang,
            self.current_style,
            self.username,
            error_text=self.current_dict["error"] if error else "",
        )
        self.forgot_password_qr_window.show()
        self.close()

    def check_recovery_code(self):
        user_recovery_code = self.from_user_db(self.username, ["recovery_code"])[0]
        if not user_recovery_code or not bcrypt.checkpw(
            self.recovery_code.encode(), user_recovery_code.encode()
        ):
            self.open_forgot_password_qr_window(error=True)
        else:
            self.open_password_recovery_window()

    def open_password_recovery_window(self):
        self.back_button.setEnabled(False)

        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        self.password_recovery_window = PasswordRecoveryWindow(
            self.current_lang, self.current_style, self.username
        )
        self.password_recovery_window.show()
        self.close()

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.message_label.setText(self.current_dict["message"])
        self.back_button.setText(self.current_dict["back"])
        self.footer_label.setText(self.current_dict["footer"])
