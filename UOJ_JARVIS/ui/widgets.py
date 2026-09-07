"""
ui/widgets.py  —  All custom Iron Man HUD widgets.
"""

import math
import time
import random
import os

import numpy as np
from PyQt5.QtWidgets import QWidget, QFrame, QScrollArea, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui     import (QPainter, QColor, QFont, QPen, QBrush, QRadialGradient,
                              QLinearGradient, QConicalGradient, QPolygonF, QPainterPath,
                              QPixmap)
from PyQt5.QtCore    import Qt, QTimer, QRect, QPoint, QPointF

from core.config import (CYAN, CYAN_DIM, CYAN_GLOW, GREEN, AMBER, RED_HUD,
                          PURPLE, BG_DEEP, BG_IMAGE)


# ══════════════════════════════════════════════════════════════════════════
#  HEX BACKGROUND
# ══════════════════════════════════════════════════════════════════════════
class HexBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._off   = 0.0
        self._scan  = 0.0
        self._bg_px = None
        self._load_bg()
        QTimer(self, timeout=self._tick, interval=40).start()

    def _load_bg(self):
        if os.path.isfile(BG_IMAGE):
            try:
                self._bg_px = QPixmap(BG_IMAGE)
            except Exception:
                self._bg_px = None

    def _tick(self):
        self._off  = (self._off + 0.25) % 60
        self._scan = (self._scan + 1.0) % (self.height() or 900)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if not w or not h:
            return
        if self._bg_px and not self._bg_px.isNull():
            scaled = self._bg_px.scaled(
                w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (w - scaled.width())  // 2
            y = (h - scaled.height()) // 2
            p.setOpacity(0.18)
            p.drawPixmap(x, y, scaled)
            p.setOpacity(1.0)
        p.fillRect(0, 0, w, h, QColor(3, 8, 22, 200))
        sz, dx, dy = 24, 24*1.732, 24*1.5
        p.setPen(QPen(QColor(0, 120, 255, 5), 0.6))
        row = 0
        y   = -dy + (self._off * 0.5 % dy)
        while y < h + dy:
            x = -dx + ((dx/2) if row % 2 else 0)
            while x < w + dx:
                pts = [
                    QPointF(x + sz * math.cos(math.radians(60*i-30)) * 0.78,
                            y + sz * math.sin(math.radians(60*i-30)) * 0.78)
                    for i in range(6)
                ]
                p.drawPolygon(QPolygonF(pts))
                x += dx
            y   += dy
            row += 1
        sg = QLinearGradient(0, self._scan-60, 0, self._scan+60)
        sg.setColorAt(0.0, QColor(0, 180, 255, 0))
        sg.setColorAt(0.5, QColor(0, 180, 255, 10))
        sg.setColorAt(1.0, QColor(0, 180, 255, 0))
        p.fillRect(0, int(self._scan)-60, w, 120, QBrush(sg))


# ══════════════════════════════════════════════════════════════════════════
#  ARC REACTOR
# ══════════════════════════════════════════════════════════════════════════
class ArcReactor(QWidget):
    def __init__(self, sz=140):
        super().__init__()
        self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._angle       = 0.0
        self._pulse       = 0.0
        self._energy      = 1.0
        self._spark       = 0.0
        self._outer_angle = 0.0
        self._ripple      = 0.0
        QTimer(self, timeout=self._tick, interval=16).start()

    def set_energy(self, v: float):
        self._energy = max(0.0, min(1.0, float(v)))

    def _tick(self):
        self._angle       = (self._angle       + 2.8)  % 360
        self._outer_angle = (self._outer_angle  - 1.2)  % 360
        self._pulse      += 0.08
        self._spark       = (self._spark        + 0.18) % 360
        self._ripple      = (self._ripple       + 0.05) % 1.0
        self.update()

    def paintEvent(self, _):
        p  = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx = cy = self.width() // 2
        R  = cx - 4
        e  = self._energy
        pv = 0.8 + 0.2 * math.sin(self._pulse * 2.5)
        for i in range(8):
            a = max(0, int(45-i*7)*e)
            p.setPen(QPen(QColor(0, int(200*e), int(255*e), int(a)), 2-i*.15))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx, cy), R+i*5, R+i*5)
        rr = int(R*(0.9 + self._ripple*0.4))
        ra = int(max(0, 80*(1-self._ripple)))
        p.setPen(QPen(QColor(0, 230, 255, int(ra*e)), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPoint(cx, cy), rr, rr)
        p.save(); p.translate(cx, cy); p.rotate(self._outer_angle)
        for i in range(12):
            a1 = math.radians(i*30); a2 = math.radians(i*30+22)
            ri, ro = int(R*.82), int(R*.96)
            pts = [
                QPointF(math.cos(a1)*ri, math.sin(a1)*ri),
                QPointF(math.cos(a1)*ro, math.sin(a1)*ro),
                QPointF(math.cos(a2)*ro, math.sin(a2)*ro),
                QPointF(math.cos(a2)*ri, math.sin(a2)*ri),
            ]
            al = int(70 + 50*math.sin(self._pulse*1.5 + i*.5))
            p.setBrush(QBrush(QColor(0, int(160*e), int(240*e), int(al*e))))
            p.setPen(QPen(QColor(0, int(220*e), 255, int(160*e)), 0.8))
            p.drawPolygon(QPolygonF(pts))
        p.restore()
        p.save(); p.translate(cx, cy); p.rotate(self._angle)
        for i in range(6):
            a1 = math.radians(i*60); a2 = math.radians(i*60+52)
            ri, ro = int(R*.44), int(R*.76)
            pts = [
                QPointF(math.cos(a1)*ri, math.sin(a1)*ri),
                QPointF(math.cos(a1)*ro, math.sin(a1)*ro),
                QPointF(math.cos(a2)*ro, math.sin(a2)*ro),
                QPointF(math.cos(a2)*ri, math.sin(a2)*ri),
            ]
            al = int(100 + 70*math.sin(self._pulse + i))
            p.setBrush(QBrush(QColor(0, int(180*e), int(255*e), int(al*e))))
            p.setPen(QPen(QColor(0, int(230*e), 255, int(200*e)), 1.2))
            p.drawPolygon(QPolygonF(pts))
        p.restore()
        p.save(); p.translate(cx, cy)
        hex_pts = [
            QPointF(math.cos(math.radians(i*60+30))*int(R*.36),
                    math.sin(math.radians(i*60+30))*int(R*.36))
            for i in range(6)
        ]
        p.setPen(QPen(QColor(0, int(200*e), 255, int(130*e)), 1.5))
        p.setBrush(QBrush(QColor(0, 30, 80, 50)))
        p.drawPolygon(QPolygonF(hex_pts))
        p.restore()
        cr = int(R*.28)
        g  = QRadialGradient(cx, cy, cr)
        g.setColorAt(0.0,  QColor(230, 250, 255, int(245*e*pv)))
        g.setColorAt(0.35, QColor(0,   220, 255, int(220*e*pv)))
        g.setColorAt(0.7,  QColor(0,   100, 220, int(120*e)))
        g.setColorAt(1.0,  QColor(0,    30,  80,  20))
        p.setBrush(QBrush(g))
        p.setPen(QPen(QColor(0, 240, 255, 220), 1.5))
        p.drawEllipse(QPoint(cx, cy), cr, cr)
        sa = math.radians(self._spark*360/360)
        sx = int(cx + math.cos(sa)*R*.72)
        sy = int(cy + math.sin(sa)*R*.72)
        sg2 = QRadialGradient(sx, sy, 5)
        sg2.setColorAt(0, QColor(255, 255, 255, 220))
        sg2.setColorAt(1, QColor(0,   200, 255,   0))
        p.setBrush(QBrush(sg2)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(sx, sy), 5, 5)
        p.setFont(QFont("Consolas", 6, QFont.Bold))
        p.setPen(QColor(0, int(200*e), 255, int(160*e)))
        p.drawText(QRect(0, cy+cr+2, self.width(), 12), Qt.AlignCenter, "JARVIS")


# ══════════════════════════════════════════════════════════════════════════
#  RADAR WIDGET
# ══════════════════════════════════════════════════════════════════════════
class RadarWidget(QWidget):
    def __init__(self, sz=140, label="SCAN"):
        super().__init__()
        self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label  = label
        self._angle = 0.0
        self._blips = [
            (random.uniform(0.2, 0.85), random.uniform(0, 360), random.randint(2, 5))
            for _ in range(random.randint(4, 7))
        ]
        QTimer(self, timeout=self._tick, interval=18).start()

    def _tick(self):
        self._angle = (self._angle + 2.2) % 360
        self.update()

    def paintEvent(self, _):
        p  = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx = cy = self.width() // 2
        R  = cx - 4
        bg = QRadialGradient(cx, cy, R)
        bg.setColorAt(0, QColor(0, 50, 20, 200))
        bg.setColorAt(1, QColor(0, 10,  5, 230))
        p.setBrush(QBrush(bg)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(cx, cy), R, R)
        for r in [.25, .5, .75, 1.0]:
            p.setPen(QPen(QColor(0, 200, 80, int(25+r*20)), 0.8))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx, cy), int(R*r), int(R*r))
        p.setPen(QPen(QColor(0, 200, 80, 30), 0.6))
        p.drawLine(cx-R, cy, cx+R, cy); p.drawLine(cx, cy-R, cx, cy+R)
        p.save(); p.translate(cx, cy); p.rotate(self._angle)
        sweep = QConicalGradient(0, 0, -90)
        sweep.setColorAt(0.0,  QColor(0, 255,  80, 150))
        sweep.setColorAt(0.2,  QColor(0, 255,  80,  30))
        sweep.setColorAt(0.21, QColor(0,   0,   0,   0))
        sweep.setColorAt(1.0,  QColor(0,   0,   0,   0))
        p.setBrush(QBrush(sweep)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(0, 0), R-1, R-1)
        p.setPen(QPen(QColor(0, 255, 80, 220), 1.5))
        p.drawLine(0, 0, R-1, 0)
        p.restore()
        for dist, angle, sz2 in self._blips:
            ba    = math.radians(angle + self._angle*.2)
            bx    = int(cx + math.cos(ba)*R*dist)
            by    = int(cy + math.sin(ba)*R*dist)
            diff  = abs((self._angle - angle + 360) % 360)
            alpha = int(min(255, 220*(1-diff/100))) if diff < 100 else 0
            if alpha > 20:
                p.setBrush(QBrush(QColor(0, 255, 80, alpha)))
                p.setPen(QPen(QColor(0, 255, 80, alpha//2), 1))
                p.drawEllipse(QPoint(bx, by), sz2//2, sz2//2)
        p.setPen(QColor(0, 180, 80, 140))
        p.setFont(QFont("Consolas", 7, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, self.label)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(0, 220, 80, 90), 1.5))
        p.drawEllipse(QPoint(cx, cy), R, R)


# ══════════════════════════════════════════════════════════════════════════
#  VOICE ORB
# ══════════════════════════════════════════════════════════════════════════
class VoiceOrb(QWidget):
    def __init__(self, sz=130):
        super().__init__()
        self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.level  = 8
        self._pulse = 0.0
        self.state  = "idle"
        self._bars  = np.zeros(80)
        QTimer(self, timeout=self._tick, interval=20).start()

    def set_level(self, v: int):
        self.level = max(5, min(int(v), 100))

    def set_state(self, s: str):
        self.state = s

    def _tick(self):
        self._pulse += 0.12
        target = self.level/100.0 if self.state in ("listening", "speaking") else 0.04
        for i in range(len(self._bars)):
            noise = random.uniform(0, target) * abs(math.sin(self._pulse + i*.3))
            self._bars[i] += (noise - self._bars[i]) * .28
        self.update()

    def paintEvent(self, _):
        p  = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx = cy = self.width() // 2
        R  = cx - 6
        cmap = {
            "listening":    (0, 255, 140),
            "processing":   (255, 160,   0),
            "speaking":     (0, 210, 255),
            "thinking":     (180,  80, 255),
            "idle":         (0, 120, 220),
            "calibrating":  (255, 200,   0),
        }
        rc = QColor(*cmap.get(self.state, (0, 150, 200)))
        for i in range(7):
            a = max(0, 50 - i*8)
            p.setPen(QPen(QColor(rc.red(), rc.green(), rc.blue(), a), 8-i*.8))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx, cy), R+i*4, R+i*4)
        n = len(self._bars)
        for i, amp in enumerate(self._bars):
            angle = 2*math.pi*i/n
            r1    = R*.5
            r2    = r1 + amp*R*.48
            al    = min(255, int(80 + amp*450))
            p.setPen(QPen(QColor(rc.red(), rc.green(), rc.blue(), al), 2.2))
            p.drawLine(
                int(cx + math.cos(angle)*r1), int(cy + math.sin(angle)*r1),
                int(cx + math.cos(angle)*r2), int(cy + math.sin(angle)*r2),
            )
        gr = QRadialGradient(cx, cy, int(R*.5))
        gr.setColorAt(0, QColor(rc.red(), rc.green(), rc.blue(), 65))
        gr.setColorAt(1, QColor(5, 8, 22, 210))
        p.setBrush(QBrush(gr)); p.setPen(QPen(rc, 1.5))
        p.drawEllipse(QPoint(cx, cy), int(R*.5), int(R*.5))
        icon_map = {
            "listening":   "🎤", "processing": "⟳",  "speaking":    "◎",
            "thinking":    "⋯",  "idle":        "◌",  "calibrating": "⊛",
        }
        p.setPen(QPen(rc, 2)); p.setFont(QFont("Segoe UI Symbol", 14))
        p.drawText(QRect(0, -8, self.width(), self.height()),
                   Qt.AlignCenter, icon_map.get(self.state, "◌"))
        p.setPen(QColor(rc.red(), rc.green(), rc.blue(), 180))
        p.setFont(QFont("Consolas", 7, QFont.Bold))
        p.drawText(QRect(0, self.height()-16, self.width(), 16),
                   Qt.AlignCenter, self.state.upper())
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(rc.red(), rc.green(), rc.blue(), 100), 1.5))
        p.drawEllipse(QPoint(cx, cy), R, R)


