"""
voice/listener.py  —  Speech-to-text background worker.
Supports wake-word mode and always-on mode.
"""

import re
import random
import threading
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal
from core.config import WAKE_WORDS
from core.deps   import SR_OK, sr
from utils.sound import SoundFX


class VoiceWorker(QThread):
    text_received = pyqtSignal(str)   # recognised text (clean)
    state_changed = pyqtSignal(str)   # idle / listening / processing / calibrating
    level_changed = pyqtSignal(int)   # 0-100 mic level
    log_msg       = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running         = True
        self._paused          = False
        self._wake_word_mode  = True
        self._mic_device_idx  = None
        self._lock            = threading.Lock()

    # ── Control ───────────────────────────────────────────────────────────
    def pause(self):
        with self._lock: self._paused = True

    def resume(self):
        with self._lock: self._paused = False

    def set_always_on(self, enabled: bool):
        self._wake_word_mode = not bool(enabled)

    def stop(self):
        self._running = False
        self.quit()
        self.wait(3000)

    # ── Wake word detection ───────────────────────────────────────────────
    @staticmethod
    def _lev(a, b):
        if len(a) < len(b): a, b = b, a
        if not b: return len(a)
        prev = list(range(len(b)+1))
        for i, ca in enumerate(a):
            curr = [i+1]
            for j, cb in enumerate(b):
                curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(0 if ca==cb else 1)))
            prev = curr
        return prev[-1]

    @classmethod
    def _has_wake_word(cls, text: str) -> bool:
        t = text.lower().strip()
        for ww in WAKE_WORDS:
            if ww in t:
                return True
        first = t.split()[0] if t.split() else ""
        for ww in ("jarvis", "javis", "jarwis"):
            if cls._lev(first, ww) <= 2:
                return True
        return False

    @staticmethod
    def _strip_wake(text: str) -> str:
        t = text.lower()
        for ww in sorted(WAKE_WORDS, key=len, reverse=True):
            t = t.replace(ww, "").strip()
        return t.lstrip(",. !").strip()

    # ── Level estimator ───────────────────────────────────────────────────
    @staticmethod
    def _estimate_level(audio_data: bytes) -> int:
        try:
            samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            return max(10, min(100, int(np.sqrt(np.mean(samples**2)) / 200)))
        except Exception:
            return random.randint(40, 80)

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        if not SR_OK:
            self.log_msg.emit("[VOICE] speech_recognition not installed.")
            return

        rec = sr.Recognizer()
        rec.energy_threshold                = 300
        rec.dynamic_energy_threshold        = True
        rec.dynamic_energy_adjustment_damping = 0.15
        rec.dynamic_energy_ratio            = 1.5
        rec.pause_threshold                 = 0.8
        rec.non_speaking_duration           = 0.5

        mic         = None
        retry_count = 0

        while self._running:
            with self._lock:
                if self._paused:
                    self.msleep(100)
                    continue

            # Initialise mic
            if mic is None:
                try:
                    mic = sr.Microphone(
                        device_index=self._mic_device_idx,
                        sample_rate=16000
                    )
                    with mic as src:
                        self.state_changed.emit("calibrating")
                        rec.adjust_for_ambient_noise(src, duration=1.5)
                    self.state_changed.emit("idle")
                    retry_count = 0
                    self.log_msg.emit(
                        f"[VOICE] Mic ready. Threshold={rec.energy_threshold:.0f}"
                    )
                except Exception as e:
                    retry_count += 1
                    self.log_msg.emit(f"[MIC ERR #{retry_count}] {e}")
                    self.state_changed.emit("idle")
                    self.msleep(min(retry_count * 2000, 15000))
                    mic = None
                    continue

            try:
                self.state_changed.emit("listening")
                with mic as src:
                    audio = rec.listen(src, timeout=5, phrase_time_limit=20)

                self.state_changed.emit("processing")
                lvl = self._estimate_level(audio.get_raw_data())
                self.level_changed.emit(lvl)

                text = ""
                for lang in ("en-US", "en-GB", "ur-PK"):
                    try:
                        text = rec.recognize_google(
                            audio, language=lang, show_all=False
                        )
                        if text:
                            break
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError:
                        break

                if not text:
                    self.state_changed.emit("idle")
                    continue

                self.log_msg.emit(f'[STT] "{text}"')

                if self._wake_word_mode:
                    if self._has_wake_word(text):
                        SoundFX.wake()
                        clean = self._strip_wake(text)
                        self.text_received.emit(clean if clean else "_wake_")
                    else:
                        self.state_changed.emit("idle")
                else:
                    clean = self._strip_wake(text)
                    if clean:
                        self.text_received.emit(clean)
                    self.state_changed.emit("idle")

            except sr.WaitTimeoutError:
                self.state_changed.emit("idle")
            except sr.UnknownValueError:
                self.state_changed.emit("idle")
            except sr.RequestError as e:
                self.log_msg.emit(f"[STT NET] {e}")
                self.state_changed.emit("idle")
                self.msleep(3000)
            except OSError as e:
                self.log_msg.emit(f"[MIC OS] {e}")
                mic = None
                self.state_changed.emit("idle")
                self.msleep(5000)
            except Exception as e:
                self.log_msg.emit(f"[VOICE ERR] {e}")
                self.msleep(1000)