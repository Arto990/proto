from io import BytesIO

import qrcode
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QBrush, QImage
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
)

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.sign_up_window import SignUpWindow


class SignUpRecoveryQRWindow(SignUpWindow, QMainWindow):
    def __init__(
        self, current_lang: str, current_style: str, recovery_phrase: list[str]
    ):
        QMainWindow.__init__(self)
        self.languages = self.load_languages("sign_up_recovery_qr_window")
        self.styles = self.load_styles("sign_up_recovery_qr_window")
        self.current_lang = current_lang
        self.current_style = current_style
        self.recovery_phrase = recovery_phrase
        self.current_dict = self.languages[self.current_lang]

        icon_path = resource_path("neuro_core/config/icons/main.png")
        self.setWindowIcon(QIcon(icon_path))
        self.window_w = 500
        self.window_h = 620
        self.setFixedSize(self.window_w, self.window_h)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 15, 0, 0)

        self.setup_ui()
        self.apply_style()
        self.update_texts()

    def setup_ui(self):
        self.logo_label = QLabel()
        self.layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addSpacing(7)

        self.gradient_label = QLabel()
        self.layout.addWidget(
            self.gradient_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addSpacing(10)

        self.instruction_label = QLabel()
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(
            self.instruction_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(10)

        # --- Додаємо QR-код ---
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(210, 210)
        self.layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.show_qr_code()  # Додаємо відразу після створення qr_label

        self.layout.addSpacing(10)

        # кнопка завантаження qr коду
        self.download_png_button = QPushButton()
        self.download_png_button.clicked.connect(self.save_qr_to_png)
        self.download_png_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_png_button.setFixedHeight(24)
        self.layout.addWidget(
            self.download_png_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(30)

        # кнопка продовжити
        self.continue_button = QPushButton()
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.setFixedSize(220, 40)
        self.layout.addWidget(
            self.continue_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(17)

        # Напис унікальності дизайну
        self.footer_label = QLabel()
        self.layout.addWidget(
            self.footer_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addStretch()

    def apply_style(self):
        style = self.styles[self.current_style]
        # Фон
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
        # Логотип
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
        # Градієнтний текст
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
        # Кнопка завантаження текстового файлу
        download_png_style = style["download_png_button"]
        download_png_icon_path = resource_path(download_png_style["icon_path"])
        self.download_png_button.setIcon(QIcon(download_png_icon_path))
        download_png_stylesheet = f"""
            QPushButton {{
                padding-left: {download_png_style["padding-left"]};
                padding-right: {download_png_style["padding-right"]};
                text-align: {download_png_style["text-align"]};
                background-color: {download_png_style["background-color"]};
                border-radius: {download_png_style["border-radius"]};
                color: {download_png_style["color"]};
                font-size: {download_png_style["font-size"]};
                font-family: {download_png_style["font-family"]};
                font-weight: {download_png_style["font-weight"]};
                border-width: {download_png_style["border-width"]};
                border-style: {download_png_style["border-style"]};
                border-color: {download_png_style["border-color"]};
            }}
            QPushButton:hover {{
                background-color: {download_png_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {download_png_style["pressed-background-color"]};
            }}
        """
        self.download_png_button.setStyleSheet(download_png_stylesheet)
        self.add_shadow(self.download_png_button, **download_png_style["shadow"])
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
        self.instruction_label.setText(self.current_dict["recovery_qr_instruction"])
        self.download_png_button.setText(self.current_dict["download_qr"])
        self.continue_button.setText(self.current_dict["continue"])
        self.footer_label.setText(self.current_dict["footer"])

    def show_qr_code(self):
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr_data = " ".join(self.recovery_phrase)
        self.qr.add_data(qr_data)
        self.qr.make(fit=True)

        qr_style = self.styles[self.current_style]["qr_code_label"]
        qr_img = self.qr.make_image(
            fill_color=qr_style["color"], back_color=qr_style["background-color"]
        )
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        qt_img = QImage.fromData(buf.getvalue())
        # Масштабуємо з невеликим запасом для padding
        pixmap = QPixmap.fromImage(qt_img).scaled(
            200,
            200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.qr_label.setPixmap(pixmap)
        self.qr_label.setScaledContents(True)

        qr_stylesheet = f"""
            QLabel {{
                border-radius: 10px; 
                background-color: {qr_style["background-color"]};  
                padding: 5px; 
            }}
        """
        self.qr_label.setStyleSheet(qr_stylesheet)

    def save_qr_to_png(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, None, "neuro_recovery_qr.png", "PNG Files (*.png)"
        )
        if file_path:
            qr_img = self.qr.make_image()
            qr_img.save(file_path)