# ══════════════════════════════════════════════════════════════════════════
#  MINI RING GAUGE
# ══════════════════════════════════════════════════════════════════════════
class MiniRing(QWidget):
    def __init__(self, label, color, sz=80):
        super().__init__()
        self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label  = label
        self.value  = 0
        self._disp  = 0.0
        self.color  = QColor(*color)
        QTimer(self, timeout=self._smooth, interval=22).start()

    def set_value(self, v):
        self.value = max(0, min(100, float(v)))

    def _smooth(self):
        self._disp += (self.value - self._disp) * .10
        self.update()

    def paintEvent(self, _):
        p  = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx = cy = self.width() // 2
        R  = self.width() // 2 - 6
        p.setPen(QPen(QColor(self.color.red(), self.color.green(),
                             self.color.blue(), 20), 8))
        p.setBrush(Qt.NoBrush)
        p.drawArc(cx-R, cy-R, R*2, R*2, 90*16, -360*16)
        for i in range(3):
            pen = QPen(
                QColor(self.color.red(), self.color.green(),
                       self.color.blue(), 30-i*8), 10+i*2
            )
            pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
            p.drawArc(cx-R, cy-R, R*2, R*2,
                      90*16, -int(360*self._disp/100)*16)
        pen = QPen(self.color, 7); pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
        p.drawArc(cx-R, cy-R, R*2, R*2, 90*16, -int(360*self._disp/100)*16)
        p.setPen(self.color)
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        p.drawText(QRect(0, -4, self.width(), self.height()),
                   Qt.AlignCenter, f"{int(self._disp)}%")
        p.setFont(QFont("Consolas", 7))
        p.setPen(QColor(self.color.red(), self.color.green(),
                        self.color.blue(), 160))
        p.drawText(QRect(0, 12, self.width(), self.height()),
                   Qt.AlignCenter, self.label)
        if self._disp > 85:
            a = int(20*abs(math.sin(time.time()*5)))
            p.setBrush(QBrush(QColor(255, 50, 50, a)))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(cx, cy), R+8, R+8)


