"""
memory/alarms.py  —  Persistent alarms and in-memory reminders.
"""

import json
import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from core.config import ALARMS_FILE


class AlarmStore(QObject):
    """Persistent daily/one-shot alarms.  Fires alarm_fired(label) signal."""

    alarm_fired = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._alarms = self._load()
        self._timer  = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._check)
        self._timer.start()

    # ── Persistence ───────────────────────────────────────────────────────
    def _load(self):
        try:
            with open(ALARMS_FILE, "r") as f:
                data = json.load(f)
            return [
                (datetime.datetime.fromisoformat(a[0]), a[1], a[2])
                for a in data
            ]
        except Exception:
            return []

    def _save(self):
        try:
            with open(ALARMS_FILE, "w") as f:
                json.dump(
                    [(a[0].isoformat(), a[1], a[2]) for a in self._alarms], f
                )
        except Exception as e:
            print(f"[ALARM SAVE] {e}")

    # ── API ───────────────────────────────────────────────────────────────
    def add_alarm(self, label: str, when: datetime.datetime,
                  repeat: bool = False) -> str:
        self._alarms.append((when, label, repeat))
        self._save()
        diff = when - datetime.datetime.now()
        mins = max(0, int(diff.total_seconds() / 60))
        return (f"Alarm set for {when.strftime('%I:%M %p')} — {label}, sir. "
                f"That is in {mins} minutes.")

    def list_alarms(self) -> str:
        now   = datetime.datetime.now()
        lines = [
            f"{i+1}. {a[0].strftime('%I:%M %p')} — {a[1]} "
            f"({'daily' if a[2] else 'once'})"
            for i, a in enumerate(self._alarms) if a[0] > now
        ]
        if not lines:
            return "No active alarms, sir."
        return "Active alarms:\n" + "\n".join(lines)

    def delete_alarm(self, idx=None) -> str:
        if idx is None:
            self._alarms = []
            self._save()
            return "All alarms cleared, sir."
        try:
            r = self._alarms.pop(int(idx) - 1)
            self._save()
            return f"Alarm '{r[1]}' deleted, sir."
        except (IndexError, ValueError):
            return "Could not delete alarm, sir."

    # ── Tick ──────────────────────────────────────────────────────────────
    def _check(self):
        now  = datetime.datetime.now()
        keep = []
        for when, label, repeat in self._alarms:
            if now >= when:
                self.alarm_fired.emit(label)
                if repeat:
                    keep.append((
                        when + datetime.timedelta(days=1), label, repeat
                    ))
            else:
                keep.append((when, label, repeat))
        if len(keep) != len(self._alarms):
            self._alarms = keep
            self._save()


class ReminderStore(QObject):
    """In-memory reminders (not persisted).  Fires fired(text) signal."""

    fired = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._list  = []
        self._timer = QTimer(self)
        self._timer.setInterval(8000)
        self._timer.timeout.connect(self._check)
        self._timer.start()

    def add(self, text: str, when: datetime.datetime) -> None:
        self._list.append((when, text))

    def list_all(self) -> str:
        if not self._list:
            return "No reminders set, sir."
        now   = datetime.datetime.now()
        lines = [
            f"  {t}  (in ~{max(0, int((w - now).total_seconds() / 60))} min)"
            for w, t in self._list
        ]
        return "Reminders:\n" + "\n".join(lines)

    def _check(self):
        now  = datetime.datetime.now()
        keep = []
        for when, text in self._list:
            if now >= when:
                self.fired.emit(text)
            else:
                keep.append((when, text))
        self._list = keep