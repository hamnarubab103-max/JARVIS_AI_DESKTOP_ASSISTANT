"""
voice/speaker.py  —  Text-to-speech worker.
Tries OpenAI TTS first, falls back to pyttsx3.
"""

import re
import io
import threading

from PyQt5.QtCore import QThread, pyqtSignal
from core import config as cfg
from core.deps import (
    TTS_PYTTS, OPENAI_OK, PYGAME_OK,
    openai, pygame
)


class RoboticVoiceProcessor:
    """Pre-process text to sound better in TTS."""

    @staticmethod
    def apply_pyttsx3(engine):
        try:
            voices = engine.getProperty("voices") or []
            for v in voices:
                name = (v.name or "").lower()
                if any(k in name for k in ("david", "mark", "zira", "hazel")):
                    engine.setProperty("voice", v.id)
                    break
            engine.setProperty("rate",   145)
            engine.setProperty("volume", 1.0)
        except Exception:
            pass

    @staticmethod
    def process(text: str) -> str:
        text = re.sub(r"\. ",  ".  ",  text)
        text = re.sub(r", ",   ",  ",  text)
        text = text.replace("J.A.R.V.I.S", "J A R V I S")
        return text


class TTSWorker(QThread):
    finished = pyqtSignal()
    log_msg  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue   = []
        self._lock    = threading.Lock()
        self._running = True
        self._py_eng  = None

    # ── External API ─────────────────────────────────────────────────────
    def speak(self, text: str):
        clean = re.sub(r"[*_`#>~|•\-]+", " ", str(text))
        clean = re.sub(r"\s+", " ", clean).strip()
        clean = RoboticVoiceProcessor.process(clean)
        if clean:
            with self._lock:
                self._queue.append(clean)

    def stop(self):
        self._running = False
        if PYGAME_OK:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.quit()
        self.wait(3000)

    def clear_queue(self):
        with self._lock:
            self._queue.clear()
        if PYGAME_OK:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    # ── pyttsx3 init ──────────────────────────────────────────────────────
    def _init_py(self):
        if not TTS_PYTTS:
            return
        try:
            import pyttsx3
            self._py_eng = pyttsx3.init()
            RoboticVoiceProcessor.apply_pyttsx3(self._py_eng)
        except Exception as e:
            self.log_msg.emit(f"[TTS INIT] {e}")
            self._py_eng = None

    # ── OpenAI TTS ────────────────────────────────────────────────────────
    def _speak_openai(self, text: str) -> bool:
        if not (OPENAI_OK and cfg.OPENAI_API_KEY and PYGAME_OK):
            return False
        try:
            client = openai.OpenAI(api_key=cfg.OPENAI_API_KEY)
            resp   = client.audio.speech.create(
                model=cfg.TTS_MODEL,
                voice=cfg.TTS_VOICE,
                input=text,
                response_format="mp3",
                speed=0.88,
            )
            audio_io = io.BytesIO(resp.content)
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_io, "mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                self.msleep(40)
                if not self._running:
                    pygame.mixer.music.stop()
                    break
            return True
        except Exception as e:
            self.log_msg.emit(f"[OPENAI TTS] {e}")
            return False

    # ── pyttsx3 speak ─────────────────────────────────────────────────────
    def _speak_py(self, text: str):
        if not self._py_eng:
            self._init_py()
        if not self._py_eng:
            return
        try:
            self._py_eng.say(text)
            self._py_eng.runAndWait()
        except Exception as e:
            self.log_msg.emit(f"[PYTTS] {e}")
            self._py_eng = None

    # ── Thread loop ───────────────────────────────────────────────────────
    def run(self):
        if not (OPENAI_OK and cfg.OPENAI_API_KEY and PYGAME_OK):
            self._init_py()
        while self._running:
            text = None
            with self._lock:
                if self._queue:
                    text = self._queue.pop(0)
            if text:
                if not self._speak_openai(text):
                    self._speak_py(text)
                self.finished.emit()
            else:
                self.msleep(40)