# ══════════════════════════════════════════════════════════════════════════
#  NETWORK WAVE
# ══════════════════════════════════════════════════════════════════════════
class NetWave(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.vals = np.zeros(100)
        self.setFixedHeight(40)

    def push(self, v):
        self.vals = np.roll(self.vals, -1)
        self.vals[-1] = float(np.clip(v, 0, 1))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        mid  = h * .8
        step = w / max(len(self.vals)-1, 1)
        path = QPainterPath()
        path.moveTo(0, mid)
        for i, v in enumerate(self.vals):
            path.lineTo(i*step, mid - v*mid*.85)
        path.lineTo(w, mid); path.lineTo(0, mid)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(0, 180, 255, 50))
        grad.setColorAt(1.0, QColor(0, 180, 255,  0))
        p.fillPath(path, QBrush(grad))
        lg = QLinearGradient(0, 0, w, 0)
        lg.setColorAt(0.0, QColor(0,  80, 200,  60))
        lg.setColorAt(0.5, QColor(0, 200, 255, 220))
        lg.setColorAt(1.0, QColor(0, 255, 180, 255))
        p.setPen(QPen(QBrush(lg), 1.5))
        for i in range(len(self.vals)-1):
            p.drawLine(
                int(i*step),     int(mid - self.vals[i]*mid*.85),
                int((i+1)*step), int(mid - self.vals[i+1]*mid*.85),
            )


