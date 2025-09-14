from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPalette, QPixmap, QBrush, QImage
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QDialog
import cv2

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.forgot_password_qr_window import ForgotPasswordQRWindow


class ForgotPasswordQRScanWindow(QDialog):
    def __init__(self, current_lang: str, current_style: str):
        super().__init__()

        self.user_db_path = resource_path("neuro_core/data/user_database.db")
        self.log_file_path = resource_path(
            "neuro_core/logs/reception/entry_log_<date>.log"
        )
        self.module_name = "Welcome"

        self.languages = ForgotPasswordQRWindow.load_languages(
            "forgot_password_qr_scan_window"
        )
        self.styles = ForgotPasswordQRWindow.load_styles(
            "forgot_password_qr_scan_window"
        )

        self.current_lang = current_lang
        self.current_style = current_style
        self.current_dict = self.languages[self.current_lang]

        icon_path = resource_path("neuro_core/config/icons/main.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(400, 600)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 21, 0, 0)

        self.camera = None
        self.timer = None
        self.error_text = ""
        self.qr_content = ""

        self.setup_ui()
        self.apply_style()
        self.update_texts()
        self.scan_qr_method()

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

        self.layout.addSpacing(6)

        # Image label for camera feed
        self.image_label = QLabel()
        self.image_label.setFixedSize(280, 280)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter)

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
        ForgotPasswordQRWindow.add_shadow(
            self.gradient_label, **gradient_style["shadow"]
        )

        # Instruction label
        instruction_style = self.styles[self.current_style]["instruction_label"]
        instruction_stylesheet = f"""
            QLabel {{
                font-family: {instruction_style["font-family"]};
                font-weight: {instruction_style["font-weight"]};
                font-size: {instruction_style["font-size"]};
                color: {instruction_style["color"]};
            }}
        """
        self.instruction_label.setStyleSheet(instruction_stylesheet)
        ForgotPasswordQRWindow.add_shadow(
            self.instruction_label, **instruction_style["shadow"]
        )

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

    def scan_qr_method(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.error_text = self.current_dict["error"]
            self.back_to_qr_window()
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            height, width, _ = frame.shape
            min_dim = min(width, height)
            x_offset = (width - min_dim) // 2
            y_offset = (height - min_dim) // 2
            cropped_frame = frame[
                y_offset : y_offset + min_dim, x_offset : x_offset + min_dim
            ]

            frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(
                frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_image).scaled(
                280,
                280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(pixmap)

            self.qr_content = ForgotPasswordQRWindow.decode_qr_code(frame)
            if self.qr_content:
                self.back_to_qr_window()

    def stop_camera(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.camera:
            self.camera.release()
            self.camera = None

    def back_to_qr_window(self):
        self.stop_camera()
        self.reject()

    def update_texts(self):
        self.setWindowTitle(self.current_dict["title"])
        self.gradient_label.setText(self.current_dict["slogan"])
        self.instruction_label.setText(self.current_dict["instruction"])
        self.footer_label.setText(self.current_dict["footer"])
