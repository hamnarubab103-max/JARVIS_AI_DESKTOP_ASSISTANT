"""
nlp/parser.py  —  Robust intent & entity extraction.

Fixes the core bug: previously the fallback chain was too eager,
so "what is brain" hit the weather handler.  This module uses
strict priority ordering + explicit negative guards.
"""

import re
import datetime
from typing import Optional, Tuple, Dict, Any

# ─── Intent tag constants ──────────────────────────────────────────────────
class Intent:
    # Meta / control
    STOP_TTS        = "stop_tts"
    WAKE_ONLY       = "wake_only"
    TOGGLE_ALWAYS_ON= "toggle_always_on"
    CALIBRATE_MIC   = "calibrate_mic"
    TOGGLE_VOICE    = "toggle_voice"
    HELP            = "help"
    EXIT            = "exit"

    # Greeting / social
    GREETING        = "greeting"
    THANKS          = "thanks"
    HOW_ARE_YOU     = "how_are_you"
    WHO_AM_I        = "who_am_i"
    WHO_MADE_YOU    = "who_made_you"
    JOKE            = "joke"
    MOTIVATE        = "motivate"
    IDEA            = "idea"

    # Time / date
    TIME            = "time"
    DATE            = "date"
    YEAR            = "year"

    # Math / conversion
    MATH            = "math"
    SQRT            = "sqrt"
    CONVERT         = "convert"

    # System info
    SYS_INFO        = "sys_info"
    SYS_INFO_FULL   = "sys_info_full"
    BATTERY         = "battery"
    UPTIME          = "uptime"
    DISK            = "disk"
    IP_ADDRESS      = "ip_address"
    NETWORK_INFO    = "network_info"
    PROCESSES       = "processes"
    PING            = "ping"

    # Power
    SHUTDOWN        = "shutdown"
    RESTART         = "restart"
    LOCK            = "lock"
    SCREENSHOT      = "screenshot"
    CLIPBOARD_SHOW  = "clipboard_show"
    CLIPBOARD_COPY  = "clipboard_copy"

    # Files
    FILE_CREATE     = "file_create"
    FILE_READ       = "file_read"
    FILE_DELETE     = "file_delete"
    FILE_LIST       = "file_list"
    OPEN_EDITOR     = "open_editor"
    OPEN_FILES_DIALOG = "open_files_dialog"
    OPEN_FOLDER     = "open_folder"
    CLOSE_APP       = "close_app"

    # Notes / memory
    NOTE_ADD        = "note_add"
    NOTE_SHOW       = "note_show"
    NOTE_DELETE     = "note_delete"
    MEM_STORE       = "mem_store"
    MEM_RECALL      = "mem_recall"
    MEM_SHOW        = "mem_show"
    MEM_FORGET      = "mem_forget"

    # Alarms / reminders
    ALARM_SET       = "alarm_set"
    ALARM_LIST      = "alarm_list"
    ALARM_DELETE    = "alarm_delete"
    REMINDER_SET    = "reminder_set"
    REMINDER_LIST   = "reminder_list"

    # Media
    MEDIA_PLAY_FILE    = "media_play_file"
    MEDIA_PLAY_FOLDER  = "media_play_folder"
    YOUTUBE_PLAY       = "youtube_play"
    MEDIA_PAUSE        = "media_pause"
    MEDIA_RESUME       = "media_resume"
    MEDIA_STOP         = "media_stop"
    MEDIA_NEXT         = "media_next"
    MEDIA_PREV         = "media_prev"
    VOLUME_UP          = "volume_up"
    VOLUME_DOWN        = "volume_down"
    VOLUME_SET         = "volume_set"

    # Email
    EMAIL_SEND      = "email_send"
    EMAIL_OPEN      = "email_open"

    # Apps / websites
    APP_OPEN        = "app_open"
    SITE_OPEN       = "site_open"

    # Web services
    WEB_SEARCH      = "web_search"
    WEATHER         = "weather"
    NEWS            = "news"

    # Image gen
    IMAGE_GEN       = "image_gen"

    # Factual / AI fallback
    FACTUAL         = "factual"
    AI_QUERY        = "ai_query"