# ══════════════════════════════════════════════════════════════════════════
#  HUD CORNER BRACKETS
# ══════════════════════════════════════════════════════════════════════════
class HUDCorner(QWidget):
    def __init__(self, corner="tl", sz=50, color=(0, 200, 255)):
        super().__init__()
        self.setFixedSize(sz, sz)
        self.corner = corner
        self._pulse = 0.0
        self._color = color
        self.setAttribute(Qt.WA_TranslucentBackground)
        QTimer(self, timeout=self._tick, interval=30).start()

    def _tick(self):
        self._pulse += 0.08
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        L = min(w, h)//2 + 4
        a = int(140 + 80*math.sin(self._pulse))
        r, g, b = self._color
        c = self.corner
        p.setPen(QPen(QColor(r, g, b, a), 2))
        if c == "tl":   p.drawLine(0, L, 0, 0); p.drawLine(0, 0, L, 0)
        elif c == "tr": p.drawLine(w-L, 0, w, 0); p.drawLine(w, 0, w, L)
        elif c == "bl": p.drawLine(0, h-L, 0, h); p.drawLine(0, h, L, h)
        elif c == "br": p.drawLine(w-L, h, w, h); p.drawLine(w, h-L, w, h)
        p.setPen(QPen(QColor(r, g, b, int(a*.4)), 4))
        if c == "tl":   p.drawLine(0, L-2, 0, 2); p.drawLine(2, 0, L-2, 0)
        elif c == "tr": p.drawLine(w-L+2, 0, w, 0); p.drawLine(w, 0, w, L-2)
        elif c == "bl": p.drawLine(0, h-L+2, 0, h); p.drawLine(0, h, L-2, h)
        elif c == "br": p.drawLine(w-L+2, h, w, h); p.drawLine(w, h-L+2, w, h)
        dot_a = int(120 + 80*math.sin(self._pulse*1.3))
        cx2 = 3 if c in ("tl", "bl") else w-3
        cy2 = 3 if c in ("tl", "tr") else h-3
        p.setBrush(QBrush(QColor(r, g, b, dot_a))); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(cx2, cy2), 3, 3)


