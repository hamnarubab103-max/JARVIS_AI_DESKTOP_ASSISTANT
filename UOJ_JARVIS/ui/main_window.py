import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

from ui.splash import SplashScreen
from ui.dashboard import Dashboard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UNIVERSTY OF JHANG (AI)")
        self.setGeometry(150, 150, 1200, 700)

        self.setCentralWidget(Dashboard())


def run_ui():
    app = QApplication(sys.argv)

    # 🔥 THIS LINE PREVENTS AUTO EXIT
    app.setQuitOnLastWindowClosed(False)

    splash = SplashScreen()
    main_window = MainWindow()

    splash.show()

    def start_app():
        print("Main UI shown")  # debug proof
        main_window.show()
        splash.close()

    QTimer.singleShot(2500, start_app)

    sys.exit(app.exec_())