# ─── App map ──────────────────────────────────────────────────────────────
WIN_APPS: Dict[str, str] = {
    "notepad":                "notepad.exe",
    "calculator":             "calc.exe",
    "paint":                  "mspaint.exe",
    "ms paint":               "mspaint.exe",
    "cmd":                    "cmd.exe",
    "command prompt":         "cmd.exe",
    "terminal":               "cmd.exe",
    "powershell":             "powershell.exe",
    "task manager":           "taskmgr.exe",
    "file explorer":          "explorer.exe",
    "explorer":               "explorer.exe",
    "control panel":          "control.exe",
    "snipping tool":          "SnippingTool.exe",
    "snip":                   "SnippingTool.exe",
    "magnifier":              "magnify.exe",
    "on screen keyboard":     "osk.exe",
    "sticky notes":           "StickyNotes.exe",
    "registry editor":        "regedit.exe",
    "device manager":         "devmgmt.msc",
    "disk management":        "diskmgmt.msc",
    "event viewer":           "eventvwr.msc",
    "services":               "services.msc",
    "msconfig":               "msconfig.exe",
    "word":                   "winword.exe",
    "microsoft word":         "winword.exe",
    "excel":                  "excel.exe",
    "microsoft excel":        "excel.exe",
    "powerpoint":             "powerpnt.exe",
    "vs code":                "code",
    "visual studio code":     "code",
    "vscode":                 "code",
    "visual studio":          "devenv.exe",
    "pycharm":                "pycharm64.exe",
    "vlc":                    "vlc.exe",
    "chrome":                 "chrome.exe",
    "google chrome":          "chrome.exe",
    "firefox":                "firefox.exe",
    "edge":                   "msedge.exe",
    "microsoft edge":         "msedge.exe",
    "brave":                  "brave.exe",
    "spotify":                "spotify.exe",
    "discord":                "discord.exe",
    "zoom":                   "zoom.exe",
    "obs":                    "obs64.exe",
    "obs studio":             "obs64.exe",
    "steam":                  "steam.exe",
    "gimp":                   "gimp-2.10.exe",
    "photoshop":              "photoshop.exe",
    "audacity":               "audacity.exe",
    "postman":                "postman.exe",
    "telegram":               "telegram.exe",
    "whatsapp":               "whatsapp.exe",
    "slack":                  "slack.exe",
    "notion":                 "notion.exe",
    "figma":                  "figma.exe",
    "blender":                "blender.exe",
}

SITES: Dict[str, str] = {
    "youtube":          "https://youtube.com",
    "google":           "https://google.com",
    "facebook":         "https://facebook.com",
    "instagram":        "https://instagram.com",
    "twitter":          "https://twitter.com",
    "github":           "https://github.com",
    "gmail":            "https://mail.google.com",
    "whatsapp web":     "https://web.whatsapp.com",
    "netflix":          "https://netflix.com",
    "amazon":           "https://amazon.com",
    "linkedin":         "https://linkedin.com",
    "reddit":           "https://reddit.com",
    "wikipedia":        "https://wikipedia.org",
    "stackoverflow":    "https://stackoverflow.com",
    "stack overflow":   "https://stackoverflow.com",
    "chatgpt":          "https://chat.openai.com",
    "chat gpt":         "https://chat.openai.com",
    "openai":           "https://openai.com",
    "claude":           "https://claude.ai",
    "anthropic":        "https://anthropic.com",
    "spotify":          "https://open.spotify.com",
    "twitch":           "https://twitch.tv",
    "discord":          "https://discord.com",
    "outlook":          "https://outlook.com",
    "google maps":      "https://maps.google.com",
    "maps":             "https://maps.google.com",
    "translate":        "https://translate.google.com",
    "google translate": "https://translate.google.com",
    "canva":            "https://canva.com",
    "daraz":            "https://daraz.pk",
    "geo news":         "https://geo.tv",
    "ary news":         "https://arynews.tv",
    "dawn":             "https://dawn.com",
    "bbc":              "https://bbc.com",
    "cnn":              "https://cnn.com",
    "google drive":     "https://drive.google.com",
    "google docs":      "https://docs.google.com",
    "kaggle":           "https://kaggle.com",
    "hugging face":     "https://huggingface.co",
    "tiktok":           "https://tiktok.com",
    "coursera":         "https://coursera.org",
    "udemy":            "https://udemy.com",
    "khan academy":     "https://khanacademy.org",
    "w3schools":        "https://w3schools.com",
    "wolframalpha":     "https://wolframalpha.com",
    "google news":      "https://news.google.com",
}

