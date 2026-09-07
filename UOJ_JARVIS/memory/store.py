"""
memory/store.py  —  Persistent notes and key-value memory.
"""

import json
import datetime
from core.config import NOTES_FILE, MEM_FILE


class MemoryStore:
    """Thread-safe notes and free-form key=value memory."""

    def __init__(self):
        self.notes  = self._load(NOTES_FILE, [])
        self.memory = self._load(MEM_FILE,   {})

    # ── I/O ──────────────────────────────────────────────────────────────
    @staticmethod
    def _load(path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    @staticmethod
    def _save(path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MEM SAVE] {e}")

    # ── Notes ─────────────────────────────────────────────────────────────
    def add_note(self, text: str) -> str:
        if not text.strip():
            return "Nothing to save, sir."
        entry = {"ts": datetime.datetime.now().isoformat(), "text": text.strip()}
        self.notes.append(entry)
        self._save(NOTES_FILE, self.notes)
        return "Note saved, sir."

    def get_notes(self) -> str:
        if not self.notes:
            return "No notes yet, sir."
        recent = self.notes[-15:]
        lines  = [f"{i+1}. [{n['ts'][:16]}] {n['text']}"
                  for i, n in enumerate(recent)]
        return "Your recent notes:\n" + "\n".join(lines)

    def delete_note(self, idx=None) -> str:
        if idx is None:
            self.notes = []
            self._save(NOTES_FILE, self.notes)
            return "All notes deleted, sir."
        try:
            self.notes.pop(int(idx) - 1)
            self._save(NOTES_FILE, self.notes)
            return f"Note {idx} deleted, sir."
        except (IndexError, ValueError):
            return "Could not delete that note, sir."

    # ── Key-value memory ──────────────────────────────────────────────────
    def remember(self, key: str, value: str) -> None:
        self.memory[key.lower()] = value
        self._save(MEM_FILE, self.memory)

    def recall(self, key: str) -> str:
        v = self.memory.get(key.lower())
        return (f"I remember: {key} is {v}, sir."
                if v else f"Nothing stored for '{key}', sir.")

    def forget(self, key: str) -> str:
        if key.lower() in self.memory:
            del self.memory[key.lower()]
            self._save(MEM_FILE, self.memory)
            return f"Forgotten: {key}, sir."
        return f"No memory for '{key}', sir."

    def all_memory(self) -> str:
        if not self.memory:
            return "Memory bank is empty, sir."
        entries = list(self.memory.items())[-10:]
        return "Stored: " + "; ".join(f"{k} = {v}" for k, v in entries)