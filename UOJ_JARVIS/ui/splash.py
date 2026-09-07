from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap


class SplashScreen(QWidget):
    # signal for main.py
    done = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setFixedSize(420, 300)
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("assets/images/logo.png")

        if pixmap.isNull():
            logo.setText("LOGO NOT FOUND")
            logo.setStyleSheet("color:white; font-size:18px;")
        else:
            logo.setPixmap(
                pixmap.scaled(
                    220,
                    220,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # splash screen for 2 seconds
        QTimer.singleShot(2000, self.finish_splash)

    def finish_splash(self):
        self.done.emit()
        self.close()