# ══════════════════════════════════════════════════════════════════════════
#  POWER BAR
# ══════════════════════════════════════════════════════════════════════════
class PowerBar(QWidget):
    def __init__(self, label="POWER LEVEL", color=(0, 255, 140)):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(28)
        self.label  = label
        self.value  = 100
        self._disp  = 0.0
        self.color  = QColor(*color)
        self._pulse = 0.0
        QTimer(self, timeout=self._smooth, interval=22).start()

    def set_value(self, v):
        self.value = max(0, min(100, float(v)))

    def _smooth(self):
        self._disp  += (self.value - self._disp) * .08
        self._pulse += 0.08
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pv   = 0.85 + 0.15*math.sin(self._pulse*2)
        bar_x, bar_w = 130, w - 140
        bar_h, bar_y = 8, (h-8)//2
        p.setFont(QFont("Consolas", 8, QFont.Bold))
        p.setPen(QColor(self.color.red(), self.color.green(),
                        self.color.blue(), 180))
        p.drawText(0, 0, 120, h, Qt.AlignVCenter|Qt.AlignLeft, self.label)
        p.setBrush(QBrush(QColor(self.color.red(), self.color.green(),
                                 self.color.blue(), 18)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)
        fw = int(bar_w * self._disp / 100)
        if fw > 0:
            gd = QLinearGradient(bar_x, 0, bar_x+bar_w, 0)
            gd.setColorAt(0,   QColor(0, 150,  80, int(200*pv)))
            gd.setColorAt(0.7, QColor(self.color.red(), self.color.green(),
                                      self.color.blue(), int(240*pv)))
            gd.setColorAt(1,   QColor(255, 255, 255, int(200*pv)))
            p.setBrush(QBrush(gd))
            p.drawRoundedRect(bar_x, bar_y, fw, bar_h, 4, 4)
        p.setFont(QFont("Consolas", 8, QFont.Bold))
        p.setPen(QColor(self.color.red(), self.color.green(),
                        self.color.blue(), 220))
        p.drawText(bar_x+bar_w+4, 0, 45, h,
                   Qt.AlignVCenter, f"{int(self._disp)}%")


# ══════════════════════════════════════════════════════════════════════════
#  CIRCULAR GAUGE
# ══════════════════════════════════════════════════════════════════════════
class CircularGauge(QWidget):
    def __init__(self, label, color, sz=120, unit="%"):
        super().__init__()
        self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label  = label
        self.unit   = unit
        self.value  = 0
        self._disp  = 0.0
        self.color  = QColor(*color)
        self._pulse = 0.0
        QTimer(self, timeout=self._smooth, interval=22).start()

    def set_value(self, v):
        self.value = max(0, min(100, float(v)))

    def _smooth(self):
        self._disp  += (self.value - self._disp) * .08
        self._pulse += 0.07
        self.update()

    def paintEvent(self, _):
        p  = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx = cy = self.width()  // 2
        R  = self.width() // 2 - 10
        for i in range(4):
            pen = QPen(QColor(self.color.red(), self.color.green(),
                              self.color.blue(), 12-i*2), 14-i*2)
            p.setPen(pen); p.setBrush(Qt.NoBrush)
            p.drawArc(cx-R, cy-R, R*2, R*2, -40*16, -(360-80)*16)
        p.setPen(QPen(QColor(self.color.red(), self.color.green(),
                             self.color.blue(), 18), 8))
        p.drawArc(cx-R, cy-R, R*2, R*2, -40*16, -(360-80)*16)
        for i in range(3):
            gpen = QPen(QColor(self.color.red(), self.color.green(),
                               self.color.blue(), 30-i*8), 11+i*2)
            gpen.setCapStyle(Qt.RoundCap); p.setPen(gpen)
            sweep = int((360-80)*self._disp/100)
            p.drawArc(cx-R, cy-R, R*2, R*2, -40*16, -sweep*16)
        pen = QPen(self.color, 8); pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
        sweep = int((360-80)*self._disp/100)
        p.drawArc(cx-R, cy-R, R*2, R*2, -40*16, -sweep*16)
        p.setPen(self.color)
        p.setFont(QFont("Consolas", 12, QFont.Bold))
        p.drawText(QRect(0, -8, self.width(), self.height()),
                   Qt.AlignCenter, f"{int(self._disp)}{self.unit}")
        p.setFont(QFont("Consolas", 7))
        p.setPen(QColor(self.color.red(), self.color.green(),
                        self.color.blue(), 150))
        p.drawText(QRect(0, 12, self.width(), self.height()),
                   Qt.AlignCenter, self.label)
        if self._disp > 85:
            pv2 = 0.8 + 0.2*math.sin(self._pulse*2)
            a   = int(18*abs(math.sin(time.time()*5))*pv2)
            p.setBrush(QBrush(QColor(255, 50, 50, a))); p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(cx, cy), R+10, R+10)


