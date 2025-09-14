from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.sign_up_window import SignUpWindow


class PrivacyPolicyWindow(QDialog):

    def __init__(self, current_lang: str, current_style: str):
        QDialog.__init__(self)

        self.languages = SignUpWindow.load_languages("privacy_policy_window")
        self.styles = SignUpWindow.load_styles("privacy_policy_window")

        self.current_lang = current_lang
        self.current_style = current_style
        self.current_dict = self.languages[self.current_lang]

        icon_path = resource_path("neuro_core/config/icons/main.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(450, 600)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10, 15, 10, 10)

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
        self.layout.addSpacing(20)

        # === Додаємо багаторядковий текст для політики ===
        self.privacy_policy_text = QTextEdit()
        self.privacy_policy_text.setReadOnly(True)
        self.layout.addWidget(self.privacy_policy_text)

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
            160,
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
        SignUpWindow.add_shadow(self.gradient_label, **gradient_style["shadow"])

        # Стиль тексту політики
        privacy_policy_style = style["privacy_policy_text"]
        privacy_policy_stylesheet = f"""
            QTextEdit {{
                font-family: {privacy_policy_style["font-family"]};
                font-weight: {privacy_policy_style["font-weight"]};
                color: {privacy_policy_style["color"]};
                font-size: {privacy_policy_style["font-size"]};
                background-color: {privacy_policy_style["background-color"]};
                padding: {privacy_policy_style["padding"]};
                border: {privacy_policy_style["border"]};
                border-radius: {privacy_policy_style["border-radius"]};
            }}
        """
        self.privacy_policy_text.setStyleSheet(privacy_policy_stylesheet)

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.privacy_policy_text.setText(self.current_dict["privacy_policy"])
