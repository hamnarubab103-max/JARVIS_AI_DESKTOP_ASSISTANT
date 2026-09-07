"""
core/deps.py  —  Detect optional third-party packages at import time.
Import this module everywhere; never do bare try/except at module level.
"""

# ── Standard always-available ─────────────────────────────────────────────
import sys, os, re, math, html, json, random, socket, platform, time
import datetime, threading, subprocess, webbrowser, io, shutil, traceback
import glob, struct, wave, smtplib, email.mime.text, email.mime.multipart

# ── Required (will raise if missing) ──────────────────────────────────────
import psutil
import numpy as np

from PyQt5.QtWidgets  import *
from PyQt5.QtGui      import *
from PyQt5.QtCore     import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# ── Optional ──────────────────────────────────────────────────────────────
try:
    import pyttsx3
    TTS_PYTTS = True
except ImportError:
    TTS_PYTTS = False

try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    sr    = None
    SR_OK = False

try:
    import requests
    REQ_OK = True
except ImportError:
    requests = None
    REQ_OK   = False

try:
    import wikipedia
    WIKI_OK = True
except ImportError:
    wikipedia = None
    WIKI_OK   = False

try:
    import openai
    OPENAI_OK = True
except ImportError:
    openai    = None
    OPENAI_OK = False

try:
    import anthropic
    CLAUDE_OK = True
except ImportError:
    anthropic = None
    CLAUDE_OK = False

try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    PYGAME_OK = True
except Exception:
    pygame    = None
    PYGAME_OK = False


def ai_engine() -> str:
    """Return the active AI engine name based on installed packages + API keys."""
    from core.config import OPENAI_API_KEY, ANTHROPIC_API_KEY
    if OPENAI_OK and OPENAI_API_KEY:
        return "openai"
    if CLAUDE_OK and ANTHROPIC_API_KEY:
        return "claude"
    return "none"


def use_openai_tts() -> bool:
    from core.config import OPENAI_API_KEY
    return OPENAI_OK and bool(OPENAI_API_KEY) and PYGAME_OK