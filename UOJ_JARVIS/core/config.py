"""
core/config.py  —  All constants, colour palette, API keys, and global flags.
"""

import os

# ─── Version ──────────────────────────────────────────────────────────────
VERSION     = "10.0"
APP_TITLE   = f"J.A.R.V.I.S  v{VERSION}  —  Ultra Pro AI Desktop Assistant  |  FYP"
DEVELOPERS  = "Amina Sikandar  |  Hamna Rubab  |  Eesha Jewan"

# ─── Storage paths ────────────────────────────────────────────────────────
DATA_DIR    = os.path.join(os.path.expanduser("~"), ".jarvis_data")
NOTES_FILE  = os.path.join(DATA_DIR, "notes.json")
MEM_FILE    = os.path.join(DATA_DIR, "memory.json")
ALARMS_FILE = os.path.join(DATA_DIR, "alarms.json")
FILES_DIR   = os.path.join(DATA_DIR, "files")
CHAT_LOG    = os.path.join(DATA_DIR, "chat_log.json")

for _d in (DATA_DIR, FILES_DIR):
    os.makedirs(_d, exist_ok=True)

# ─── Assets ───────────────────────────────────────────────────────────────
_here       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR  = os.path.join(_here, "assets", "images")
BG_IMAGE    = os.path.join(ASSETS_DIR, "background.jpg")

# ─── API Keys (env-first, then empty) ─────────────────────────────────────
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY",    "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GMAIL_USER        = os.environ.get("GMAIL_USER",  "")
GMAIL_PASS        = os.environ.get("GMAIL_PASS",  "")

# ─── AI Model names ───────────────────────────────────────────────────────
GPT_MODEL    = "gpt-4o"
CLAUDE_MODEL = "claude-sonnet-4-20250514"
TTS_MODEL    = "tts-1"
TTS_VOICE    = "onyx"         # mutable at runtime via settings

# ─── Iron Man HUD Colour Palette ──────────────────────────────────────────
BG_DEEP    = "#030810"
BG_PANEL   = "rgba(3,10,28,220)"
BG_CARD    = "rgba(5,14,38,180)"
CYAN       = "#00d4ff"
CYAN_DIM   = "#006688"
CYAN_GLOW  = "#00f0ff"
GREEN      = "#00ff9d"
AMBER      = "#ffb700"
RED_HUD    = "#ff2244"
PURPLE     = "#7b4fff"
ORANGE     = "#ff6600"
BORDER     = "rgba(0,200,255,35)"
BORDER_HI  = "rgba(0,240,255,100)"
GOLD       = "#ffd700"
TEAL_GLOW  = "#00ffcc"

# ─── Wake words ───────────────────────────────────────────────────────────
WAKE_WORDS = [
    "jarvis", "javis", "jarwis", "jarviz", "jarves", "jarbs", "j.a.r.v.i.s",
    "جارویس", "jaarvis", "jar vis", "jar-vis", "garvis", "harvis",
    "hey jarvis", "ok jarvis", "yo jarvis", "jarvis please", "please jarvis",
]

# ─── JARVIS system prompt ─────────────────────────────────────────────────
JARVIS_SYSTEM = """\
You are J.A.R.V.I.S (Just A Rather Very Intelligent System),
a hyper-intelligent AI desktop assistant — Final Year Project.
Developed by Amina Sikandar, Hamna Rubab, and Eesha Jewan.

ABSOLUTE RULES:
1. ALWAYS answer every question fully. Never refuse.
2. LANGUAGE: Urdu/Roman-Urdu input → Roman Urdu reply. English input → English reply.
3. Address the user as "sir".
4. Be CONCISE: 2-3 sentences unless asked for detail.
5. Voice-friendly output: NO markdown, NO bullet symbols, NO asterisks, NO special chars.
   Write flowing spoken sentences only.
6. Dry wit and genuine personality — never robotic.
7. Code questions: complete, working, copy-paste-ready code only.
8. Factual questions: direct, accurate, confident.
You are omniscient: history, science, tech, culture, maths, programming,
Urdu poetry, Pakistani culture, current events, philosophy, and beyond."""