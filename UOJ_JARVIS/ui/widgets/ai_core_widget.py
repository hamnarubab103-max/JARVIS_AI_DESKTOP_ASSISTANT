# ui/widgets/ai_core_widget.py

import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient


class AICoreWidget(QWidget):
    """
    Professional animated AI core.
    States:
    - idle
    - listening
    - thinking
    - speaking
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(260, 260)

        self.state = "idle"
        self.angle = 0
        self.pulse = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    # ---------------- Set State ----------------
    def set_state(self, state):
        self.state = state

    # ---------------- Animation ----------------
    def animate(self):
        self.angle = (self.angle + 2) % 360
        self.pulse += 0.05
        self.update()

    # ---------------- Paint ----------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2

        base_radius = min(w, h) // 4

        # ---------------- Glow core ----------------
        glow_radius = base_radius + int(math.sin(self.pulse) * 6)

        gradient = QRadialGradient(cx, cy, glow_radius * 2)
        gradient.setColorAt(0, QColor(0, 255, 255, 200))
        gradient.setColorAt(1, QColor(0, 255, 255, 20))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - glow_radius, cy - glow_radius,
                            glow_radius * 2, glow_radius * 2)

        # ---------------- Core circle ----------------
        painter.setBrush(QColor(0, 255, 255, 180))
        painter.drawEllipse(cx - base_radius,
                            cy - base_radius,
                            base_radius * 2,
                            base_radius * 2)

        # ---------------- State-specific effects ----------------
        if self.state == "thinking":
            self.draw_rotating_rings(painter, cx, cy, base_radius)

        elif self.state == "listening":
            self.draw_waveform(painter, cx, cy, base_radius)

        elif self.state == "speaking":
            self.draw_expanding_ring(painter, cx, cy, base_radius)

    # ---------------- Thinking animation ----------------
    def draw_rotating_rings(self, painter, cx, cy, radius):
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(0, 255, 255, 150), 3))

        for i in range(2):
            r = radius + 20 + i * 15
            angle = self.angle + i * 60
            start = int(angle * 16)
            span = int(120 * 16)
            painter.drawArc(cx - r, cy - r, r * 2, r * 2, start, span)

    # ---------------- Listening animation ----------------
    def draw_waveform(self, painter, cx, cy, radius):
        painter.setPen(QPen(QColor(0, 255, 255, 200), 2))

        bars = 32
        for i in range(bars):
            angle = (360 / bars) * i + self.angle
            rad = math.radians(angle)

            height = radius + math.sin(self.pulse * 4 + i) * 10

            x1 = cx + math.cos(rad) * radius
            y1 = cy + math.sin(rad) * radius
            x2 = cx + math.cos(rad) * height
            y2 = cy + math.sin(rad) * height

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    # ---------------- Speaking animation ----------------
    def draw_expanding_ring(self, painter, cx, cy, radius):
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(0, 255, 255, 120), 4))

        expand = int((math.sin(self.pulse * 2) + 1) * 10)
        r = radius + expand
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)