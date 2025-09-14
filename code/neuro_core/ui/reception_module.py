import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from neuro_core.ui.windows.login_window import LoginWindow
from neuro_core.neuro_ai.action_detection.main import ActionDetection


def main():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    login_window = LoginWindow()
    login_window.show()

    # TODO: Delete after testing
    # action_detection = ActionDetection(user_name="test_user")
    # action_detection.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