# ══════════════════════════════════════════════════════════════════════════
#  CHAT BUBBLE + CHAT AREA
# ══════════════════════════════════════════════════════════════════════════
import html as _html

class ChatBubble(QFrame):
    def __init__(self, role: str, text: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 2, 6, 2)
        is_user = (role == "user")
        if is_user:
            lay.addStretch()
        lbl = QLabel(_html.escape(str(text)))
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(560)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if is_user:
            lbl.setStyleSheet(
                "background:rgba(0,100,180,55);color:#b8e8ff;"
                "border:1px solid rgba(0,160,255,50);"
                "border-radius:12px 12px 2px 12px;"
                "padding:9px 14px;font-family:Consolas;font-size:12px;"
            )
        else:
            lbl.setStyleSheet(
                "background:rgba(0,20,60,140);color:#00eedd;"
                "border:1px solid rgba(0,210,255,30);"
                "border-radius:12px 12px 12px 2px;"
                "padding:9px 14px;font-family:Consolas;font-size:12px;"
            )
        lay.addWidget(lbl)
        if not is_user:
            lay.addStretch()


class ChatArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{width:4px;background:transparent;}"
            "QScrollBar::handle:vertical{background:rgba(0,180,255,45);border-radius:2px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}"
        )
        self._container = QWidget()
        self._container.setStyleSheet("background:transparent;")
        self._layout    = QVBoxLayout(self._container)
        self._layout.setSpacing(4)
        self._layout.setContentsMargins(6, 10, 6, 10)
        self._layout.addStretch()
        self.setWidget(self._container)

    def add_message(self, role: str, text: str):
        bubble = ChatBubble(role, text)
        self._layout.insertWidget(self._layout.count()-1, bubble)
        QTimer.singleShot(
            50,
            lambda: self.verticalScrollBar().setValue(
                self.verticalScrollBar().maximum()
            ),
        )

    def add_system(self, text: str):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"color:{CYAN_DIM};font-family:Consolas;font-size:9px;"
            f"padding:4px;background:rgba(0,50,100,18);border-radius:4px;"
        )
        self._layout.insertWidget(self._layout.count()-1, lbl)