import random

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QBrush
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGraphicsOpacityEffect,
    QPushButton,
    QHBoxLayout,
    QApplication,
    QFileDialog,
)

from neuro_core.tools.utils import resource_path
from neuro_core.ui.windows.sign_up_recovery_qr_window import SignUpRecoveryQRWindow
from neuro_core.ui.windows.sign_up_window import SignUpWindow


class SignUpRecoveryCodeWindow(SignUpWindow, QMainWindow):
    def __init__(
        self, current_lang: str, current_style: str, recovery_phrase: list[str]
    ):
        QMainWindow.__init__(self)
        self.languages = self.load_languages("sign_up_recovery_code_window")
        self.styles = self.load_styles("sign_up_recovery_code_window")
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

        # --- Фіксована ручна сітка для recovery phrase ---

        self.grid_top = 260
        self.button_width = 85
        self.button_height = 32
        self.num_cols = 3
        self.num_rows = 4

        self.col_spacing = 12  # Горизонтальний відступ між кнопками
        self.row_spacing = 12  # Вертикальний відступ між кнопками

        self.window_w = self.width()

        # 1. Розрахунок ширини сітки
        self.grid_w = (
            self.num_cols * self.button_width + (self.num_cols - 1) * self.col_spacing
        )
        # 2. Вираховуємо зсув для центрування по горизонталі
        self.grid_left = (self.window_w - self.grid_w) // 2

        self.recovery_labels = []
        self.label_grid_positions = []

        for idx in range(self.num_rows * self.num_cols):
            label = QLabel("", self.central_widget)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(self.button_width, self.button_height)
            label.hide()
            self.recovery_labels.append(label)

            row = idx // self.num_cols
            col = idx % self.num_cols
            x = self.grid_left + col * (self.button_width + self.col_spacing)
            y = self.grid_top + row * (self.button_height + self.row_spacing)
            self.label_grid_positions.append(QPoint(x, y))

        self.layout.addSpacing(210)

        # кнопка копіювання та завантаження текстового файлу
        copy_txt_layout = QHBoxLayout()
        copy_txt_layout.setContentsMargins(self.grid_left, 0, self.grid_left, 0)

        # кнопка копіювання коду
        self.copy_button = QPushButton()
        self.copy_button.clicked.connect(self.copy_code_to_clipboard)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setFixedHeight(24)
        copy_txt_layout.addWidget(
            self.copy_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # кнопка завантаження текстового файлу
        self.download_txt_button = QPushButton()
        self.download_txt_button.clicked.connect(self.save_code_to_txt)
        self.download_txt_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_txt_button.setFixedHeight(24)
        copy_txt_layout.addWidget(
            self.download_txt_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.layout.addLayout(copy_txt_layout)

        self.layout.addSpacing(55)

        # кнопка продовжити
        self.continue_button = QPushButton()
        self.continue_button.clicked.connect(self.open_sign_up_recovery_qr_window)
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.setFixedSize(220, 40)
        self.layout.addWidget(
            self.continue_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.layout.addSpacing(18)

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
        # Кнопки-слів
        phrase_label_style = style["phrase_label"]
        phrase_label_stylesheet = f"""
            QLabel {{
                background-color: {phrase_label_style["background-color"]};
                border-width: {phrase_label_style["border-width"]};
                border-radius: {phrase_label_style["border-radius"]};
                color: {phrase_label_style["color"]};
                font-size: {phrase_label_style["font-size"]};
                font-family: {phrase_label_style["font-family"]};
                font-weight: {phrase_label_style["font-weight"]};
                border-style: {phrase_label_style["border-style"]};
                border-color: {phrase_label_style["border-color"]};           
            }}
        """
        for label in self.recovery_labels:
            label.setStyleSheet(phrase_label_stylesheet)
            if phrase_label_style.get("shadow"):
                self.add_shadow(label, **phrase_label_style["shadow"])
        # Кнопка копіювання
        copy_button_style = style["copy_button"]
        copy_icon_path = resource_path(copy_button_style["icon_path"])
        self.copy_button.setIcon(QIcon(copy_icon_path))
        copy_button_stylesheet = f"""
            QPushButton {{
                text-align: {copy_button_style["text-align"]};
                padding-left: {copy_button_style["padding-left"]};
                padding-right: {copy_button_style["padding-right"]};
                background-color: {copy_button_style["background-color"]};
                border-radius: {copy_button_style["border-radius"]};
                color: {copy_button_style["color"]};
                font-size: {copy_button_style["font-size"]};
                font-family: {copy_button_style["font-family"]};
                font-weight: {copy_button_style["font-weight"]};
                border-width: {copy_button_style["border-width"]};
                border-style: {copy_button_style["border-style"]};
                border-color: {copy_button_style["border-color"]};
            }}
            QPushButton:hover {{
                background-color: {copy_button_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {copy_button_style["pressed-background-color"]};
            }}
        """
        self.copy_button.setStyleSheet(copy_button_stylesheet)
        self.add_shadow(self.copy_button, **copy_button_style["shadow"])
        # Кнопка завантаження текстового файлу
        download_txt_style = style["download_txt_button"]
        download_txt_icon_path = resource_path(download_txt_style["icon_path"])
        self.download_txt_button.setIcon(QIcon(download_txt_icon_path))
        download_txt_stylesheet = f"""
            QPushButton {{
                padding-left: {download_txt_style["padding-left"]};
                padding-right: {download_txt_style["padding-right"]};
                text-align: {download_txt_style["text-align"]};
                background-color: {download_txt_style["background-color"]};
                border-radius: {download_txt_style["border-radius"]};
                color: {download_txt_style["color"]};
                font-size: {download_txt_style["font-size"]};
                font-family: {download_txt_style["font-family"]};
                font-weight: {download_txt_style["font-weight"]};
                border-width: {download_txt_style["border-width"]};
                border-style: {download_txt_style["border-style"]};
                border-color: {download_txt_style["border-color"]};
            }}
            QPushButton:hover {{
                background-color: {download_txt_style["hover-background-color"]};
            }}
            QPushButton:pressed {{
                background-color: {download_txt_style["pressed-background-color"]};
            }}
        """
        self.download_txt_button.setStyleSheet(download_txt_stylesheet)
        self.add_shadow(self.download_txt_button, **download_txt_style["shadow"])
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
        self.instruction_label.setText(self.current_dict["recovery_phrase_instruction"])
        for label in self.recovery_labels:
            label.setText("")
            label.hide()
        for idx, word in enumerate(self.recovery_phrase):
            self.recovery_labels[idx].setText(word)
        QTimer.singleShot(200, self.animate_phrase)
        self.copy_button.setText(self.current_dict["copy_to_clipboard"])
        self.download_txt_button.setText(self.current_dict["download_txt"])
        self.continue_button.setText(self.current_dict["continue"])
        self.footer_label.setText(self.current_dict["footer"])

    def animate_phrase(self):
        self.label_animations = []
        self.current_label = 0
        self._prepare_labels_for_animation()
        self._animate_next_label()

    def _prepare_labels_for_animation(self):
        self.label_target_positions = self.label_grid_positions
        self.label_start_positions = []
        shown = set()  # індекси вже з'явлених кнопок (спочатку порожній)

        for idx, label in enumerate(self.recovery_labels):
            row = idx // self.num_cols
            col = idx % self.num_cols
            target_pos = self.label_grid_positions[idx]

            # Сусіди
            left_idx = idx - 1 if col > 0 else None
            right_idx = idx + 1 if col < self.num_cols - 1 else None
            top_idx = idx - self.num_cols if row > 0 else None
            bottom_idx = idx + self.num_cols if row < self.num_rows - 1 else None

            # Формуємо дозволені напрямки
            directions = []
            if left_idx is None or left_idx not in shown:
                directions.append("left")
            if right_idx is None or right_idx not in shown:
                directions.append("right")
            if top_idx is None or top_idx not in shown:
                directions.append("top")
            if bottom_idx is None or bottom_idx not in shown:
                directions.append("bottom")

            direction = random.choice(directions)
            offset = 120

            if direction == "left":
                start_pos = QPoint(target_pos.x() - offset, target_pos.y())
            elif direction == "right":
                start_pos = QPoint(target_pos.x() + offset, target_pos.y())
            elif direction == "top":
                start_pos = QPoint(target_pos.x(), target_pos.y() - offset)
            else:  # "bottom"
                start_pos = QPoint(target_pos.x(), target_pos.y() + offset)

            self.label_start_positions.append(start_pos)
            label.move(start_pos)

            # Прозорість
            opacity_effect = QGraphicsOpacityEffect()
            label.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(0)

            shown.add(idx)  # відмічаємо, що ця кнопка вже з'явилась

    def _animate_next_label(self):
        if self.current_label >= len(self.recovery_phrase):
            return
        label = self.recovery_labels[self.current_label]
        label.show()
        target_pos = self.label_grid_positions[self.current_label]
        start_pos = self.label_start_positions[self.current_label]
        opacity_effect = label.graphicsEffect()
        pos_anim = QPropertyAnimation(label, b"pos")
        pos_anim.setDuration(550)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(target_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(400)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        pos_anim.start()
        fade_anim.start()
        self.label_animations.append((pos_anim, fade_anim))
        self.current_label += 1
        QTimer.singleShot(200, self._animate_next_label)

    def copy_code_to_clipboard(self):
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(" ".join(self.recovery_phrase))

    def save_code_to_txt(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, None, "neuro_recovery_code.txt", "Text Files (*.txt)"  # системна мова
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(" ".join(self.recovery_phrase))

    def open_sign_up_recovery_qr_window(self):
        self.continue_button.setEnabled(False)
        self.sign_up_recovery_qr_window = SignUpRecoveryQRWindow(
            self.current_lang, self.current_style, self.recovery_phrase
        )
        self.sign_up_recovery_qr_window.show()
        self.close()
