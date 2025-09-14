from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.sign_up_recovery_code_window import SignUpRecoveryCodeWindow
from neuro_core.ui.windows.sign_up_window import SignUpWindow


class SignUpSuccessWindow(SignUpWindow, QMainWindow):
    def __init__(
        self, current_lang: str, current_style: str, recovery_phrase: list[str]
    ):
        QMainWindow.__init__(self)

        self.languages = self.load_languages("sign_up_success_window")
        self.styles = self.load_styles("sign_up_success_window")

        self.current_lang = current_lang
        self.current_style = current_style
        self.recovery_phrase = recovery_phrase
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
        # Логотип
        self.logo_label = QLabel()
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addSpacing(7)

        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(80)

        # іконка успіху
        self.success_icon = QSvgWidget()
        self.success_icon.setFixedSize(45, 45)
        self.layout.addWidget(
            self.success_icon, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(5)

        # Заголовок успіху
        self.success_label = QLabel()
        self.success_label.setFixedHeight(35)
        self.layout.addWidget(
            self.success_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Текст успіху
        self.success_text_label = QLabel()
        self.success_text_label.setFixedHeight(15)
        self.layout.addWidget(
            self.success_text_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(150)

        # Кнопка продовжити

        self.continue_button = QPushButton()
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.clicked.connect(self.open_sign_up_recovery_code_window)
        self.continue_button.setFixedSize(220, 40)
        self.layout.addWidget(
            self.continue_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(32)

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
            161,
            121,
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

        # Стиль іконки успіху
        success_icon_path = resource_path(style["success_icon_path"])
        self.success_icon.load(success_icon_path)

        # Стиль заголовку успіху
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

        # Стиль тексту успіху
        success_text_style = style["success_text_label"]
        success_text_stylesheet = f"""
            QLabel {{
                font-family: {success_text_style["font-family"]};
                font-weight: {success_text_style["font-weight"]};
                color: {success_text_style["color"]};
                font-size: {success_text_style["font-size"]};
            }}
        """
        self.success_text_label.setStyleSheet(success_text_stylesheet)
        self.add_shadow(self.success_text_label, **success_text_style["shadow"])

        # Стиль кнопки продовжити
        continue_style = style["continue_button"]
        continue_stylesheet = f"""
            QPushButton {{
                background-color: {continue_style["background-color"]};
                border-radius: {continue_style["border-radius"]};
                font-family: {continue_style["font-family"]};
                font-weight: {continue_style["font-weight"]};
                color: {continue_style["color"]};
                font-size: {continue_style["font-size"]};
                border-width: {continue_style["border-width"]};
                border-style: {continue_style["border-style"]};
                border-color: {continue_style["border-color"]};
            }}
            QPushButton:hover {{
                background-color: {continue_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {continue_style["pressed-background-color"]};
            }}
        """
        self.continue_button.setStyleSheet(continue_stylesheet)
        self.add_shadow(self.continue_button, **continue_style["shadow"])

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

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.success_label.setText(self.current_dict["success_title"])
        self.success_text_label.setText(self.current_dict["success_message"])
        self.continue_button.setText(self.current_dict["continue"])
        self.footer_label.setText(self.current_dict["footer"])

    def open_sign_up_recovery_code_window(self):
        self.continue_button.setEnabled(False)
        self.sign_up_recovery_code_window = SignUpRecoveryCodeWindow(
            self.current_lang, self.current_style, self.recovery_phrase
        )
        self.sign_up_recovery_code_window.show()
        self.close()
