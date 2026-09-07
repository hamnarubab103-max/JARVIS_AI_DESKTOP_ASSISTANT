"""
core/ai_workers.py  —  QThread workers for AI chat and image generation.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from core import config as cfg
from core.deps import OPENAI_OK, CLAUDE_OK, openai, anthropic


class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, query: str, history: list,
                 context: str = "", parent=None):
        super().__init__(parent)
        self.query   = query
        self.history = list(history)
        self.context = context

    def run(self):
        full = (
            f"[Context: {self.context}]\n{self.query}"
            if self.context else self.query
        )

        # ── OpenAI GPT ────────────────────────────────────────────────────
        if OPENAI_OK and cfg.OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=cfg.OPENAI_API_KEY)
                msgs   = (
                    [{"role": "system", "content": cfg.JARVIS_SYSTEM}]
                    + self.history[-20:]
                    + [{"role": "user", "content": full}]
                )
                resp = client.chat.completions.create(
                    model=cfg.GPT_MODEL,
                    messages=msgs,
                    max_tokens=700,
                    temperature=0.76,
                )
                self.response_ready.emit(
                    resp.choices[0].message.content.strip()
                )
                return
            except Exception as e:
                print(f"[GPT] {e}")

        # ── Claude ────────────────────────────────────────────────────────
        if CLAUDE_OK and cfg.ANTHROPIC_API_KEY:
            try:
                client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY)
                msgs   = (
                    self.history[-14:]
                    + [{"role": "user", "content": full}]
                )
                msg = client.messages.create(
                    model=cfg.CLAUDE_MODEL,
                    max_tokens=700,
                    system=cfg.JARVIS_SYSTEM,
                    messages=msgs,
                )
                self.response_ready.emit(msg.content[0].text.strip())
                return
            except Exception as e:
                print(f"[CLAUDE] {e}")

        self.error_occurred.emit(
            "No AI engine configured, sir. Please set your API key in Settings."
        )


class ImageGenWorker(QThread):
    done = pyqtSignal(str, str)   # prompt, url
    fail = pyqtSignal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        if not (OPENAI_OK and cfg.OPENAI_API_KEY):
            self.fail.emit("OpenAI API key required for image generation, sir.")
            return
        try:
            client = openai.OpenAI(api_key=cfg.OPENAI_API_KEY)
            resp   = client.images.generate(
                model="dall-e-3",
                prompt=self.prompt,
                n=1,
                size="1024x1024",
                quality="standard",
            )
            self.done.emit(self.prompt, resp.data[0].url)
        except Exception as e:
            self.fail.emit(f"Image generation failed: {e}")