FOLDERS = ("documents", "downloads", "desktop", "pictures", "music", "videos")


# ─── Parser ───────────────────────────────────────────────────────────────
class CommandParser:
    """
    Converts raw text → (intent, entities_dict).

    Priority order (highest first):
      1. Meta / TTS control
      2. Explicit system commands (shutdown, lock, …)
      3. Date / time  ← must come BEFORE factual so "what time" doesn't go to AI
      4. Notes / memory
      5. Alarms / reminders
      6. Media
      7. Email
      8. Files
      9. Math / conversion
      10. System info  ← explicit keywords only
      11. Social / greeting
      12. App / site open
      13. Web search
      14. Weather  ← only if explicit weather keyword
      15. News     ← only if explicit news keyword
      16. Image generation
      17. Factual query (what is X / who is X)  ← before generic AI
      18. AI fallback
    """

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _strip_wake(text: str) -> str:
        from core.config import WAKE_WORDS
        t = text.lower()
        for ww in sorted(WAKE_WORDS, key=len, reverse=True):
            t = t.replace(ww, "").strip()
        return t.lstrip(",. !").strip()

    @staticmethod
    def _lev(a: str, b: str) -> int:
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
    def has_wake_word(cls, text: str) -> bool:
        from core.config import WAKE_WORDS
        t = text.lower().strip()
        for ww in WAKE_WORDS:
            if ww in t:
                return True
        first = t.split()[0] if t.split() else ""
        for ww in ("jarvis", "javis", "jarwis"):
            if cls._lev(first, ww) <= 2:
                return True
        return False

    # ── main entry ────────────────────────────────────────────────────────
    @classmethod
    def parse(cls, raw: str) -> Tuple[str, Dict[str, Any]]:
        """
        Returns (intent, entities).
        Entities keys depend on intent — see individual handlers.
        """
        cmd   = raw.strip().lower()
        clean = cls._strip_wake(cmd)       # cmd without wake word prefix

        # 1. Meta / TTS
        if cmd == "_wake_":
            return Intent.WAKE_ONLY, {}

        if any(p in cmd for p in ("stop speaking", "be quiet", "shut up",
                                   "stop talking", "silence", "band karo",
                                   "chup", "khamosh")):
            return Intent.STOP_TTS, {}

        if any(p in cmd for p in ("toggle always on", "always on mode",
                                   "enable always on", "disable always on")):
            return Intent.TOGGLE_ALWAYS_ON, {}

        if any(p in cmd for p in ("recalibrate", "calibrate mic",
                                   "calibrate microphone", "reset microphone",
                                   "fix microphone")):
            return Intent.CALIBRATE_MIC, {}

        if any(p in cmd for p in ("toggle voice", "mute voice", "unmute voice",
                                   "turn off voice", "turn on voice",
                                   "voice off", "voice on")):
            return Intent.TOGGLE_VOICE, {}

        # 2. Exit
        if any(p in cmd for p in ("goodbye", "bye", "shut down jarvis",
                                   "khuda hafiz", "allah hafiz", "alvida",
                                   "exit jarvis", "quit jarvis", "band karo jarvis")):
            return Intent.EXIT, {}

        # 3. Help
        if any(p in cmd for p in ("help", "what can you do", "capabilities",
                                   "features", "commands", "meri madad karo")):
            return Intent.HELP, {}

        # 4. Power commands  (before "open" to avoid confusion)
        if any(p in cmd for p in ("shutdown", "shut down computer",
                                   "power off", "turn off computer")):
            return Intent.SHUTDOWN, {}

        if any(p in cmd for p in ("restart computer", "reboot", "restart system")):
            return Intent.RESTART, {}

        if any(p in cmd for p in ("lock computer", "lock pc",
                                   "lock screen", "lock workstation")):
            return Intent.LOCK, {}

        # 5. Screenshot / clipboard
        if any(p in cmd for p in ("screenshot", "capture screen",
                                   "take screenshot", "screen shot")):
            return Intent.SCREENSHOT, {}

        if re.match(r"^copy (.+)", cmd):
            text = raw[5:].strip()
            return Intent.CLIPBOARD_COPY, {"text": text}

        if any(p in cmd for p in ("show clipboard", "clipboard content", "clipboard")):
            return Intent.CLIPBOARD_SHOW, {}

        # 6. Date / time  ← STRICT: only if the sentence is primarily asking for time/date
        if any(p in cmd for p in ("what time", "current time", "time is it",
                                   "waqt kya", "tell me the time", "time batao",
                                   "clock", "kitne baje")):
            return Intent.TIME, {}

        if any(p in cmd for p in ("what date", "today date", "current date",
                                   "aaj ki tarikh", "what day is it", "date today",
                                   "day today", "din kya")):
            return Intent.DATE, {}

        if any(p in cmd for p in ("what year", "current year", "konsa saal", "year kya")):
            return Intent.YEAR, {}

        # 7. Ping / internet
        if any(p in cmd for p in ("ping", "check internet", "am i online",
                                   "network check", "internet check",
                                   "internet connection")):
            return Intent.PING, {}

        # 8. Email
        email_m = re.search(
            r"send\s+(?:an?\s+)?email\s+to\s+([\w.\-@]+)\s+"
            r"(?:with\s+)?subject\s+(.+?)\s+(?:and\s+)?(?:body|message|saying)\s+(.+)",
            raw, re.IGNORECASE)
        if email_m:
            return Intent.EMAIL_SEND, {
                "to":      email_m.group(1).strip(),
                "subject": email_m.group(2).strip(),
                "body":    email_m.group(3).strip(),
            }
        if any(p in cmd for p in ("open email", "compose email",
                                   "send email", "write email")):
            if any(p in cmd for p in ("open gmail", "go to gmail")):
                return Intent.SITE_OPEN, {"name": "gmail", "url": SITES["gmail"]}
            return Intent.EMAIL_OPEN, {}

        # 9. Notes
        if any(p in cmd for p in ("write note", "save note", "add note",
                                   "note karo", "take note", "note down",
                                   "make note", "create note")):
            content = re.sub(
                r"(write note|save note|add note|note karo|take note|"
                r"note down|make note|create note)", "", raw, flags=re.IGNORECASE
            ).strip()
            return Intent.NOTE_ADD, {"content": content}

        if any(p in cmd for p in ("show notes", "read notes", "list notes",
                                   "my notes", "all notes")):
            return Intent.NOTE_SHOW, {}

        m_del = re.search(r"delete note\s*(\d+)", cmd)
        if m_del:
            return Intent.NOTE_DELETE, {"idx": m_del.group(1)}
        if any(p in cmd for p in ("delete all notes", "clear notes", "clear all notes")):
            return Intent.NOTE_DELETE, {"idx": None}

        # 10. Memory
        mem_m = re.search(r"(remember|store)\s+(.+?)\s+(is|=|hai)\s+(.+)", cmd)
        if mem_m:
            return Intent.MEM_STORE, {
                "key":   mem_m.group(2).strip(),
                "value": mem_m.group(4).strip(),
            }
        recall_m = re.search(r"recall\s+(.+)", cmd)
        if recall_m:
            return Intent.MEM_RECALL, {"key": recall_m.group(1).strip()}
        if any(p in cmd for p in ("what do you remember", "show memory",
                                   "all memory", "my memory")):
            return Intent.MEM_SHOW, {}
        forget_m = re.search(r"forget\s+(.+)", cmd)
        if forget_m:
            return Intent.MEM_FORGET, {"key": forget_m.group(1).strip()}

        # 11. Alarms / reminders
        if any(p in cmd for p in ("set alarm", "alarm lagao", "alarm at",
                                   "alarm for", "create alarm", "new alarm")):
            return Intent.ALARM_SET, {"raw": raw, "cmd": cmd}
        if any(p in cmd for p in ("list alarms", "show alarms", "my alarms")):
            return Intent.ALARM_LIST, {}
        if any(p in cmd for p in ("delete alarm", "remove alarm",
                                   "clear alarms", "cancel alarm")):
            idx_m = re.search(r"\d+", cmd)
            return Intent.ALARM_DELETE, {"idx": int(idx_m.group()) if idx_m else None}

        if any(p in cmd for p in ("remind me", "set reminder",
                                   "yaad dilao", "reminder lagao")):
            return Intent.REMINDER_SET, {"raw": raw, "cmd": cmd}
        if any(p in cmd for p in ("list reminders", "show reminders",
                                   "my reminders")):
            return Intent.REMINDER_LIST, {}

        # 12. Media
        pf = re.search(
            r"play\s+(?:file\s+)?(.+\.(mp3|mp4|wav|ogg|flac|avi|mkv|m4a|aac|wma))",
            cmd, re.IGNORECASE)
        if pf:
            return Intent.MEDIA_PLAY_FILE, {"filename": pf.group(1).strip()}

        if re.search(r"play\s+(.+)\s+on\s+youtube", cmd):
            q = re.sub(r"play|on youtube", "", cmd).strip()
            return Intent.YOUTUBE_PLAY, {"query": q}

        if re.search(r"play\s+(music|audio|songs?|gana|tracks?)", cmd):
            fm = re.search(r"from\s+(\w+)", cmd)
            return Intent.MEDIA_PLAY_FOLDER, {
                "folder": fm.group(1) if fm else "music"
            }

        if any(p in cmd for p in ("pause music", "pause video",
                                   "pause media", "pause playback")):
            return Intent.MEDIA_PAUSE, {}
        if any(p in cmd for p in ("resume music", "resume media",
                                   "unpause", "continue playing")):
            return Intent.MEDIA_RESUME, {}
        if any(p in cmd for p in ("stop music", "stop video", "stop media")):
            return Intent.MEDIA_STOP, {}
        if any(p in cmd for p in ("next track", "next song", "skip song")):
            return Intent.MEDIA_NEXT, {}
        if any(p in cmd for p in ("previous track", "prev track",
                                   "previous song", "back song")):
            return Intent.MEDIA_PREV, {}
        if any(p in cmd for p in ("volume up", "louder",
                                   "increase volume", "aawaz barho")):
            return Intent.VOLUME_UP, {}
        if any(p in cmd for p in ("volume down", "quieter",
                                   "decrease volume", "aawaz kam")):
            return Intent.VOLUME_DOWN, {}
        vol_m = re.search(r"set volume\s+(?:to\s+)?(\d+)", cmd)
        if vol_m:
            return Intent.VOLUME_SET, {"level": int(vol_m.group(1))}

        # 13. Files
        wf = re.search(
            r"create\s+(?:a\s+)?(?:file|document)\s+(.+?)\s+with\s+content\s+(.+)",
            raw, re.IGNORECASE)
        if wf:
            return Intent.FILE_CREATE, {
                "filename": wf.group(1).strip(),
                "content":  wf.group(2).strip(),
            }
        rf = re.search(r"(?:read|show)\s+file\s+(.+)", raw, re.IGNORECASE)
        if rf:
            return Intent.FILE_READ, {"filename": rf.group(1).strip()}
        df2 = re.search(r"delete\s+file\s+(.+)", raw, re.IGNORECASE)
        if df2:
            return Intent.FILE_DELETE, {"filename": df2.group(1).strip()}
        lf = re.search(r"list\s+files?\s+(?:in\s+)?(.+)", raw, re.IGNORECASE)
        if lf:
            return Intent.FILE_LIST, {"folder": lf.group(1).strip()}

        if any(p in cmd for p in ("open editor", "text editor",
                                   "open text editor")):
            return Intent.OPEN_EDITOR, {}

        if any(p in cmd for p in ("open file manager", "file manager",
                                   "browse files")):
            return Intent.OPEN_FILES_DIALOG, {}

        for k in FOLDERS:
            if (f"open {k}" in cmd or f"go to {k}" in cmd
                    or f"{k} folder" in cmd):
                return Intent.OPEN_FOLDER, {"folder": k}

        # 14. Math  ← only if digit present
        if (any(p in cmd for p in ("calculate", "compute", "evaluate",
                                    "how much is", "kitna hai", "solve",
                                    "math"))
                and any(c.isdigit() for c in cmd)):
            return Intent.MATH, {"raw": raw, "cmd": cmd}

        if any(p in cmd for p in ("square root", "sqrt", "root of")):
            nums = re.findall(r"\d+\.?\d*", cmd)
            if nums:
                return Intent.SQRT, {"number": float(nums[0])}

        if any(p in cmd for p in ("convert", "to fahrenheit", "to celsius",
                                   "to miles", "to km", "to kg", "to lbs",
                                   "to meters", "to feet")):
            return Intent.CONVERT, {"raw": raw, "cmd": cmd}

        # 15. System info  ← STRICT keywords only
        if any(p in cmd for p in ("detailed system info", "full system info",
                                   "complete system info", "system statistics")):
            return Intent.SYS_INFO_FULL, {}

        if any(p in cmd for p in ("system info", "system status",
                                   "computer info", "hardware info",
                                   "pc info", "system details")):
            return Intent.SYS_INFO, {}

        if any(p in cmd for p in ("battery", "battery status", "charging status",
                                   "battery percentage", "battery level")):
            return Intent.BATTERY, {}

        if any(p in cmd for p in ("uptime", "system uptime", "how long running",
                                   "boot time")):
            return Intent.UPTIME, {}

        if any(p in cmd for p in ("disk space", "storage space",
                                   "free space", "hard drive space",
                                   "disk usage")):
            return Intent.DISK, {}

        if any(p in cmd for p in ("ip address", "my ip", "local ip",
                                   "ip batao", "what is my ip")):
            return Intent.IP_ADDRESS, {}

        if any(p in cmd for p in ("network info", "network details",
                                   "show network", "network interfaces")):
            return Intent.NETWORK_INFO, {}

        if any(p in cmd for p in ("list processes", "running processes",
                                   "process list", "top processes",
                                   "what is running")):
            return Intent.PROCESSES, {}

        # 16. Social / greeting
        if any(w in cmd for w in ("hello", "hi jarvis", "hey jarvis",
                                   "good morning", "good evening",
                                   "good afternoon", "good night",
                                   "salam", "aadab", "assalam")):
            return Intent.GREETING, {}

        if any(p in cmd for p in ("thank", "shukriya", "meherbani",
                                   "thanks", "thank you", "shukran")):
            return Intent.THANKS, {}

        if any(p in cmd for p in ("how are you", "kaise ho", "theek ho",
                                   "you ok", "how do you do",
                                   "are you okay")):
            return Intent.HOW_ARE_YOU, {}

        if any(p in cmd for p in ("what is your name", "your name",
                                   "who are you", "tum kaun ho",
                                   "introduce yourself", "apna naam batao")):
            return Intent.WHO_AM_I, {}

        if any(p in cmd for p in ("who made you", "who created you",
                                   "kisne banaya", "who built you",
                                   "developer", "creator")):
            return Intent.WHO_MADE_YOU, {}

        if any(p in cmd for p in ("joke", "funny", "mazaak", "lataifa",
                                   "tell me a joke", "make me laugh", "hasao")):
            return Intent.JOKE, {}

        if any(p in cmd for p in ("motivate", "inspire", "quote",
                                   "motivation", "himmat", "encourage", "boost me")):
            return Intent.MOTIVATE, {}

        if any(p in cmd for p in ("idea", "project idea", "suggest idea",
                                   "koi idea do")):
            return Intent.IDEA, {}

        # 17. Image generation
        if any(p in cmd for p in ("generate image", "create image", "dall-e",
                                   "draw a picture", "generate a picture",
                                   "make art", "image banao", "image generate")):
            prompt = re.sub(
                r"(generate image of?|create image of?|draw|dall-e|"
                r"generate a picture of?|make art of?|image banao|"
                r"image generate of?)", "", cmd
            ).strip() or raw
            return Intent.IMAGE_GEN, {"prompt": prompt}

        # 18. App open
        app_verb = re.match(r"^(open|launch|run|start)\s+(.+)$", cmd)
        if app_verb:
            name = app_verb.group(2).strip()
            if name in WIN_APPS:
                return Intent.APP_OPEN, {
                    "name": name, "exe": WIN_APPS[name]
                }

        # 19. Site open
        site_verb = re.match(
            r"^(open|go to|launch|browse|visit)\s+(.+)$", cmd)
        if site_verb:
            name = site_verb.group(2).strip()
            if name in SITES:
                return Intent.SITE_OPEN, {
                    "name": name, "url": SITES[name]
                }
            # fuzzy site match
            for sname, surl in SITES.items():
                if sname in cmd:
                    return Intent.SITE_OPEN, {"name": sname, "url": surl}

        # 20. Web search  ← must be BEFORE weather/news
        if any(p in cmd for p in ("search for", "google for", "look up",
                                   "find online", "dhundo", "talash karo",
                                   "search online", "google search",
                                   "search google", "google it")):
            q = re.sub(
                r"(search for|google for|look up|find online|dhundo|talash karo|"
                r"search online|google search|search google|google it)", "", cmd
            ).strip()
            return Intent.WEB_SEARCH, {"query": q}

        # 21. Weather  ← ONLY if word "weather" / "mausam" / "forecast" present
        #     NOT triggered by "what is X" without weather keyword
        WEATHER_KEYWORDS = ("weather", "mausam", "forecast", "temperature",
                             "humidity", "rainfall", "barish kitni",
                             "weather today", "weather in", "weather at",
                             "weather for", "aaj ka mausam")
        if any(p in cmd for p in WEATHER_KEYWORDS):
            city = re.sub(
                r"(weather|mausam|temperature|in|at|for|current|aaj|ka|"
                r"forecast|batao|today|rain|sunny|cloudy|how is|what is|the|"
                r"humidity|forecast)", "", cmd
            ).strip()
            if not city or len(city) < 2:
                city = "Karachi"
            return Intent.WEATHER, {"city": city}

        # 22. News  ← ONLY if "news" / "khabar" / "headlines" present
        NEWS_KEYWORDS = ("latest news", "breaking news", "news today",
                         "khabar", "headlines", "news pakistan",
                         "news update", "current news", "aaj ki khabar")
        if any(p in cmd for p in NEWS_KEYWORDS):
            topic = re.sub(
                r"(latest|news|khabar|headlines|today|breaking|pakistan|"
                r"update|current|aaj ki)", "", cmd
            ).strip()
            return Intent.NEWS, {"topic": topic}

        # 23. Close app
        close_m = re.search(r"^(?:close|kill|terminate)\s+(.+)$", cmd)
        if close_m:
            return Intent.CLOSE_APP, {"name": close_m.group(1).strip()}

        # 24. Factual query  ← "what is X", "who is X", etc.
        FACTUAL_RE = re.compile(
            r"^(what\s+is\s+|what\s+are\s+|who\s+is\s+|who\s+was\s+|"
            r"tell\s+me\s+about\s+|explain\s+|define\s+|what\s+does\s+|"
            r"how\s+does\s+|how\s+do\s+|describe\s+|"
            r"information\s+(?:on|about)\s+|history\s+of\s+|"
            r"biography\s+of\s+|kya\s+hai\s+|kon\s+hai\s+|"
            r"kon\s+tha\s+|batao\s+|ke\s+baare\s+mein\s+)",
            re.IGNORECASE,
        )
        factual_m = FACTUAL_RE.match(cmd)
        if factual_m:
            topic = cmd[factual_m.end():].strip()
            if topic and len(topic) > 1:
                return Intent.FACTUAL, {"topic": topic, "original": raw}

        # 25. Wikipedia trigger phrases
        for tr in ("tell me about", "explain", "information on",
                   "information about", "history of", "biography of",
                   "ke baare mein", "describe", "batao"):
            if tr in cmd:
                q = cmd[cmd.find(tr)+len(tr):].strip()
                if q and len(q) > 1:
                    return Intent.FACTUAL, {"topic": q, "original": raw}
                break

        # 26. AI fallback
        return Intent.AI_QUERY, {"query": raw}