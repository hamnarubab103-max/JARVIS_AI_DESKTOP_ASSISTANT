"""
J.A.R.V.I.S  v10.0  —  Ultra Pro Iron Man HUD Dashboard
Entry Point
Developed by: Amina Sikandar | Hamna Rubab | Eesha Jewan
International Expo Edition
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from ui.splash import SplashScreen
from ui.dashboard import Dashboard


def apply_dark_palette(app: QApplication) -> None:
    """Apply the Iron Man HUD dark palette globally."""
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(3,   8, 22))
    pal.setColor(QPalette.WindowText,      QColor(0, 220, 255))
    pal.setColor(QPalette.Base,            QColor(3,   6, 18))
    pal.setColor(QPalette.AlternateBase,   QColor(6,  12, 32))
    pal.setColor(QPalette.ToolTipBase,     QColor(0, 220, 255))
    pal.setColor(QPalette.ToolTipText,     QColor(3,   6, 18))
    pal.setColor(QPalette.Text,            QColor(0, 200, 255))
    pal.setColor(QPalette.Button,          QColor(6,  12, 32))
    pal.setColor(QPalette.ButtonText,      QColor(0, 200, 255))
    pal.setColor(QPalette.BrightText,      Qt.white)
    pal.setColor(QPalette.Highlight,       QColor(0, 160, 255))
    pal.setColor(QPalette.HighlightedText, QColor(3,   6, 18))
    app.setPalette(pal)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("J.A.R.V.I.S v10.0")
    app.setApplicationVersion("10.0")
    app.setOrganizationName("JARVIS Labs — Amina | Hamna | Eesha")
    app.setStyle("Fusion")
    apply_dark_palette(app)

    splash = SplashScreen()
    splash.show()

    dashboard_ref = []  # keep reference alive

    def launch():
        d = Dashboard()
        dashboard_ref.append(d)
        d.showMaximized()

    splash.done.connect(launch)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()