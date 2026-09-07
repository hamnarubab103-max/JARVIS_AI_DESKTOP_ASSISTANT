"""
J.A.R.V.I.S  v10.0  —  Ultra Pro Iron Man HUD Dashboard
Developed by: Amina Sikandar | Hamna Rubab | Eesha Jewan
International Expo Edition — 100% Complete & Error-Free
"""

import sys, os, re, math, html, json, random, socket, platform, time
import datetime, threading, subprocess, webbrowser, io, shutil, traceback
import glob, struct, wave, smtplib, email.mime.text, email.mime.multipart
import ctypes, winreg

import psutil
import numpy as np

from PyQt5.QtWidgets  import *
from PyQt5.QtGui      import *
from PyQt5.QtCore     import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# ─── Optional imports ─────────────────────────────────────────────────────
try:    import pyttsx3;           TTS_PYTTS = True
except: TTS_PYTTS = False

try:
    import speech_recognition as sr
    SR_OK = True
except: SR_OK = False

try:    import requests;          REQ_OK = True
except: REQ_OK = False

try:    import wikipedia;         WIKI_OK = True
except: WIKI_OK = False

try:
    import openai
    OPENAI_OK = True
except Exception as _e:
    OPENAI_OK = False
    print(f"[STARTUP] openai import failed: {_e}")  # <-- check your terminal for this

try:
    import anthropic
    CLAUDE_OK = True
except Exception as _e:
    CLAUDE_OK = False
    print(f"[STARTUP] anthropic import failed: {_e}")  # <-- check your terminal for this

try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    PYGAME_OK = True
except: PYGAME_OK = False

# ─── API Keys ──────────────────────────────────────────────────────────────
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", ".....")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "....")
GMAIL_USER        = os.environ.get("GMAIL_USER", "...")
GMAIL_PASS        = os.environ.get("GMAIL_PASS", "...")

GPT_MODEL    = "gpt-4o"
CLAUDE_MODEL = "claude-sonnet-4-20250514"
TTS_MODEL    = "tts-1"
TTS_VOICE    = "onyx"

AI_ENGINE = ("openai" if (OPENAI_OK and OPENAI_API_KEY) else
             "claude" if (CLAUDE_OK and ANTHROPIC_API_KEY) else "none")
USE_OPENAI_TTS = OPENAI_OK and bool(OPENAI_API_KEY) and PYGAME_OK

# ─── Storage ──────────────────────────────────────────────────────────────
DATA_DIR    = os.path.join(os.path.expanduser("~"), ".jarvis_data")
NOTES_FILE  = os.path.join(DATA_DIR, "notes.json")
MEM_FILE    = os.path.join(DATA_DIR, "memory.json")
ALARMS_FILE = os.path.join(DATA_DIR, "alarms.json")
FILES_DIR   = os.path.join(DATA_DIR, "files")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# ─── Assets path ──────────────────────────────────────────────────────────
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "images")
BG_IMAGE   = os.path.join(ASSETS_DIR, "background.jpg")

# ─── Professional HUD Color Palette (v11 — Expo Edition) ─────────────────
BG_DEEP    = "#070B12"
BG_PANEL   = "rgba(10,15,26,235)"
BG_CARD    = "rgba(14,21,36,190)"
CYAN       = "#22D3EE"
CYAN_DIM   = "#0E7490"
CYAN_GLOW  = "#67E8F9"
GREEN      = "#34D399"
AMBER      = "#FBBF24"
RED_HUD    = "#F87171"
PURPLE     = "#A78BFA"
ORANGE     = "#FB923C"
BORDER     = "rgba(34,211,238,30)"
BORDER_HI  = "rgba(103,232,249,95)"
GOLD       = "#FACC15"
TEAL_GLOW  = "#5EEAD4"

WAKE_WORDS = [
    "jarvis","javis","jarwis","jarviz","jarves","jarbs","j.a.r.v.i.s",
    "جارویس","jaarvis","jar vis","jar-vis","garvis","harvis",
    "hey jarvis","ok jarvis","yo jarvis","jarvis please","please jarvis"
]

JARVIS_SYSTEM = """You are J.A.R.V.I.S (Just A Rather Very Intelligent System),
a hyper-intelligent AI desktop assistant — Final Year Project.
Developed by Amina Sikandar, Hamna Rubab, and Eesha Jewan.

ABSOLUTE RULES:
1. ALWAYS answer every question. Never refuse.
2. LANGUAGE: Urdu/Roman-Urdu input → Roman Urdu reply. English → English.
3. Address the user as "sir".
4. Be CONCISE: 2-3 sentences unless asked for detail.
5. Voice-friendly: NO markdown, NO bullets, NO asterisks, NO special chars.
   Write flowing spoken sentences only.
6. Dry wit and genuine personality — never boring or robotic.
7. Code questions: complete, working, copy-paste-ready code only.
8. Factual questions: direct, accurate, confident.
You are omniscient: history, science, tech, culture, maths, programming,
Urdu poetry, Pakistani culture, current events, philosophy, and far beyond."""


# ══════════════════════════════════════════════════════════════════════════
#  ROBOTIC TTS VOICE PROCESSOR
# ══════════════════════════════════════════════════════════════════════════
class RoboticVoiceProcessor:
    @staticmethod
    def apply_robot_effect_pyttsx3(engine):
        try:
            voices = engine.getProperty('voices') or []
            for v in voices:
                name = (v.name or '').lower()
                if any(k in name for k in ('david','mark','zira','hazel')):
                    engine.setProperty('voice', v.id)
                    break
            engine.setProperty('rate', 145)
            engine.setProperty('volume', 1.0)
        except: pass

    @staticmethod
    def process_text_for_robot(text):
        text = re.sub(r'\. ', '.  ', text)
        text = re.sub(r', ', ',  ', text)
        text = text.replace('J.A.R.V.I.S', 'J A R V I S')
        return text


# ══════════════════════════════════════════════════════════════════════════
#  SOUND FX
# ══════════════════════════════════════════════════════════════════════════
class SoundFX:
    @staticmethod
    def _beep(freq=880, dur=0.08, vol=0.4, shape="sine"):
        if not PYGAME_OK: return
        try:
            sr2 = 44100; n = int(sr2 * dur)
            t = np.linspace(0, dur, n, endpoint=False)
            if shape == "square":
                w = np.sign(np.sin(2*np.pi*freq*t)).astype(np.float32)
            elif shape == "saw":
                w = (2*(t*freq - np.floor(t*freq+0.5))).astype(np.float32)
            elif shape == "robot":
                w = (0.6*np.sign(np.sin(2*np.pi*freq*t)) +
                     0.3*np.sign(np.sin(2*np.pi*freq*1.5*t)) +
                     0.1*np.sign(np.sin(2*np.pi*freq*2*t))).astype(np.float32)
            else:
                w = np.sin(2*np.pi*freq*t).astype(np.float32)
            attack = min(int(sr2*.003), n); release = min(int(n*.25), n)
            env = np.ones(n, dtype=np.float32)
            env[:attack]   = np.linspace(0, 1, attack)
            env[-release:] = np.linspace(1, 0, release)
            w = (w * env * vol * 32767).astype(np.int16)
            stereo = np.ascontiguousarray(np.column_stack((w, w)))
            pygame.sndarray.make_sound(stereo).play()
        except: pass

    @staticmethod
    def click():  SoundFX._beep(1400, .03, .2, "square")
    @staticmethod
    def alert():
        if not PYGAME_OK: return
        def _p():
            for f in [660,880,660,1100,880]: SoundFX._beep(f,.1,.5,"robot"); time.sleep(.12)
        threading.Thread(target=_p, daemon=True).start()
    @staticmethod
    def boot():
        if not PYGAME_OK: return
        def _p():
            seq = [(220,.08),(330,.06),(440,.06),(550,.06),(660,.08),
                   (880,.1),(1100,.1),(1320,.12),(1100,.1),(880,.18)]
            for f,d in seq: SoundFX._beep(f,d,.35,"robot"); time.sleep(d+.02)
        threading.Thread(target=_p, daemon=True).start()
    @staticmethod
    def thinking():
        if not PYGAME_OK: return
        def _p():
            for f in [440,520,480,560]: SoundFX._beep(f,.06,.15,"saw"); time.sleep(.08)
        threading.Thread(target=_p, daemon=True).start()
    @staticmethod
    def error():
        if not PYGAME_OK: return
        for f in [880,440,220]: SoundFX._beep(f,.12,.5,"square"); time.sleep(.14)
    @staticmethod
    def ack():
        if not PYGAME_OK: return
        def _p(): SoundFX._beep(1100,.04,.3,"robot"); time.sleep(.05); SoundFX._beep(1320,.06,.3,"robot")
        threading.Thread(target=_p, daemon=True).start()
    @staticmethod
    def alarm_beep():
        if not PYGAME_OK: return
        def _p():
            for _ in range(8): SoundFX._beep(1200,.12,.7,"robot"); time.sleep(.15)
        threading.Thread(target=_p, daemon=True).start()
    @staticmethod
    def power_up():
        if not PYGAME_OK: return
        def _p():
            for f in range(100, 2000, 80): SoundFX._beep(f,.02,.2,"robot"); time.sleep(.02)
        threading.Thread(target=_p, daemon=True).start()
    @staticmethod
    def wake():
        if not PYGAME_OK: return
        def _p():
            for f in [800,1000,1200]: SoundFX._beep(f,.05,.4,"robot"); time.sleep(.06)
        threading.Thread(target=_p, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════
#  MEMORY / NOTES
# ══════════════════════════════════════════════════════════════════════════
class MemoryStore:
    def __init__(self):
        self.notes  = self._load(NOTES_FILE, [])
        self.memory = self._load(MEM_FILE,   {})

    @staticmethod
    def _load(path, default):
        try:
            with open(path,"r",encoding="utf-8") as f: return json.load(f)
        except: return default

    @staticmethod
    def _save(path, data):
        try:
            with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
        except Exception as e: print(f"[MEM] {e}")

    def add_note(self, text):
        e = {"ts":datetime.datetime.now().isoformat(),"text":text}
        self.notes.append(e); self._save(NOTES_FILE, self.notes)
        return "Note saved, sir."

    def get_notes(self):
        if not self.notes: return "No notes yet, sir."
        lines = [f"{i+1}. [{n['ts'][:16]}] {n['text']}" for i,n in enumerate(self.notes[-15:])]
        return "Your recent notes:\n" + "\n".join(lines)

    def delete_note(self, idx=None):
        if idx is None:
            self.notes = []; self._save(NOTES_FILE, self.notes)
            return "All notes deleted, sir."
        try:
            self.notes.pop(int(idx)-1); self._save(NOTES_FILE, self.notes)
            return f"Note {idx} deleted, sir."
        except: return "Could not delete that note, sir."

    def remember(self, key, value):
        self.memory[key.lower()] = value; self._save(MEM_FILE, self.memory)

    def recall(self, key):
        v = self.memory.get(key.lower())
        return f"I remember: {key} = {v}, sir." if v else f"Nothing stored for '{key}', sir."

    def forget(self, key):
        if key.lower() in self.memory:
            del self.memory[key.lower()]; self._save(MEM_FILE, self.memory)
            return f"Forgotten: {key}, sir."
        return f"No memory for '{key}', sir."

    def all_memory(self):
        if not self.memory: return "Memory bank is empty, sir."
        return "Stored: " + "; ".join(f"{k}={v}" for k,v in list(self.memory.items())[-10:])


# ══════════════════════════════════════════════════════════════════════════
#  FILE UTILS
# ══════════════════════════════════════════════════════════════════════════
def _disk_usage_safe():
    try: return psutil.disk_usage('/')
    except:
        try:
            parts = psutil.disk_partitions()
            if parts: return psutil.disk_usage(parts[0].mountpoint)
        except: pass
    return None

def _folder_path(name):
    hm = os.path.expanduser("~")
    fm = {
        "documents": os.path.join(hm,"Documents"),
        "downloads": os.path.join(hm,"Downloads"),
        "desktop":   os.path.join(hm,"Desktop"),
        "pictures":  os.path.join(hm,"Pictures"),
        "music":     os.path.join(hm,"Music"),
        "videos":    os.path.join(hm,"Videos"),
        "files":     FILES_DIR
    }
    return fm.get(name.lower(), os.path.join(hm, name))

def create_file_doc(filename, content, folder=None):
    try:
        base = _folder_path(folder) if folder else os.path.join(os.path.expanduser("~"),"Documents")
        if os.path.isabs(filename): base=os.path.dirname(filename); filename=os.path.basename(filename)
        os.makedirs(base, exist_ok=True)
        if not any(filename.endswith(x) for x in ('.txt','.py','.html','.md','.csv','.json','.log')):
            filename += ".txt"
        path = os.path.join(base, filename)
        with open(path,"w",encoding="utf-8") as f: f.write(content)
        return f"File created at {path}, sir."
    except Exception as e: return f"Could not create file: {e}"

def read_file_doc(filename):
    try:
        for p in [filename,
                  os.path.join(os.path.expanduser("~"),"Documents",filename),
                  os.path.join(os.path.expanduser("~"),filename),
                  os.path.join(FILES_DIR,filename)]:
            if os.path.isfile(p):
                with open(p,"r",encoding="utf-8",errors="replace") as f:
                    return f"Contents of {os.path.basename(p)}:\n{f.read(3000)}"
        return f"File '{filename}' not found, sir."
    except Exception as e: return f"Could not read file: {e}"

def delete_file_doc(filename):
    try:
        for p in [filename,
                  os.path.join(os.path.expanduser("~"),"Documents",filename),
                  os.path.join(FILES_DIR,filename)]:
            if os.path.isfile(p): os.remove(p); return "File deleted, sir."
        return f"File '{filename}' not found, sir."
    except Exception as e: return f"Could not delete: {e}"

def list_files_in(folder):
    try:
        path = _folder_path(folder)
        if not os.path.isdir(path): return f"Folder '{folder}' not found, sir."
        items = sorted(os.listdir(path))[:25]
        return (f"Files in {folder}: " + ", ".join(items)) if items else f"{folder} is empty, sir."
    except Exception as e: return f"Could not list: {e}"

def open_path(path):
    try:
        if platform.system()=="Windows": os.startfile(path)
        elif platform.system()=="Darwin": subprocess.Popen(["open",path])
        else: subprocess.Popen(["xdg-open",path])
        return f"Opened {os.path.basename(path)}, sir."
    except Exception as e: return f"Could not open: {e}"

def close_window_by_name(name):
    name_l = name.lower(); killed = []
    for proc in psutil.process_iter(['name','pid']):
        try:
            if name_l in (proc.info['name'] or '').lower():
                proc.terminate(); killed.append(proc.info['name'])
        except: pass
    if killed: return f"Closed {', '.join(set(killed))}, sir."
    return f"Could not find '{name}' to close, sir."

def shutdown_system():
    if platform.system()=="Windows": subprocess.run(["shutdown","/s","/t","5"])
    else: subprocess.run(["sudo","shutdown","-h","now"])

def restart_system():
    if platform.system()=="Windows": subprocess.run(["shutdown","/r","/t","5"])
    else: subprocess.run(["sudo","shutdown","-r","now"])

def lock_system():
    if platform.system()=="Windows":
        subprocess.run(["rundll32.exe","user32.dll,LockWorkStation"])
        return "Workstation locked, sir."
    elif platform.system()=="Darwin":
        subprocess.run(["pmset","displaysleepnow"])
        return "Display locked, sir."
    return "Lock command sent, sir."

def send_email(to_addr, subject, body):
    if not GMAIL_USER or not GMAIL_PASS:
        return "Email credentials not configured. Please set GMAIL_USER and GMAIL_PASS in Settings, sir."
    try:
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = GMAIL_USER; msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(email.mime.text.MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(); server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg); server.quit()
        return f"Email sent to {to_addr} successfully, sir."
    except Exception as e:
        return f"Failed to send email: {e}"

def get_system_info_full():
    """Return comprehensive system information."""
    try:
        vm  = psutil.virtual_memory()
        du  = _disk_usage_safe()
        bat = psutil.sensors_battery()
        cpu_f = psutil.cpu_freq()
        net = psutil.net_if_addrs()
        lines = []
        lines.append(f"OS: {platform.system()} {platform.release()} {platform.version()}")
        lines.append(f"Machine: {platform.machine()} | Processor: {platform.processor()[:60]}")
        lines.append(f"CPU Cores: {psutil.cpu_count(False)} physical, {psutil.cpu_count()} logical")
        if cpu_f: lines.append(f"CPU Freq: {cpu_f.current:.0f} MHz (max {cpu_f.max:.0f} MHz)")
        lines.append(f"CPU Usage: {psutil.cpu_percent()}%")
        lines.append(f"RAM: {vm.total//1024**3} GB total, {vm.used//1024**3} GB used ({vm.percent}%)")
        if du: lines.append(f"Disk: {du.total//1024**3} GB total, {du.free//1024**3} GB free ({du.percent}% used)")
        if bat: lines.append(f"Battery: {bat.percent:.0f}% {'(Charging)' if bat.power_plugged else '(On Battery)'}")
        lines.append(f"Hostname: {socket.gethostname()}")
        try: lines.append(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
        except: pass
        bt = datetime.datetime.fromtimestamp(psutil.boot_time())
        up = datetime.datetime.now()-bt
        h,r = divmod(int(up.total_seconds()),3600); m2,s = divmod(r,60)
        lines.append(f"Uptime: {h}h {m2}m {s}s")
        return "\n".join(lines)
    except Exception as e:
        return f"System info error: {e}"


# ══════════════════════════════════════════════════════════════════════════
#  ALARM / REMINDER STORES
# ══════════════════════════════════════════════════════════════════════════
class AlarmStore(QObject):
    alarm_fired = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._alarms = self._load()
        QTimer(self, timeout=self._check, interval=5000).start()

    def _load(self):
        try:
            with open(ALARMS_FILE,"r") as f:
                data = json.load(f)
                return [(datetime.datetime.fromisoformat(a[0]),a[1],a[2]) for a in data]
        except: return []

    def _save(self):
        try:
            with open(ALARMS_FILE,"w") as f:
                json.dump([(a[0].isoformat(),a[1],a[2]) for a in self._alarms],f)
        except: pass

    def add_alarm(self, label, when, repeat=False):
        self._alarms.append((when,label,repeat)); self._save()
        diff = when - datetime.datetime.now()
        mins = max(0, int(diff.total_seconds()/60))
        return f"Alarm set for {when.strftime('%H:%M')} — {label}, sir. That is in {mins} minutes."

    def list_alarms(self):
        if not self._alarms: return "No alarms set, sir."
        now = datetime.datetime.now()
        lines = [f"{i+1}. {a[0].strftime('%H:%M')} — {a[1]} ({'repeat' if a[2] else 'once'})"
                 for i,a in enumerate(self._alarms) if a[0]>now]
        return ("Active alarms:\n"+"\n".join(lines)) if lines else "No future alarms, sir."

    def delete_alarm(self, idx=None):
        if idx is None:
            self._alarms=[]; self._save(); return "All alarms cleared, sir."
        try:
            r=self._alarms.pop(int(idx)-1); self._save()
            return f"Alarm '{r[1]}' deleted, sir."
        except: return "Could not delete alarm, sir."

    def _check(self):
        now=datetime.datetime.now(); keep=[]
        for when,label,repeat in self._alarms:
            if now>=when:
                self.alarm_fired.emit(label)
                if repeat: keep.append((when+datetime.timedelta(days=1),label,repeat))
            else: keep.append((when,label,repeat))
        if len(keep)!=len(self._alarms): self._alarms=keep; self._save()


class ReminderStore(QObject):
    fired = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent); self._list=[]
        QTimer(self, timeout=self._check, interval=8000).start()

    def add(self, text, when): self._list.append((when,text))

    def list_all(self):
        if not self._list: return "No reminders, sir."
        now=datetime.datetime.now()
        lines=[f"• {t} (in ~{max(0,int((w-now).total_seconds()/60))} min)" for w,t in self._list]
        return "Reminders:\n"+"\n".join(lines)

    def _check(self):
        now=datetime.datetime.now(); keep=[]
        for when,text in self._list:
            if now>=when: self.fired.emit(text)
            else: keep.append((when,text))
        self._list=keep


# ══════════════════════════════════════════════════════════════════════════
#  ROBOTIC TTS WORKER
# ══════════════════════════════════════════════════════════════════════════
class TTSWorker(QThread):
    finished = pyqtSignal()
    log_msg  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue=[]; self._lock=threading.Lock(); self._running=True; self._py_eng=None

    def speak(self, text):
        clean = re.sub(r"[*_`#>~|•\-]+", " ", str(text))
        clean = re.sub(r"\s+", " ", clean).strip()
        clean = RoboticVoiceProcessor.process_text_for_robot(clean)
        if clean:
            with self._lock: self._queue.append(clean)

    def stop(self):
        self._running=False
        if PYGAME_OK:
            try: pygame.mixer.music.stop()
            except: pass
        self.quit(); self.wait(3000)

    def clear_queue(self):
        with self._lock: self._queue.clear()
        if PYGAME_OK:
            try: pygame.mixer.music.stop()
            except: pass

    def _init_py(self):
        if not TTS_PYTTS: return
        try:
            # SAPI5 (pyttsx3's Windows backend) needs COM initialized on the
            # SAME thread it is used from. Since TTSWorker runs on its own
            # QThread, skipping this makes pyttsx3.init() fail silently and
            # Jarvis never speaks — this was the root cause of the mute bug.
            if platform.system() == "Windows":
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception as ce:
                    self.log_msg.emit(f"[TTS] COM init warning: {ce}")
            self._py_eng = pyttsx3.init()
            RoboticVoiceProcessor.apply_robot_effect_pyttsx3(self._py_eng)
        except Exception as e:
            self.log_msg.emit(f"[TTS] Engine init failed: {e}")
            self._py_eng = None

    def _speak_openai(self, text):
        if not (OPENAI_OK and OPENAI_API_KEY and PYGAME_OK): return False
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            resp = client.audio.speech.create(
                model=TTS_MODEL, voice=TTS_VOICE,
                input=text, response_format="mp3",
                speed=0.88
            )
            audio_io = io.BytesIO(resp.content)
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_io, "mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                self.msleep(40)
                if not self._running: pygame.mixer.music.stop(); break
            return True
        except Exception as e: self.log_msg.emit(f"[OPENAI TTS] {e}"); return False

    def _speak_py(self, text):
        if not self._py_eng: self._init_py()
        if not self._py_eng: return
        try: self._py_eng.say(text); self._py_eng.runAndWait()
        except Exception as e: self.log_msg.emit(f"[PYTTS] {e}"); self._py_eng=None

    def run(self):
        if not (OPENAI_OK and OPENAI_API_KEY and PYGAME_OK): self._init_py()
        while self._running:
            text = None
            with self._lock:
                if self._queue: text = self._queue.pop(0)
            if text:
                if not self._speak_openai(text): self._speak_py(text)
                self.finished.emit()
            else:
                self.msleep(40)


# ══════════════════════════════════════════════════════════════════════════
#  VOICE WORKER
# ══════════════════════════════════════════════════════════════════════════
class VoiceWorker(QThread):
    text_received = pyqtSignal(str)
    state_changed = pyqtSignal(str)
    level_changed = pyqtSignal(int)
    log_msg       = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running        = True
        self._paused         = False
        self._wake_word_mode = True
        self._mic_device_idx = None
        self._pause_lock     = threading.Lock()

    def pause(self):
        with self._pause_lock: self._paused = True

    def resume(self):
        with self._pause_lock: self._paused = False

    def set_always_on(self, v):
        self._wake_word_mode = not bool(v)

    @staticmethod
    def _has_wake_word(text):
        t = text.lower().strip()
        for ww in WAKE_WORDS:
            if ww in t: return True
        first = t.split()[0] if t.split() else ""
        for ww in ["jarvis","javis","jarwis"]:
            if VoiceWorker._lev(first, ww) <= 2: return True
        return False

    @staticmethod
    def _lev(a, b):
        if len(a)<len(b): a,b=b,a
        if not b: return len(a)
        prev=list(range(len(b)+1))
        for i,ca in enumerate(a):
            curr=[i+1]
            for j,cb in enumerate(b):
                curr.append(min(prev[j+1]+1,curr[j]+1,prev[j]+(0 if ca==cb else 1)))
            prev=curr
        return prev[-1]

    @staticmethod
    def _strip_wake(text):
        t=text.lower()
        for ww in sorted(WAKE_WORDS, key=len, reverse=True):
            t=t.replace(ww,"").strip()
        return t.lstrip(",. !").strip()

    @staticmethod
    def _estimate_level(audio_data):
        try:
            samples=np.frombuffer(audio_data,dtype=np.int16).astype(np.float32)
            return max(10, min(100, int(np.sqrt(np.mean(samples**2))/200)))
        except: return random.randint(40,80)

    def run(self):
        if not SR_OK:
            self.log_msg.emit("[VOICE] SpeechRecognition not installed."); return

        rec = sr.Recognizer()
        rec.energy_threshold                      = 300
        rec.dynamic_energy_threshold               = True
        rec.dynamic_energy_adjustment_damping      = 0.15
        rec.dynamic_energy_ratio                   = 1.5
        rec.pause_threshold                        = 0.8
        rec.non_speaking_duration                  = 0.5
        rec.operation_timeout                      = None

        mic = None
        retry_count = 0

        while self._running:
            with self._pause_lock:
                paused = self._paused
            if paused:
                self.msleep(100); continue

            if mic is None:
                try:
                    mic = sr.Microphone(device_index=self._mic_device_idx, sample_rate=16000)
                    with mic as src:
                        self.state_changed.emit("calibrating")
                        rec.adjust_for_ambient_noise(src, duration=1.5)
                    self.state_changed.emit("idle")
                    retry_count = 0
                    self.log_msg.emit(f"[VOICE] Mic ready. Threshold={rec.energy_threshold:.0f}")
                except Exception as e:
                    retry_count += 1
                    self.log_msg.emit(f"[MIC ERR #{retry_count}] {e}")
                    self.state_changed.emit("idle")
                    self.msleep(min(retry_count * 2000, 15000))
                    mic = None; continue

            try:
                with self._pause_lock:
                    paused = self._paused
                if paused: continue

                self.state_changed.emit("listening")
                with mic as src:
                    audio = rec.listen(src, timeout=5, phrase_time_limit=20)

                self.state_changed.emit("processing")
                lvl = self._estimate_level(audio.get_raw_data())
                self.level_changed.emit(lvl)

                text = ""
                for lang in ("en-US", "en-GB", "ur-PK"):
                    try:
                        text = rec.recognize_google(audio, language=lang, show_all=False)
                        if text: break
                    except sr.UnknownValueError: continue
                    except sr.RequestError: break

                if not text:
                    self.state_changed.emit("idle"); continue

                self.log_msg.emit(f"[🎤 STT] \"{text}\"")

                if self._wake_word_mode:
                    if self._has_wake_word(text):
                        SoundFX.wake()
                        clean = self._strip_wake(text)
                        if clean: self.text_received.emit(clean)
                        else:     self.text_received.emit("_wake_")
                    else:
                        self.state_changed.emit("idle")
                else:
                    clean = self._strip_wake(text)
                    if clean: self.text_received.emit(clean)
                    self.state_changed.emit("idle")

            except sr.WaitTimeoutError:   self.state_changed.emit("idle")
            except sr.UnknownValueError:  self.state_changed.emit("idle")
            except sr.RequestError as e:
                self.log_msg.emit(f"[STT NET] {e}")
                self.state_changed.emit("idle"); self.msleep(3000)
            except OSError as e:
                self.log_msg.emit(f"[MIC OS] {e}")
                mic = None; self.state_changed.emit("idle"); self.msleep(5000)
            except Exception as e:
                self.log_msg.emit(f"[VOICE ERR] {e}"); self.msleep(1000)

    def stop(self):
        self._running = False
        self.quit(); self.wait(3000)


# ══════════════════════════════════════════════════════════════════════════
#  AI WORKERS
# ══════════════════════════════════════════════════════════════════════════
class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, query, history, context="", parent=None):
        super().__init__(parent)
        self.query=query; self.history=list(history); self.context=context

    def run(self):
        full = f"[Context: {self.context}]\n{self.query}" if self.context else self.query
        if OPENAI_OK and OPENAI_API_KEY:
            try:
                client=openai.OpenAI(api_key=OPENAI_API_KEY)
                msgs=[{"role":"system","content":JARVIS_SYSTEM}]+self.history[-20:]+[{"role":"user","content":full}]
                resp=client.chat.completions.create(model=GPT_MODEL,messages=msgs,max_tokens=650,temperature=0.76)
                self.response_ready.emit(resp.choices[0].message.content.strip()); return
            except Exception as e:
                print(f"[GPT] {e}")
                gpt_err = str(e)
        else:
            gpt_err = None
        if CLAUDE_OK and ANTHROPIC_API_KEY:
            try:
                client=anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                msgs=self.history[-14:]+[{"role":"user","content":full}]
                msg=client.messages.create(model=CLAUDE_MODEL,max_tokens=650,system=JARVIS_SYSTEM,messages=msgs)
                self.response_ready.emit(msg.content[0].text.strip()); return
            except Exception as e:
                print(f"[CLAUDE] {e}")
                self.error_occurred.emit(f"AI call failed, sir: {e}"); return
        if gpt_err:
            self.error_occurred.emit(f"AI call failed, sir: {gpt_err}"); return
        self.error_occurred.emit("No AI configured, sir. Please set your API key in Settings.")


class ImageGenWorker(QThread):
    done=pyqtSignal(str,str); fail=pyqtSignal(str)
    def __init__(self,prompt,parent=None): super().__init__(parent); self.prompt=prompt
    def run(self):
        if not (OPENAI_OK and OPENAI_API_KEY): self.fail.emit("OpenAI API key required, sir."); return
        try:
            client=openai.OpenAI(api_key=OPENAI_API_KEY)
            resp=client.images.generate(model="dall-e-3",prompt=self.prompt,n=1,size="1024x1024",quality="standard")
            self.done.emit(self.prompt, resp.data[0].url)
        except Exception as e: self.fail.emit(f"Image generation failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
#  ARC REACTOR WIDGET
# ══════════════════════════════════════════════════════════════════════════
class ArcReactor(QWidget):
    def __init__(self, sz=140):
        super().__init__(); self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._angle=0.0; self._pulse=0.0; self._energy=1.0; self._spark=0.0
        self._outer_angle=0.0; self._ripple=0.0
        QTimer(self, timeout=self._tick, interval=16).start()

    def set_energy(self, v): self._energy=max(0.0, min(1.0, float(v)))

    def _tick(self):
        self._angle=(self._angle+2.8)%360
        self._outer_angle=(self._outer_angle-1.2)%360
        self._pulse+=0.08
        self._spark=(self._spark+0.18)%360
        self._ripple=(self._ripple+0.05)%1.0
        self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx=cy=self.width()//2; R=cx-4
        e=self._energy
        pv=0.8+0.2*math.sin(self._pulse*2.5)

        for i in range(8):
            a=max(0, int(45-i*7)*e)
            p.setPen(QPen(QColor(0, int(200*e), int(255*e), int(a)), 2-i*.15))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx,cy), R+i*5, R+i*5)

        rr = int(R*(0.9 + self._ripple*0.4))
        ra = int(max(0, 80*(1-self._ripple)))
        p.setPen(QPen(QColor(0,230,255,int(ra*e)), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPoint(cx,cy), rr, rr)

        p.save(); p.translate(cx,cy); p.rotate(self._outer_angle)
        for i in range(12):
            a1=math.radians(i*30); a2=math.radians(i*30+22)
            ri,ro=int(R*.82),int(R*.96)
            pts=[QPointF(math.cos(a1)*ri,math.sin(a1)*ri),
                 QPointF(math.cos(a1)*ro,math.sin(a1)*ro),
                 QPointF(math.cos(a2)*ro,math.sin(a2)*ro),
                 QPointF(math.cos(a2)*ri,math.sin(a2)*ri)]
            al=int(70+50*math.sin(self._pulse*1.5+i*.5))
            p.setBrush(QBrush(QColor(0,int(160*e),int(240*e),int(al*e))))
            p.setPen(QPen(QColor(0,int(220*e),255,int(160*e)), 0.8))
            p.drawPolygon(QPolygonF(pts))
        p.restore()

        p.save(); p.translate(cx,cy); p.rotate(self._angle)
        for i in range(6):
            a1=math.radians(i*60); a2=math.radians(i*60+52)
            ri,ro=int(R*.44),int(R*.76)
            pts=[QPointF(math.cos(a1)*ri,math.sin(a1)*ri),
                 QPointF(math.cos(a1)*ro,math.sin(a1)*ro),
                 QPointF(math.cos(a2)*ro,math.sin(a2)*ro),
                 QPointF(math.cos(a2)*ri,math.sin(a2)*ri)]
            al=int(100+70*math.sin(self._pulse+i))
            p.setBrush(QBrush(QColor(0,int(180*e),int(255*e),int(al*e))))
            p.setPen(QPen(QColor(0,int(230*e),255,int(200*e)), 1.2))
            p.drawPolygon(QPolygonF(pts))
        p.restore()

        p.save(); p.translate(cx,cy)
        hex_pts=[QPointF(math.cos(math.radians(i*60+30))*int(R*.36),
                          math.sin(math.radians(i*60+30))*int(R*.36)) for i in range(6)]
        p.setPen(QPen(QColor(0,int(200*e),255,int(130*e)),1.5))
        p.setBrush(QBrush(QColor(0,30,80,50)))
        p.drawPolygon(QPolygonF(hex_pts))
        p.restore()

        cr=int(R*.28)
        g=QRadialGradient(cx,cy,cr)
        g.setColorAt(0.0, QColor(230,250,255,int(245*e*pv)))
        g.setColorAt(0.35,QColor(0,220,255,int(220*e*pv)))
        g.setColorAt(0.7, QColor(0,100,220,int(120*e)))
        g.setColorAt(1.0, QColor(0,30,80,20))
        p.setBrush(QBrush(g)); p.setPen(QPen(QColor(0,240,255,220),1.5))
        p.drawEllipse(QPoint(cx,cy), cr, cr)

        sa=math.radians(self._spark*360/360)
        sx=int(cx+math.cos(sa)*R*.72); sy=int(cy+math.sin(sa)*R*.72)
        sg=QRadialGradient(sx,sy,5)
        sg.setColorAt(0,QColor(255,255,255,220)); sg.setColorAt(1,QColor(0,200,255,0))
        p.setBrush(QBrush(sg)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(sx,sy),5,5)

        p.setFont(QFont("Consolas",6,QFont.Bold))
        p.setPen(QColor(0,int(200*e),255,int(160*e)))
        p.drawText(QRect(0,cy+cr+2,self.width(),12),Qt.AlignCenter,"JARVIS")


# ══════════════════════════════════════════════════════════════════════════
#  RADAR WIDGET
# ══════════════════════════════════════════════════════════════════════════
class RadarWidget(QWidget):
    def __init__(self, sz=140, label="SCAN"):
        super().__init__(); self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label=label; self._angle=0.0
        self._blips=[(random.uniform(0.2,0.85), random.uniform(0,360), random.randint(2,5))
                       for _ in range(random.randint(4,7))]
        QTimer(self, timeout=self._tick, interval=18).start()

    def _tick(self): self._angle=(self._angle+2.2)%360; self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx=cy=self.width()//2; R=cx-4

        bg=QRadialGradient(cx,cy,R)
        bg.setColorAt(0, QColor(0,50,20,200)); bg.setColorAt(1, QColor(0,10,5,230))
        p.setBrush(QBrush(bg)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(cx,cy),R,R)

        for r in [.25,.5,.75,1.0]:
            p.setPen(QPen(QColor(0,200,80,int(25+r*20)),0.8))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx,cy),int(R*r),int(R*r))

        p.setPen(QPen(QColor(0,200,80,30),0.6))
        p.drawLine(cx-R,cy,cx+R,cy); p.drawLine(cx,cy-R,cx,cy+R)

        p.save(); p.translate(cx,cy); p.rotate(self._angle)
        sweep=QConicalGradient(0,0,-90)
        sweep.setColorAt(0.0, QColor(0,255,80,150))
        sweep.setColorAt(0.2, QColor(0,255,80,30))
        sweep.setColorAt(0.21, QColor(0,0,0,0))
        sweep.setColorAt(1.0, QColor(0,0,0,0))
        p.setBrush(QBrush(sweep)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(0,0),R-1,R-1)
        p.setPen(QPen(QColor(0,255,80,220),1.5))
        p.drawLine(0,0,R-1,0)
        p.restore()

        for dist,angle,sz2 in self._blips:
            ba=math.radians(angle+self._angle*.2)
            bx=int(cx+math.cos(ba)*R*dist); by=int(cy+math.sin(ba)*R*dist)
            diff=abs((self._angle-angle+360)%360)
            alpha=int(min(255,220*(1-diff/100))) if diff<100 else 0
            if alpha>20:
                p.setBrush(QBrush(QColor(0,255,80,alpha)))
                p.setPen(QPen(QColor(0,255,80,alpha//2),1))
                p.drawEllipse(QPoint(bx,by),sz2//2,sz2//2)

        p.setPen(QColor(0,180,80,140)); p.setFont(QFont("Consolas",7,QFont.Bold))
        p.drawText(self.rect(),Qt.AlignCenter,self.label)
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor(0,220,80,90),1.5))
        p.drawEllipse(QPoint(cx,cy),R,R)


# ══════════════════════════════════════════════════════════════════════════
#  VOICE ORB
# ══════════════════════════════════════════════════════════════════════════
class VoiceOrb(QWidget):
    def __init__(self, sz=130):
        super().__init__(); self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.level=8; self._pulse=0.0; self.state="idle"
        self._bars=np.zeros(80)
        QTimer(self, timeout=self._tick, interval=20).start()

    def set_level(self, v): self.level=max(5, min(int(v), 100))
    def set_state(self, s): self.state=s

    def _tick(self):
        self._pulse+=0.12
        target = self.level/100.0 if self.state in ("listening","speaking") else 0.04
        for i in range(len(self._bars)):
            noise=random.uniform(0,target)*abs(math.sin(self._pulse+i*.3))
            self._bars[i]+=(noise-self._bars[i])*.28
        self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx=cy=self.width()//2; R=cx-6

        cmap={
            "listening" :(0,255,140),
            "processing":(255,160,0),
            "speaking"  :(0,210,255),
            "thinking"  :(180,80,255),
            "idle"      :(0,120,220),
            "calibrating":(255,200,0),
        }
        rc=QColor(*cmap.get(self.state,(0,150,200)))

        for i in range(7):
            a=max(0,50-i*8)
            p.setPen(QPen(QColor(rc.red(),rc.green(),rc.blue(),a),8-i*.8))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx,cy),R+i*4,R+i*4)

        n=len(self._bars)
        for i,amp in enumerate(self._bars):
            angle=2*math.pi*i/n
            r1=R*.5; r2=r1+amp*R*.48
            al=min(255,int(80+amp*450))
            p.setPen(QPen(QColor(rc.red(),rc.green(),rc.blue(),al),2.2))
            p.drawLine(
                int(cx+math.cos(angle)*r1),int(cy+math.sin(angle)*r1),
                int(cx+math.cos(angle)*r2),int(cy+math.sin(angle)*r2)
            )

        gr=QRadialGradient(cx,cy,int(R*.5))
        gr.setColorAt(0,QColor(rc.red(),rc.green(),rc.blue(),65))
        gr.setColorAt(1,QColor(5,8,22,210))
        p.setBrush(QBrush(gr)); p.setPen(QPen(rc,1.5))
        p.drawEllipse(QPoint(cx,cy),int(R*.5),int(R*.5))

        icon_map={"listening":"🎤","processing":"⟳","speaking":"◎",
                  "thinking":"⋯","idle":"◌","calibrating":"⊛"}
        p.setPen(QPen(rc,2)); p.setFont(QFont("Segoe UI Symbol",14))
        p.drawText(QRect(0,-8,self.width(),self.height()),Qt.AlignCenter,icon_map.get(self.state,"◌"))

        p.setPen(QColor(rc.red(),rc.green(),rc.blue(),180))
        p.setFont(QFont("Consolas",7,QFont.Bold))
        p.drawText(QRect(0,self.height()-16,self.width(),16),Qt.AlignCenter,self.state.upper())

        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(rc.red(),rc.green(),rc.blue(),100),1.5))
        p.drawEllipse(QPoint(cx,cy),R,R)


# ══════════════════════════════════════════════════════════════════════════
#  MINI RING GAUGE
# ══════════════════════════════════════════════════════════════════════════
class MiniRing(QWidget):
    def __init__(self, label, color, sz=80):
        super().__init__(); self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label=label; self.value=0; self._disp=0.0
        self.color=QColor(*color)
        QTimer(self, timeout=self._smooth, interval=22).start()

    def set_value(self, v): self.value=max(0, min(100, float(v)))

    def _smooth(self): self._disp+=(self.value-self._disp)*.10; self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx=cy=self.width()//2; R=self.width()//2-6

        p.setPen(QPen(QColor(self.color.red(),self.color.green(),self.color.blue(),20),8))
        p.setBrush(Qt.NoBrush)
        p.drawArc(cx-R,cy-R,R*2,R*2,90*16,-360*16)

        for i in range(3):
            pen=QPen(QColor(self.color.red(),self.color.green(),self.color.blue(),30-i*8),10+i*2)
            pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
            p.drawArc(cx-R,cy-R,R*2,R*2,90*16,-int(360*self._disp/100)*16)

        pen=QPen(self.color,7); pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
        p.drawArc(cx-R,cy-R,R*2,R*2,90*16,-int(360*self._disp/100)*16)

        p.setPen(self.color)
        p.setFont(QFont("Consolas",9,QFont.Bold))
        p.drawText(QRect(0,-4,self.width(),self.height()),Qt.AlignCenter,f"{int(self._disp)}%")
        p.setFont(QFont("Consolas",7))
        p.setPen(QColor(self.color.red(),self.color.green(),self.color.blue(),160))
        p.drawText(QRect(0,12,self.width(),self.height()),Qt.AlignCenter,self.label)

        if self._disp > 85:
            a=int(20*abs(math.sin(time.time()*5)))
            p.setBrush(QBrush(QColor(255,50,50,a)))
            p.setPen(Qt.NoPen); p.drawEllipse(QPoint(cx,cy),R+8,R+8)


# ══════════════════════════════════════════════════════════════════════════
#  NETWORK WAVEFORM
# ══════════════════════════════════════════════════════════════════════════
class NetWave(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.vals=np.zeros(100); self.setFixedHeight(40)

    def push(self, v):
        self.vals=np.roll(self.vals,-1); self.vals[-1]=float(np.clip(v,0,1)); self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height(); mid=h*.8; step=w/max(len(self.vals)-1,1)
        path=QPainterPath(); path.moveTo(0,mid)
        for i,v in enumerate(self.vals): path.lineTo(i*step, mid-v*mid*.85)
        path.lineTo(w,mid); path.lineTo(0,mid)
        grad=QLinearGradient(0,0,0,h)
        grad.setColorAt(0.0,QColor(0,180,255,50)); grad.setColorAt(1.0,QColor(0,180,255,0))
        p.fillPath(path,QBrush(grad))
        lg=QLinearGradient(0,0,w,0)
        lg.setColorAt(0.0,QColor(0,80,200,60)); lg.setColorAt(0.5,QColor(0,200,255,220))
        lg.setColorAt(1.0,QColor(0,255,180,255))
        p.setPen(QPen(QBrush(lg),1.5))
        for i in range(len(self.vals)-1):
            p.drawLine(int(i*step),int(mid-self.vals[i]*mid*.85),
                       int((i+1)*step),int(mid-self.vals[i+1]*mid*.85))


# ══════════════════════════════════════════════════════════════════════════
#  HUD CORNER BRACKETS
# ══════════════════════════════════════════════════════════════════════════
class HUDCorner(QWidget):
    def __init__(self, corner="tl", sz=50, color=(0,200,255)):
        super().__init__(); self.setFixedSize(sz,sz)
        self.corner=corner; self._pulse=0.0; self._color=color
        self.setAttribute(Qt.WA_TranslucentBackground)
        QTimer(self,timeout=self._tick,interval=30).start()

    def _tick(self): self._pulse+=0.08; self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height(); L=min(w,h)//2+4
        a=int(140+80*math.sin(self._pulse))
        r,g,b=self._color; c=self.corner
        p.setPen(QPen(QColor(r,g,b,a),2))
        if c=="tl":   p.drawLine(0,L,0,0); p.drawLine(0,0,L,0)
        elif c=="tr": p.drawLine(w-L,0,w,0); p.drawLine(w,0,w,L)
        elif c=="bl": p.drawLine(0,h-L,0,h); p.drawLine(0,h,L,h)
        elif c=="br": p.drawLine(w-L,h,w,h); p.drawLine(w,h-L,w,h)
        p.setPen(QPen(QColor(r,g,b,int(a*.4)),4))
        if c=="tl":   p.drawLine(0,L-2,0,2); p.drawLine(2,0,L-2,0)
        elif c=="tr": p.drawLine(w-L+2,0,w,0); p.drawLine(w,0,w,L-2)
        elif c=="bl": p.drawLine(0,h-L+2,0,h); p.drawLine(0,h,L-2,h)
        elif c=="br": p.drawLine(w-L+2,h,w,h); p.drawLine(w,h-L+2,w,h)
        dot_a=int(120+80*math.sin(self._pulse*1.3))
        cx2 = 3 if c in ("tl","bl") else w-3
        cy2 = 3 if c in ("tl","tr") else h-3
        p.setBrush(QBrush(QColor(r,g,b,dot_a))); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(cx2,cy2),3,3)


# ══════════════════════════════════════════════════════════════════════════
#  HEX GRID BACKGROUND
# ══════════════════════════════════════════════════════════════════════════
class HexBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._off=0.0; self._scan=0.0; self._bg_pix=None
        self._load_bg()
        QTimer(self,timeout=self._tick,interval=40).start()

    def _load_bg(self):
        if os.path.isfile(BG_IMAGE):
            try: self._bg_pix = QPixmap(BG_IMAGE)
            except: self._bg_pix=None

    def _tick(self):
        self._off=(self._off+0.25)%60
        self._scan=(self._scan+1.0)%(self.height() or 900)
        self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height()
        if not w or not h: return

        if self._bg_pix and not self._bg_pix.isNull():
            scaled = self._bg_pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (w - scaled.width()) // 2
            y = (h - scaled.height()) // 2
            p.setOpacity(0.18); p.drawPixmap(x, y, scaled); p.setOpacity(1.0)

        p.fillRect(0,0,w,h,QColor(3,8,22,200))

        sz,dx,dy=24,24*1.732,24*1.5
        p.setPen(QPen(QColor(0,120,255,5),0.6))
        row=0; y=-dy+(self._off*.5%dy)
        while y<h+dy:
            x=-dx+((dx/2) if row%2 else 0)
            while x<w+dx:
                pts=[QPointF(x+sz*math.cos(math.radians(60*i-30))*.78,
                             y+sz*math.sin(math.radians(60*i-30))*.78) for i in range(6)]
                p.drawPolygon(QPolygonF(pts)); x+=dx
            y+=dy; row+=1

        sg=QLinearGradient(0,self._scan-60,0,self._scan+60)
        sg.setColorAt(0.0,QColor(0,180,255,0))
        sg.setColorAt(0.5,QColor(0,180,255,10))
        sg.setColorAt(1.0,QColor(0,180,255,0))
        p.fillRect(0,int(self._scan)-60,w,120,QBrush(sg))


# ══════════════════════════════════════════════════════════════════════════
#  IRON MAN FIGURE
# ══════════════════════════════════════════════════════════════════════════
class IronManFigure(QWidget):
    def __init__(self, w=280, h=420):
        super().__init__(); self.setFixedSize(w, h)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._pulse=0.0; self._scan=0.0; self._energy_ring=0.0
        QTimer(self,timeout=self._tick,interval=18).start()

    def _tick(self):
        self._pulse+=0.055
        self._scan=(self._scan+0.8)%self.height()
        self._energy_ring=(self._energy_ring+1.5)%360
        self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height()
        pv=0.7+0.3*math.sin(self._pulse*2)
        pv2=0.6+0.4*math.sin(self._pulse*1.3+1.0)

        bg=QRadialGradient(w//2,h//2,w*.7)
        bg.setColorAt(0,QColor(0,80,180,int(30*pv)))
        bg.setColorAt(0.5,QColor(0,40,100,int(15*pv)))
        bg.setColorAt(1,QColor(0,0,0,0))
        p.fillRect(0,0,w,h,QBrush(bg))

        hx,hy,hw,hh=w//2-30,10,60,72
        hg=QRadialGradient(w//2,hy+hh//2,40)
        hg.setColorAt(0,QColor(0,100,200,int(40*pv))); hg.setColorAt(1,QColor(0,0,0,0))
        p.fillRect(hx-10,hy-5,hw+20,hh+10,QBrush(hg))
        p.setPen(QPen(QColor(0,180,255,int(160*pv)),1.5))
        p.setBrush(QBrush(QColor(0,20,60,int(100*pv))))
        p.drawRoundedRect(hx,hy,hw,hh,6,6)
        p.setPen(QPen(QColor(0,150,255,int(80*pv)),1))
        p.drawLine(hx+hw//2,hy+8,hx+hw//2,hy+hh-8)
        p.drawLine(hx+8,hy+hh//2,hx+hw-8,hy+hh//2)

        ey=hy+20
        for ex in [hx+8, hx+hw-28]:
            eye_g=QLinearGradient(ex,ey,ex+20,ey+11)
            eye_g.setColorAt(0,QColor(0,220,255,int(250*pv)))
            eye_g.setColorAt(1,QColor(0,130,220,int(130*pv)))
            p.setBrush(QBrush(eye_g)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(ex,ey,20,11,3,3)
            for i in range(4):
                a=max(0,int(40-i*10)*int(pv))
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(QColor(0,200,255,a),i+1))
                p.drawRoundedRect(ex-i,ey-i,20+i*2,11+i*2,3+i,3+i)

        ty=hy+hh+6; tx=w//2-50; tw=100; th=130
        tg=QRadialGradient(w//2,ty+th//2,70)
        tg.setColorAt(0,QColor(0,80,180,int(30*pv))); tg.setColorAt(1,QColor(0,0,0,0))
        p.fillRect(tx-20,ty-5,tw+40,th+10,QBrush(tg))
        torso=QPolygonF([
            QPointF(tx+10,ty), QPointF(tx+tw-10,ty),
            QPointF(tx+tw+2,ty+th*.35), QPointF(tx+tw-2,ty+th),
            QPointF(tx+2,ty+th), QPointF(tx-2,ty+th*.35)
        ])
        p.setPen(QPen(QColor(0,160,255,int(130*pv)),1.5))
        p.setBrush(QBrush(QColor(0,15,55,int(100*pv))))
        p.drawPolygon(torso)
        p.setPen(QPen(QColor(0,120,200,int(60*pv)),1))
        p.drawLine(tx+tw//2,ty+10,tx+tw//2,ty+th-10)
        for i in range(3):
            y2=ty+30+i*35; p.drawLine(tx+15,y2,tx+tw-15,y2)

        arc_cx=w//2; arc_cy=ty+50
        for i in range(8):
            a=max(0,int(55-i*8)*pv)
            p.setPen(QPen(QColor(0,200,255,int(a)),2.5-i*.25))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(arc_cx,arc_cy),28+i*7,28+i*7)
        p.save(); p.translate(arc_cx,arc_cy); p.rotate(self._energy_ring)
        for i in range(6):
            a1=math.radians(i*60); a2=math.radians(i*60+48)
            ri,ro=22,30
            pts=[QPointF(math.cos(a1)*ri,math.sin(a1)*ri),
                 QPointF(math.cos(a1)*ro,math.sin(a1)*ro),
                 QPointF(math.cos(a2)*ro,math.sin(a2)*ro),
                 QPointF(math.cos(a2)*ri,math.sin(a2)*ri)]
            al=int(80+60*math.sin(self._pulse+i))
            p.setBrush(QBrush(QColor(0,int(180*pv),int(255*pv),int(al*pv))))
            p.setPen(Qt.NoPen); p.drawPolygon(QPolygonF(pts))
        p.restore()
        arc_r=QRadialGradient(arc_cx,arc_cy,22)
        arc_r.setColorAt(0,QColor(230,248,255,int(248*pv)))
        arc_r.setColorAt(0.35,QColor(0,220,255,int(220*pv2)))
        arc_r.setColorAt(0.7,QColor(0,80,180,int(100*pv)))
        arc_r.setColorAt(1,QColor(0,30,80,40))
        p.setBrush(QBrush(arc_r)); p.setPen(QPen(QColor(0,240,255,220),1.5))
        p.drawEllipse(QPoint(arc_cx,arc_cy),22,22)

        for sx,sw in [(tx-36,32),(tx+tw+4,32)]:
            sg2=QLinearGradient(sx,ty,sx+sw,ty+60)
            sg2.setColorAt(0,QColor(0,100,200,int(80*pv)))
            sg2.setColorAt(1,QColor(0,40,100,int(50*pv)))
            p.setPen(QPen(QColor(0,160,255,int(110*pv)),1.2))
            p.setBrush(QBrush(sg2))
            p.drawRoundedRect(sx,ty+4,sw,55,8,8)
            p.setPen(QPen(QColor(0,200,255,int(80*pv)),1))
            p.drawLine(sx+4,ty+20,sx+sw-4,ty+20)
            p.drawLine(sx+4,ty+35,sx+sw-4,ty+35)

        for ax,aw in [(tx-44,24),(tx+tw+12,24)]:
            p.setPen(QPen(QColor(0,140,255,int(95*pv)),1.2))
            p.setBrush(QBrush(QColor(0,12,45,int(85*pv))))
            p.drawRoundedRect(ax,ty+52,aw,90,6,6)
            p.setPen(QPen(QColor(0,120,200,int(55*pv)),1))
            for yi in range(3): p.drawLine(ax+3,ty+68+yi*22,ax+aw-3,ty+68+yi*22)

        p.setPen(QPen(QColor(0,140,255,int(80*pv)),1))
        p.setBrush(QBrush(QColor(0,12,45,int(65*pv))))
        p.drawRoundedRect(tx+8,ty+th+2,tw-16,28,4,4)
        for lx,lw in [(tx+10,35),(tx+tw-45,35)]:
            p.setPen(QPen(QColor(0,120,240,int(70*pv)),1))
            p.setBrush(QBrush(QColor(0,10,40,int(55*pv))))
            p.drawRoundedRect(lx,ty+th+28,lw,55,5,5)

        sg3=QLinearGradient(0,self._scan-18,0,self._scan+18)
        sg3.setColorAt(0,QColor(0,200,255,0))
        sg3.setColorAt(0.5,QColor(0,200,255,int(60*pv)))
        sg3.setColorAt(1,QColor(0,200,255,0))
        p.fillRect(tx-45,int(self._scan)-18,tw+90,36,QBrush(sg3))

        p.setFont(QFont("Consolas",7))
        labels_l=[("ARMOR","100%",(0,255,140)),("POWER","MAX",(0,210,255)),
                  ("SHIELD","ON",(0,255,180)),("BOOST","RDY",(0,200,255))]
        labels_r=[("CPU",f"{random.randint(40,95)}%",(0,210,255)),
                  ("AI","ONLINE",(0,255,140)),
                  ("NET","LIVE",(0,200,255)),
                  ("SYS","OK",(0,255,180))]
        for i,(lbl,val,col) in enumerate(labels_l):
            a=int(120*pv)
            p.setPen(QColor(*col,a)); p.drawText(2,ty+12+i*22,lbl)
            p.setPen(QColor(*col,int(a*1.4))); p.drawText(2,ty+22+i*22,val)
        for i,(lbl,val,col) in enumerate(labels_r):
            a=int(120*pv)
            p.setPen(QColor(*col,a)); p.drawText(w-42,ty+12+i*22,lbl)
            p.setPen(QColor(*col,int(a*1.4))); p.drawText(w-42,ty+22+i*22,val)

        p.setPen(QPen(QColor(0,150,255,int(40*pv)),0.8))
        p.drawLine(2,ty+20,tx-10,ty+25); p.drawLine(2,ty+60,tx-10,ty+65)
        p.drawLine(2,ty+100,tx-10,ty+95)
        p.drawLine(w-2,ty+20,tx+tw+10,ty+25); p.drawLine(w-2,ty+60,tx+tw+10,ty+65)
        p.drawLine(w-2,ty+100,tx+tw+10,ty+95)


# ══════════════════════════════════════════════════════════════════════════
#  CIRCULAR GAUGE
# ══════════════════════════════════════════════════════════════════════════
class CircularGauge(QWidget):
    def __init__(self, label, color, sz=120, unit="%"):
        super().__init__(); self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label=label; self.unit=unit; self.value=0; self._disp=0.0
        self.color=QColor(*color); self._pulse=0.0
        QTimer(self, timeout=self._smooth, interval=22).start()

    def set_value(self, v): self.value=max(0, min(100, float(v)))

    def _smooth(self):
        self._disp+=(self.value-self._disp)*.08
        self._pulse+=0.07; self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx=cy=self.width()//2; R=self.width()//2-10

        for i in range(4):
            pen=QPen(QColor(self.color.red(),self.color.green(),self.color.blue(),12-i*2),14-i*2)
            p.setPen(pen); p.setBrush(Qt.NoBrush)
            p.drawArc(cx-R,cy-R,R*2,R*2,-40*16,-(360-80)*16)

        p.setPen(QPen(QColor(self.color.red(),self.color.green(),self.color.blue(),18),8))
        p.drawArc(cx-R,cy-R,R*2,R*2,-40*16,-(360-80)*16)

        for i in range(3):
            gpen=QPen(QColor(self.color.red(),self.color.green(),self.color.blue(),30-i*8),11+i*2)
            gpen.setCapStyle(Qt.RoundCap); p.setPen(gpen)
            sweep=int((360-80)*self._disp/100)
            p.drawArc(cx-R,cy-R,R*2,R*2,-40*16,-sweep*16)

        pen=QPen(self.color,8); pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
        sweep=int((360-80)*self._disp/100)
        p.drawArc(cx-R,cy-R,R*2,R*2,-40*16,-sweep*16)

        for i in range(11):
            angle=math.radians(-40+i*28)
            r1=R-2; r2=R+4 if i%5==0 else R+2
            p.setPen(QPen(QColor(self.color.red(),self.color.green(),self.color.blue(),80),1))
            p.drawLine(int(cx+math.cos(angle)*r1),int(cy+math.sin(angle)*r1),
                       int(cx+math.cos(angle)*r2),int(cy+math.sin(angle)*r2))

        p.setPen(self.color)
        p.setFont(QFont("Consolas",12,QFont.Bold))
        p.drawText(QRect(0,-8,self.width(),self.height()),Qt.AlignCenter,f"{int(self._disp)}{self.unit}")
        p.setFont(QFont("Consolas",7))
        p.setPen(QColor(self.color.red(),self.color.green(),self.color.blue(),150))
        p.drawText(QRect(0,12,self.width(),self.height()),Qt.AlignCenter,self.label)

        if self._disp > 85:
            pv=0.8+0.2*math.sin(self._pulse*2)
            a=int(18*abs(math.sin(time.time()*5))*pv)
            p.setBrush(QBrush(QColor(255,50,50,a))); p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(cx,cy),R+10,R+10)


# ══════════════════════════════════════════════════════════════════════════
#  POWER BAR
# ══════════════════════════════════════════════════════════════════════════
class PowerBar(QWidget):
    def __init__(self, label="POWER LEVEL", color=(0,255,140)):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(28); self.label=label
        self.value=100; self._disp=0.0
        self.color=QColor(*color); self._pulse=0.0
        QTimer(self,timeout=self._smooth,interval=22).start()

    def set_value(self, v): self.value=max(0,min(100,float(v)))

    def _smooth(self):
        self._disp+=(self.value-self._disp)*.08
        self._pulse+=0.08; self.update()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height(); pv=0.85+0.15*math.sin(self._pulse*2)
        bar_x=130; bar_w=w-bar_x-10; bar_h=8; bar_y=(h-bar_h)//2
        p.setFont(QFont("Consolas",8,QFont.Bold))
        p.setPen(QColor(self.color.red(),self.color.green(),self.color.blue(),180))
        p.drawText(0,0,120,h,Qt.AlignVCenter|Qt.AlignLeft,self.label)
        p.setBrush(QBrush(QColor(self.color.red(),self.color.green(),self.color.blue(),18)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar_x,bar_y,bar_w,bar_h,4,4)
        fill_w=int(bar_w*self._disp/100)
        if fill_w>0:
            gd=QLinearGradient(bar_x,0,bar_x+bar_w,0)
            gd.setColorAt(0,QColor(0,150,80,int(200*pv)))
            gd.setColorAt(0.7,QColor(self.color.red(),self.color.green(),self.color.blue(),int(240*pv)))
            gd.setColorAt(1,QColor(255,255,255,int(200*pv)))
            p.setBrush(QBrush(gd)); p.drawRoundedRect(bar_x,bar_y,fill_w,bar_h,4,4)
            p.setBrush(QBrush(QColor(self.color.red(),self.color.green(),self.color.blue(),int(30*pv))))
            p.drawRoundedRect(bar_x-1,bar_y-2,fill_w+2,bar_h+4,5,5)
        p.setFont(QFont("Consolas",8,QFont.Bold))
        p.setPen(QColor(self.color.red(),self.color.green(),self.color.blue(),220))
        p.drawText(bar_x+bar_w+4,0,45,h,Qt.AlignVCenter,f"{int(self._disp)}%")


# ══════════════════════════════════════════════════════════════════════════
#  MEDIA PLAYER
# ══════════════════════════════════════════════════════════════════════════
class MediaPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._player=QMediaPlayer(self); self._current=""; self._playlist=[]; self._pl_idx=0
        self._build_ui()
        self._player.stateChanged.connect(self._on_state)
        self._player.positionChanged.connect(self._on_pos)
        self._player.durationChanged.connect(self._on_dur)
        self._player.mediaStatusChanged.connect(self._on_media_status)

    def _build_ui(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(4,4,4,4); lay.setSpacing(4)
        self.track_lbl=QLabel("♪  No media loaded")
        self.track_lbl.setStyleSheet(f"color:{CYAN_GLOW};font:bold 10px Consolas;background:transparent;padding:2px;")
        self.track_lbl.setAlignment(Qt.AlignCenter); self.track_lbl.setWordWrap(True)
        lay.addWidget(self.track_lbl)
        self.seek=QSlider(Qt.Horizontal); self.seek.setRange(0,0)
        self.seek.setStyleSheet(f"""
            QSlider::groove:horizontal{{height:4px;background:rgba(0,200,255,15);border-radius:2px;}}
            QSlider::handle:horizontal{{width:10px;height:10px;margin:-3px 0;background:{CYAN};border-radius:5px;}}
            QSlider::sub-page:horizontal{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0055ff,stop:1 #00ffcc);border-radius:2px;}}""")
        self.seek.sliderMoved.connect(self._player.setPosition); lay.addWidget(self.seek)
        self.time_lbl=QLabel("0:00 / 0:00")
        self.time_lbl.setStyleSheet(f"color:{CYAN_DIM};font:8px Consolas;")
        self.time_lbl.setAlignment(Qt.AlignCenter); lay.addWidget(self.time_lbl)
        btn_style=(f"QPushButton{{background:rgba(0,200,255,10);color:{CYAN};"
                   f"border:1px solid rgba(0,200,255,30);border-radius:4px;font-size:11px;}}"
                   f"QPushButton:hover{{background:rgba(0,200,255,28);}}"
                   f"QPushButton:pressed{{background:rgba(0,200,255,50);}}")
        btn_row=QHBoxLayout(); btn_row.setSpacing(2); self._play_btn=None
        for icon,tip,fn in [("⏮","Prev",self.prev_track),("⏪","Rew",self._rew),
                             ("▶","Play",self.toggle_play),("⏩","Fwd",self._ffw),
                             ("⏭","Next",self.next_track),("⏹","Stop",self._player.stop),
                             ("🔀","Shuffle",self._shuffle),("📂","Open",self._open_file)]:
            b=QPushButton(icon); b.setFixedSize(32,26); b.setToolTip(tip)
            b.setStyleSheet(btn_style); b.clicked.connect(fn); btn_row.addWidget(b)
            if tip=="Play": self._play_btn=b
        lay.addLayout(btn_row)
        vol_row=QHBoxLayout()
        vol_lbl=QLabel("🔊"); vol_lbl.setStyleSheet(f"color:{CYAN};")
        vol_row.addWidget(vol_lbl)
        self.vol_sl=QSlider(Qt.Horizontal); self.vol_sl.setRange(0,100); self.vol_sl.setValue(80)
        self.vol_sl.setStyleSheet(self.seek.styleSheet())
        self.vol_sl.valueChanged.connect(self._player.setVolume)
        self._player.setVolume(80); vol_row.addWidget(self.vol_sl); lay.addLayout(vol_row)

    def load_and_play(self,path):
        if not os.path.isfile(path): return f"Media file not found: {path}"
        self._current=path
        self._player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(path))))
        self._player.play(); self.track_lbl.setText(f"♪  {os.path.basename(path)[:40]}")
        return f"Playing: {os.path.basename(path)}, sir."

    def load_playlist(self,paths):
        self._playlist=[p for p in paths if os.path.isfile(p)]; self._pl_idx=0
        if self._playlist: return self.load_and_play(self._playlist[0])
        return "No valid media files found, sir."

    def toggle_play(self):
        if self._player.state()==QMediaPlayer.PlayingState: self._player.pause()
        else: self._player.play()

    def next_track(self):
        if self._playlist:
            self._pl_idx=(self._pl_idx+1)%len(self._playlist)
            self.load_and_play(self._playlist[self._pl_idx])

    def prev_track(self):
        if self._playlist:
            self._pl_idx=(self._pl_idx-1)%len(self._playlist)
            self.load_and_play(self._playlist[self._pl_idx])

    def _shuffle(self):
        if self._playlist: random.shuffle(self._playlist); self.load_and_play(self._playlist[0])

    def _rew(self): self._player.setPosition(max(0,self._player.position()-10000))
    def _ffw(self): self._player.setPosition(min(self._player.duration(),self._player.position()+10000))

    def _open_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Open Media",os.path.expanduser("~"),
            "Media Files (*.mp3 *.mp4 *.wav *.ogg *.flac *.avi *.mkv *.m4a *.aac);;All (*)")
        if path: self.load_and_play(path)

    def _on_state(self,state):
        if self._play_btn:
            self._play_btn.setText("⏸" if state==QMediaPlayer.PlayingState else "▶")

    def _on_pos(self,pos):
        self.seek.setValue(pos)
        self.time_lbl.setText(f"{self._fmt(pos)} / {self._fmt(self._player.duration())}")

    def _on_dur(self,dur): self.seek.setRange(0,dur)
    def _on_media_status(self,status):
        if status==QMediaPlayer.EndOfMedia and self._playlist: self.next_track()

    @staticmethod
    def _fmt(ms): s=ms//1000; return f"{s//60}:{s%60:02d}"


# ══════════════════════════════════════════════════════════════════════════
#  STYLE CONSTANTS
# ══════════════════════════════════════════════════════════════════════════
DIALOG_STYLE = (
    f"QDialog{{background:{BG_DEEP};}}"
    f"QLabel{{color:{CYAN};font-family:Consolas;font-size:10px;}}"
    f"QLineEdit,QTextEdit,QPlainTextEdit{{background:rgba(3,6,18,210);color:#00e8cc;"
    f"border:1px solid rgba(0,200,255,35);border-radius:6px;padding:4px;"
    f"font-family:Consolas;font-size:11px;}}"
    f"QComboBox{{background:rgba(3,6,18,210);color:#00e8cc;"
    f"border:1px solid rgba(0,200,255,35);border-radius:6px;padding:4px;}}"
    f"QCheckBox{{color:#00ccaa;font-family:Consolas;}}"
    f"QTimeEdit,QSpinBox{{background:rgba(3,6,18,210);color:#00e8cc;"
    f"border:1px solid rgba(0,200,255,35);border-radius:6px;padding:4px;}}")

BTN_STYLE = (
    f"QPushButton{{background:rgba(0,180,255,10);color:{CYAN};"
    f"border:1px solid rgba(0,200,255,45);border-radius:7px;"
    f"padding:7px 18px;font-family:Consolas;font-size:10px;}}"
    f"QPushButton:hover{{background:rgba(0,200,255,28);border-color:{BORDER_HI};}}"
    f"QPushButton:pressed{{background:rgba(0,200,255,50);}}")

TAB_STYLE = (f"""
    QTabWidget::pane{{border:1px solid rgba(0,200,255,30);background:rgba(3,6,20,210);}}
    QTabBar::tab{{background:rgba(0,200,255,8);color:#006688;padding:6px 18px;
        border:1px solid rgba(0,200,255,25);border-radius:5px;margin:2px;
        font-family:Consolas;font-size:9px;}}
    QTabBar::tab:selected{{background:rgba(0,200,255,28);color:{CYAN};}}
    QTabBar::tab:hover{{background:rgba(0,200,255,18);}}""")


# ══════════════════════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ══════════════════════════════════════════════════════════════════════════
class SplashScreen(QWidget):
    done = pyqtSignal()
    def __init__(self):
        super().__init__()
        self._launched = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(820, 480)
        self._angle=0.0; self._pulse=0.0; self._alpha=0; self._progress=0
        self._ring_r=[0.0,0.0,0.0]
        self._msgs=[
            "Initialising J.A.R.V.I.S v10.0…",
            "Loading neural core…","Calibrating arc reactor…",
            "Activating robotic TTS engine…","Connecting bilingual STT…",
            "Loading audio systems…","Arming alarm cores…",
            "Mounting file modules…","Email subsystem ready…",
            "Voice recognition calibrating…","All systems online. Welcome, sir.",
        ]
        self._msg_idx=0; self._msg=self._msgs[0]
        ctr=QApplication.primaryScreen().availableGeometry().center()
        self.move(ctr.x()-410, ctr.y()-240)
        QTimer(self,timeout=self._tick,interval=16).start()
        QTimer(self,timeout=self._advance,interval=340).start()

    def _tick(self):
        self._angle=(self._angle+2.5)%360; self._pulse+=0.07
        self._alpha=min(255,self._alpha+8)
        for i in range(len(self._ring_r)):
            self._ring_r[i]=min(240,self._ring_r[i]+1.1+i*.3)
        self.update()

    def _advance(self):
        self._progress=min(100,self._progress+10)
        if self._msg_idx<len(self._msgs):
            self._msg=self._msgs[self._msg_idx]; self._msg_idx+=1
        if self._progress>=100: QTimer.singleShot(600,self._finish)

    def _finish(self):
        if self._launched: return
        self._launched=True; self.done.emit(); self.close()

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setOpacity(self._alpha/255.0)
        path=QPainterPath(); path.addRoundedRect(QRectF(0,0,820,480),24,24)
        bg=QLinearGradient(0,0,820,480)
        bg.setColorAt(0,QColor(2,5,18,255)); bg.setColorAt(1,QColor(4,12,32,255))
        p.fillPath(path,QBrush(bg))
        p.setPen(QPen(QColor(0,180,255,90),1.5)); p.drawRoundedRect(1,1,818,478,24,24)
        cx,cy=410,195
        for i, r in enumerate(self._ring_r):
            a=max(0,int(28*(1-r/240)))
            p.setPen(QPen(QColor(0,180,255,a),1.0)); p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx,cy),int(r),int(r))
        for i in range(4):
            a=max(0,25-i*5)
            p.setPen(QPen(QColor(0,180,255,a),4-i)); p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPoint(cx,cy),100+i*10,100+i*10)
        p.save(); p.translate(cx,cy); p.rotate(self._angle)
        for i in range(6):
            a1=math.radians(i*60); a2=math.radians(i*60+52)
            ri,ro=70,92
            pts=[QPointF(math.cos(a1)*ri,math.sin(a1)*ri),
                 QPointF(math.cos(a1)*ro,math.sin(a1)*ro),
                 QPointF(math.cos(a2)*ro,math.sin(a2)*ro),
                 QPointF(math.cos(a2)*ri,math.sin(a2)*ri)]
            al=int(100+60*math.sin(self._pulse+i))
            p.setBrush(QBrush(QColor(0,150,255,al))); p.setPen(QPen(QColor(0,220,255,130),1.2))
            p.drawPolygon(QPolygonF(pts))
        p.restore()
        g=QRadialGradient(cx,cy,50)
        pv=0.75+0.25*math.sin(self._pulse*2)
        g.setColorAt(0.0,QColor(220,248,255,int(240*pv)))
        g.setColorAt(0.4,QColor(0,200,255,int(200*pv)))
        g.setColorAt(1.0,QColor(0,40,90,20))
        p.setBrush(QBrush(g)); p.setPen(QPen(QColor(0,220,255,200),2)); p.drawEllipse(QPoint(cx,cy),50,50)
        f=QFont("Consolas",34,QFont.Bold); f.setLetterSpacing(QFont.AbsoluteSpacing,16)
        p.setFont(f); p.setPen(QColor(0,230,255))
        p.drawText(QRect(0,308,820,58),Qt.AlignCenter,"J.A.R.V.I.S")
        p.setFont(QFont("Consolas",9)); p.setPen(QColor(0,100,140))
        p.drawText(QRect(0,368,820,20),Qt.AlignCenter,
                   "Just A Rather Very Intelligent System  ·  v10.0  ·  Ultra Pro Edition")
        bx,by,bw,bh=100,396,620,7
        p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor(0,45,75))); p.drawRoundedRect(bx,by,bw,bh,3,3)
        fill=int(bw*self._progress/100)
        grad=QLinearGradient(bx,0,bx+bw,0)
        grad.setColorAt(0.0,QColor(0,150,255)); grad.setColorAt(1.0,QColor(0,255,180))
        p.setBrush(QBrush(grad)); p.drawRoundedRect(bx,by,fill,bh,3,3)
        if fill>4:
            p.setBrush(QBrush(QColor(0,255,200,180))); p.drawEllipse(bx+fill-4,by-3,8,13)
        p.setPen(QColor(0,140,160)); p.setFont(QFont("Consolas",9))
        p.drawText(QRect(0,410,820,18),Qt.AlignCenter,self._msg)
        p.setPen(QColor(15,55,75)); p.setFont(QFont("Consolas",8))
        p.drawText(QRect(0,432,820,18),Qt.AlignCenter,
                   "Developed by  Amina Sikandar  |  Hamna Rubab  |  Eesha Jewan")
        p.setPen(QColor(10,40,60)); p.setFont(QFont("Consolas",8))
        p.drawText(QRect(730,460,80,14),Qt.AlignRight,f"{self._progress}%")


# ══════════════════════════════════════════════════════════════════════════
#  DIALOGS
# ══════════════════════════════════════════════════════════════════════════
class EmailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S — Send Email")
        self.setMinimumSize(500,400); self.setStyleSheet(DIALOG_STYLE)
        lay=QVBoxLayout(self)
        lay.addWidget(QLabel("To:"))
        self.to_edit=QLineEdit(); self.to_edit.setPlaceholderText("recipient@email.com"); lay.addWidget(self.to_edit)
        lay.addWidget(QLabel("Subject:"))
        self.subj_edit=QLineEdit(); self.subj_edit.setPlaceholderText("Email subject…"); lay.addWidget(self.subj_edit)
        lay.addWidget(QLabel("Message:"))
        self.body_edit=QTextEdit(); self.body_edit.setPlaceholderText("Compose your message…"); lay.addWidget(self.body_edit)
        self.status=QLabel(""); lay.addWidget(self.status)
        btn_row=QHBoxLayout()
        for label,fn in [("📧 Send",self._send),("Close",self.accept)]:
            b=QPushButton(label); b.setStyleSheet(BTN_STYLE); b.clicked.connect(fn); btn_row.addWidget(b)
        lay.addLayout(btn_row)

    def _send(self):
        result=send_email(self.to_edit.text(),self.subj_edit.text(),self.body_edit.toPlainText())
        self.status.setText(result)


class NotesDialog(QDialog):
    def __init__(self,mem,parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S — Notes & Memory")
        self.setMinimumSize(600,480); self.setStyleSheet(DIALOG_STYLE)
        lay=QVBoxLayout(self)
        tabs=QTabWidget(); tabs.setStyleSheet(TAB_STYLE)
        nt=QWidget(); nl=QVBoxLayout(nt)
        self.nb=QTextEdit(readOnly=True)
        self.nb.setStyleSheet("background:rgba(3,6,18,210);color:#88ddaa;font-size:12px;"
                              "border:1px solid rgba(0,200,255,18);border-radius:6px;")
        self.nb.setPlainText(mem.get_notes()); nl.addWidget(self.nb)
        add_row=QHBoxLayout()
        self.note_inp=QLineEdit(); self.note_inp.setPlaceholderText("Add note…")
        btn_add=QPushButton("➕ Add"); btn_add.setStyleSheet(BTN_STYLE)
        btn_add.clicked.connect(lambda:(mem.add_note(self.note_inp.text()),
            self.nb.setPlainText(mem.get_notes()),self.note_inp.clear()))
        add_row.addWidget(self.note_inp); add_row.addWidget(btn_add); nl.addLayout(add_row)
        btn_cl=QPushButton("🗑 Clear All"); btn_cl.setStyleSheet(BTN_STYLE)
        btn_cl.clicked.connect(lambda:(mem.delete_note(),self.nb.setPlainText("Cleared.")))
        nl.addWidget(btn_cl); tabs.addTab(nt,"📝 Notes")
        mt=QWidget(); ml=QVBoxLayout(mt)
        self.mb=QTextEdit(readOnly=True)
        self.mb.setStyleSheet("background:rgba(3,6,18,210);color:#aaaaff;font-size:12px;"
                              "border:1px solid rgba(160,80,255,18);border-radius:6px;")
        self.mb.setPlainText(mem.all_memory()); ml.addWidget(self.mb)
        mem_row=QHBoxLayout()
        self.mk=QLineEdit(); self.mk.setPlaceholderText("Key…")
        self.mv=QLineEdit(); self.mv.setPlaceholderText("Value…")
        btn_m=QPushButton("💾 Store"); btn_m.setStyleSheet(BTN_STYLE)
        btn_m.clicked.connect(lambda:(mem.remember(self.mk.text(),self.mv.text()),
            self.mb.setPlainText(mem.all_memory()),self.mk.clear(),self.mv.clear()))
        mem_row.addWidget(self.mk); mem_row.addWidget(self.mv); mem_row.addWidget(btn_m)
        ml.addLayout(mem_row); tabs.addTab(mt,"🧠 Memory")
        lay.addWidget(tabs)
        ok=QPushButton("Close"); ok.setStyleSheet(BTN_STYLE); ok.clicked.connect(self.accept)
        lay.addWidget(ok,alignment=Qt.AlignRight)


class AlarmDialog(QDialog):
    def __init__(self,alarm_store,reminder_store,parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S — Alarms & Reminders")
        self.setMinimumSize(540,440); self.setStyleSheet(DIALOG_STYLE)
        self.alarms=alarm_store; self.reminders=reminder_store
        lay=QVBoxLayout(self)
        lay.addWidget(self._lbl("⏰  SET NEW ALARM"))
        row1=QHBoxLayout()
        self.alarm_label=QLineEdit(); self.alarm_label.setPlaceholderText("Label…")
        self.alarm_time=QTimeEdit(QTime.currentTime().addSecs(300))
        self.alarm_repeat=QCheckBox("Daily")
        btn_add=QPushButton("➕ Add"); btn_add.setStyleSheet(BTN_STYLE)
        btn_add.clicked.connect(self._add_alarm)
        for w in (self.alarm_label,self.alarm_time,self.alarm_repeat,btn_add): row1.addWidget(w)
        lay.addLayout(row1)
        lay.addWidget(self._lbl("⏰  ACTIVE ALARMS"))
        self.alarm_box=QTextEdit(readOnly=True)
        self.alarm_box.setStyleSheet("background:rgba(3,6,18,210);color:#ffcc00;font-size:11px;"
                                     "border:1px solid rgba(255,200,0,22);border-radius:6px;")
        self.alarm_box.setPlainText(self.alarms.list_alarms()); lay.addWidget(self.alarm_box)
        lay.addWidget(self._lbl("⏱  REMINDER"))
        row2=QHBoxLayout()
        self.rem_text=QLineEdit(); self.rem_text.setPlaceholderText("Reminder text…")
        self.rem_mins=QSpinBox(); self.rem_mins.setRange(1,9999); self.rem_mins.setValue(15); self.rem_mins.setSuffix(" min")
        btn_rem=QPushButton("⏱ Add"); btn_rem.setStyleSheet(BTN_STYLE); btn_rem.clicked.connect(self._add_reminder)
        for w in (self.rem_text,self.rem_mins,btn_rem): row2.addWidget(w)
        lay.addLayout(row2)
        btn_row=QHBoxLayout()
        for label,fn in [("🗑 Clear All",lambda:(self.alarms.delete_alarm(),self._refresh())),("Close",self.accept)]:
            b=QPushButton(label); b.setStyleSheet(BTN_STYLE); b.clicked.connect(fn); btn_row.addWidget(b)
        lay.addLayout(btn_row)

    def _lbl(self,t):
        l=QLabel(t); l.setStyleSheet("color:#ffcc00;font:bold 9px Consolas;padding:2px;"); return l

    def _add_alarm(self):
        label=self.alarm_label.text().strip() or "Alarm"
        qt=self.alarm_time.time(); now=datetime.datetime.now()
        when=now.replace(hour=qt.hour(),minute=qt.minute(),second=0,microsecond=0)
        if when<=now: when+=datetime.timedelta(days=1)
        self.alarms.add_alarm(label,when,self.alarm_repeat.isChecked()); self._refresh()

    def _add_reminder(self):
        text=self.rem_text.text().strip()
        if text:
            when=datetime.datetime.now()+datetime.timedelta(minutes=self.rem_mins.value())
            self.reminders.add(text,when); self.rem_text.clear()

    def _refresh(self): self.alarm_box.setPlainText(self.alarms.list_alarms())


class SettingsDialog(QDialog):
    def __init__(self,current_voice,always_on,mic_idx,parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S — Settings")
        self.setMinimumWidth(560); self.setStyleSheet(DIALOG_STYLE)
        lay=QVBoxLayout(self)
        lay.addWidget(QLabel("TTS Voice:"))
        self.voice_combo=QComboBox()
        voices=["onyx (deep robotic male — RECOMMENDED)","echo (male)","alloy (neutral)",
                "fable (expressive)","nova (female)","shimmer (soft female)"]
        self.voice_combo.addItems(voices)
        for i,v in enumerate(voices):
            if current_voice in v: self.voice_combo.setCurrentIndex(i); break
        lay.addWidget(self.voice_combo)
        lay.addWidget(QLabel("\nVoice Mode:"))
        self.always_on_cb=QCheckBox("Always-On Mode (no wake word required)")
        self.always_on_cb.setChecked(always_on); lay.addWidget(self.always_on_cb)
        lay.addWidget(QLabel("\nMicrophone:"))
        self.mic_combo=QComboBox(); self.mic_combo.addItem("Default Microphone",None)
        if SR_OK:
            try:
                for i,name in enumerate(sr.Microphone.list_microphone_names()):
                    self.mic_combo.addItem(f"[{i}] {name}",i)
                    if mic_idx is not None and i==mic_idx: self.mic_combo.setCurrentIndex(i+1)
            except: pass
        lay.addWidget(self.mic_combo)
        lay.addWidget(QLabel("\nOpenAI API Key:"))
        self.oai_key=QLineEdit(); self.oai_key.setEchoMode(QLineEdit.Password)
        self.oai_key.setPlaceholderText("sk-…"); self.oai_key.setText(OPENAI_API_KEY); lay.addWidget(self.oai_key)
        lay.addWidget(QLabel("\nAnthropic API Key:"))
        self.ant_key=QLineEdit(); self.ant_key.setEchoMode(QLineEdit.Password)
        self.ant_key.setPlaceholderText("sk-ant-…"); self.ant_key.setText(ANTHROPIC_API_KEY); lay.addWidget(self.ant_key)
        lay.addWidget(QLabel("\nGmail:"))
        row=QHBoxLayout()
        self.g_user=QLineEdit(); self.g_user.setPlaceholderText("your@gmail.com"); self.g_user.setText(GMAIL_USER)
        self.g_pass=QLineEdit(); self.g_pass.setEchoMode(QLineEdit.Password)
        self.g_pass.setPlaceholderText("App password"); self.g_pass.setText(GMAIL_PASS)
        row.addWidget(self.g_user); row.addWidget(self.g_pass); lay.addLayout(row)
        btn=QPushButton("✅  Save & Apply"); btn.setStyleSheet(BTN_STYLE)
        btn.clicked.connect(self.accept); lay.addWidget(btn)
        self.selected_voice=current_voice; self.selected_always_on=always_on
        self.selected_mic_idx=mic_idx

    def accept(self):
        global TTS_VOICE,OPENAI_API_KEY,ANTHROPIC_API_KEY,AI_ENGINE,USE_OPENAI_TTS,GMAIL_USER,GMAIL_PASS
        TTS_VOICE=self.voice_combo.currentText().split()[0]
        self.selected_voice=TTS_VOICE; self.selected_always_on=self.always_on_cb.isChecked()
        self.selected_mic_idx=self.mic_combo.currentData()
        nk=self.oai_key.text().strip()
        if nk: OPENAI_API_KEY=nk
        ak=self.ant_key.text().strip()
        if ak: ANTHROPIC_API_KEY=ak
        gu=self.g_user.text().strip()
        if gu: GMAIL_USER=gu
        gp=self.g_pass.text().strip()
        if gp: GMAIL_PASS=gp
        AI_ENGINE=("openai" if (OPENAI_OK and OPENAI_API_KEY) else
                   "claude" if (CLAUDE_OK and ANTHROPIC_API_KEY) else "none")
        USE_OPENAI_TTS=OPENAI_OK and bool(OPENAI_API_KEY) and PYGAME_OK
        super().accept()


class TextEditorDialog(QDialog):
    def __init__(self,filename="",content="",parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"J.A.R.V.I.S — Editor: {filename or 'New File'}")
        self.setMinimumSize(760,560); self.setStyleSheet(DIALOG_STYLE)
        lay=QVBoxLayout(self)
        top=QHBoxLayout(); top.addWidget(QLabel("File:"))
        self.name_edit=QLineEdit(filename); top.addWidget(self.name_edit); lay.addLayout(top)
        self.editor=QTextEdit(); self.editor.setPlainText(content)
        self.editor.setStyleSheet(
            f"background:{BG_DEEP};color:#00e8cc;font-family:Consolas;font-size:12px;"
            f"border:1px solid {BORDER};border-radius:8px;padding:8px;")
        lay.addWidget(self.editor)
        btn_row=QHBoxLayout()
        for label,fn in [("💾 Save",self._save),("📋 Copy",self._copy),("🗑 Clear",self._clear),("Close",self.reject)]:
            b=QPushButton(label); b.setStyleSheet(BTN_STYLE); b.clicked.connect(fn)
            btn_row.addWidget(b)
        lay.addLayout(btn_row); self.result_msg=""

    def _save(self):
        fname=self.name_edit.text().strip() or "jarvis_file.txt"
        self.result_msg=create_file_doc(fname,self.editor.toPlainText())
        QMessageBox.information(self,"Saved",self.result_msg); self.accept()
    def _copy(self): QApplication.clipboard().setText(self.editor.toPlainText())
    def _clear(self): self.editor.clear()


class FileManagerDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S — File Manager")
        self.setMinimumSize(720,540); self.setStyleSheet(DIALOG_STYLE)
        lay=QVBoxLayout(self)
        self.fs_model=QFileSystemModel()
        self.fs_model.setRootPath(os.path.expanduser("~"))
        self.tree=QTreeView(); self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(os.path.expanduser("~")))
        self.tree.setStyleSheet(
            f"QTreeView{{background:{BG_DEEP};color:#b0c8d8;border:1px solid {BORDER};"
            f"border-radius:8px;font-size:11px;}}"
            "QTreeView::item:hover{background:rgba(0,180,255,14);}"
            "QTreeView::item:selected{background:rgba(0,180,255,35);}"
            "QHeaderView::section{background:rgba(0,20,50,180);color:#00d4ff;"
            "border:none;font-size:10px;padding:4px;}")
        self.tree.doubleClicked.connect(self._open_item); lay.addWidget(self.tree)
        btn_row=QHBoxLayout()
        for label,slot in [("📂 Open",self._open_selected),("✏ Rename",self._rename_selected),
                           ("🗑 Delete",self._delete_selected),("📁 New Folder",self._new_folder),("Close",self.accept)]:
            b=QPushButton(label); b.setStyleSheet(BTN_STYLE); b.clicked.connect(slot)
            btn_row.addWidget(b)
        lay.addLayout(btn_row)

    def _open_item(self,index):
        path=self.fs_model.filePath(index)
        if os.path.isfile(path): open_path(path)

    def _open_selected(self):
        idx=self.tree.currentIndex()
        if idx.isValid(): open_path(self.fs_model.filePath(idx))

    def _delete_selected(self):
        idx=self.tree.currentIndex()
        if not idx.isValid(): return
        path=self.fs_model.filePath(idx)
        if QMessageBox.question(self,"Confirm",f"Delete {os.path.basename(path)}?",
                                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            try:
                if os.path.isfile(path): os.remove(path)
                elif os.path.isdir(path): shutil.rmtree(path)
            except Exception as e: QMessageBox.warning(self,"Error",str(e))

    def _rename_selected(self):
        idx=self.tree.currentIndex()
        if not idx.isValid(): return
        path=self.fs_model.filePath(idx)
        new_name,ok=QInputDialog.getText(self,"Rename","New name:",text=os.path.basename(path))
        if ok and new_name:
            try: os.rename(path,os.path.join(os.path.dirname(path),new_name))
            except Exception as e: QMessageBox.warning(self,"Error",str(e))

    def _new_folder(self):
        name,ok=QInputDialog.getText(self,"New Folder","Folder name:")
        if ok and name:
            idx=self.tree.currentIndex()
            base=(self.fs_model.filePath(idx) if idx.isValid() and
                  os.path.isdir(self.fs_model.filePath(idx)) else os.path.expanduser("~"))
            try: os.makedirs(os.path.join(base,name),exist_ok=True)
            except Exception as e: QMessageBox.warning(self,"Error",str(e))


# ══════════════════════════════════════════════════════════════════════════
#  CHAT AREA
# ══════════════════════════════════════════════════════════════════════════
class ChatBubble(QFrame):
    def __init__(self, role, text, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        lay=QHBoxLayout(self); lay.setContentsMargins(6,2,6,2)
        is_user=(role=="user")
        if is_user: lay.addStretch()
        lbl=QLabel(html.escape(text))
        lbl.setWordWrap(True); lbl.setMaximumWidth(560)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if is_user:
            lbl.setStyleSheet(
                "background:rgba(0,100,180,55);color:#b8e8ff;"
                "border:1px solid rgba(0,160,255,50);border-radius:12px 12px 2px 12px;"
                "padding:9px 14px;font-family:Consolas;font-size:12px;")
        else:
            lbl.setStyleSheet(
                "background:rgba(0,20,60,140);color:#00eedd;"
                "border:1px solid rgba(0,210,255,30);border-radius:12px 12px 12px 2px;"
                "padding:9px 14px;font-family:Consolas;font-size:12px;")
        lay.addWidget(lbl)
        if not is_user: lay.addStretch()


class ChatArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{width:4px;background:transparent;}"
            "QScrollBar::handle:vertical{background:rgba(0,180,255,45);border-radius:2px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        self._container=QWidget(); self._container.setStyleSheet("background:transparent;")
        self._layout=QVBoxLayout(self._container)
        self._layout.setSpacing(4); self._layout.setContentsMargins(6,10,6,10)
        self._layout.addStretch(); self.setWidget(self._container)

    def add_message(self, role, text):
        bubble=ChatBubble(role,text)
        self._layout.insertWidget(self._layout.count()-1,bubble)
        QTimer.singleShot(50,lambda:self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()))

    def add_system(self, text):
        lbl=QLabel(text); lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color:{CYAN_DIM};font-family:Consolas;font-size:9px;"
                          f"padding:4px;background:rgba(0,50,100,18);border-radius:4px;")
        self._layout.insertWidget(self._layout.count()-1,lbl)


# ══════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
class Dashboard(QWidget):
    _sig_log  = pyqtSignal(str)
    _sig_live = pyqtSignal(str)
    _sig_cmd  = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(1440, 900)
        self.setWindowTitle("J.A.R.V.I.S  v10.0  —  Ultra Pro AI Desktop Assistant  |  FYP")
        self.setStyleSheet(f"background:{BG_DEEP};")

        self._chat_history    = []
        self._active_workers  = []
        self._last_net        = psutil.net_io_counters()
        self._tick_count      = 0
        self._voice_active    = True
        self._always_on_voice = False
        self._tts_busy        = False
        self._mic_device_idx  = None
        self._power_val       = 100

        self.mem       = MemoryStore()
        self.reminders = ReminderStore(self)
        self.alarms    = AlarmStore(self)
        self.reminders.fired.connect(self._on_reminder)
        self.alarms.alarm_fired.connect(self._on_alarm)
        self._sig_log .connect(self._do_log)
        self._sig_live.connect(self._do_live_status)
        self._sig_cmd .connect(self.execute_command)

        self.tts = TTSWorker(self)
        self.tts.log_msg .connect(self._do_log)
        self.tts.finished.connect(self._on_tts_done)
        self.tts.start()

        self._build_ui()
        self._start_voice()
        SoundFX.boot()

        QTimer.singleShot(2000, lambda: self._say(
            "JARVIS version 10 ultra pro online. "
            "All systems nominal. Arc reactor at maximum capacity. "
            "Say Jarvis followed by your command"))

    # ─── BUILD UI ──────────────────────────────────────────────────────────
    def _build_ui(self):
        self.hex_bg = HexBackground(self)
        self.hex_bg.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hex_bg.lower()

        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ════ LEFT PANEL ════
        left_panel = QFrame()
        left_panel.setFixedWidth(262)
        left_panel.setStyleSheet(f"QFrame{{background:rgba(2,8,22,230);border-right:1px solid rgba(0,180,255,30);}}")
        lp = QVBoxLayout(left_panel)
        lp.setContentsMargins(8,10,8,8); lp.setSpacing(5)

        brand_row = QHBoxLayout(); brand_row.setContentsMargins(0,0,0,0)
        brand_row.addWidget(HUDCorner("tl",24))
        brand_lbl = QLabel("J.A.R.V.I.S")
        brand_lbl.setFont(QFont("Consolas",14,QFont.Bold))
        brand_lbl.setStyleSheet(f"color:{CYAN_GLOW};letter-spacing:5px;background:transparent;")
        brand_lbl.setAlignment(Qt.AlignCenter); brand_row.addWidget(brand_lbl)
        brand_row.addWidget(HUDCorner("tr",24)); lp.addLayout(brand_row)

        ver_lbl = QLabel("ULTRA PRO  v10.0  — AI DESKTOP ASSISTANT")
        ver_lbl.setStyleSheet(f"color:{CYAN_DIM};font:7px Consolas;background:transparent;")
        ver_lbl.setAlignment(Qt.AlignCenter); lp.addWidget(ver_lbl)
        lp.addWidget(self._div())

        arc_row = QHBoxLayout(); arc_row.setAlignment(Qt.AlignCenter)
        self.arc = ArcReactor(110); arc_row.addWidget(self.arc); lp.addLayout(arc_row)

        ai_color = GREEN if AI_ENGINE != "none" else RED_HUD
        ai_badge = QLabel(f"⚡  AI ENGINE: {AI_ENGINE.upper()}")
        ai_badge.setAlignment(Qt.AlignCenter)
        ai_badge.setStyleSheet(f"color:{ai_color};font:bold 8px Consolas;background:rgba(0,255,80,8);"
                               f"border:1px solid rgba(0,255,80,25);border-radius:4px;padding:3px;")
        lp.addWidget(ai_badge)
        lp.addWidget(self._div())

        gauges_row = QHBoxLayout(); gauges_row.setSpacing(2)
        self.cpu_gauge  = CircularGauge("CPU",  (0,210,255), 78)
        self.ram_gauge  = CircularGauge("RAM",  (255,150,0), 78)
        self.disk_gauge = CircularGauge("DISK", (0,255,120), 78)
        for g in (self.cpu_gauge, self.ram_gauge, self.disk_gauge): gauges_row.addWidget(g)
        lp.addLayout(gauges_row)

        self.cpu_bar  = PowerBar("CPU LOAD",  (0,210,255))
        self.ram_bar  = PowerBar("RAM USAGE", (255,150,0))
        self.net_bar  = PowerBar("NETWORK",   (0,255,180))
        for b in (self.cpu_bar, self.ram_bar, self.net_bar): lp.addWidget(b)
        lp.addWidget(self._div())

        net_hdr = QLabel("◈  NETWORK I/O")
        net_hdr.setStyleSheet(f"color:{CYAN_DIM};font:7px Consolas;background:transparent;")
        net_hdr.setAlignment(Qt.AlignCenter); lp.addWidget(net_hdr)
        self.net_wave = NetWave(); lp.addWidget(self.net_wave)
        self.net_lbl = QLabel("↑0  ↓0 KB/s")
        self.net_lbl.setStyleSheet(f"color:{CYAN_DIM};font:7px Consolas;background:transparent;")
        self.net_lbl.setAlignment(Qt.AlignCenter); lp.addWidget(self.net_lbl)
        lp.addWidget(self._div())

        scan_row = QHBoxLayout(); scan_row.setSpacing(4)
        scan_row.addWidget(RadarWidget(110,"RADAR"))
        scan_row.addWidget(RadarWidget(110,"THREAT"))
        lp.addLayout(scan_row)
        lp.addWidget(self._div())

        tools = [
            ("⚙","Settings",self._open_settings),
            ("📝","Notes",self._open_notes),
            ("📁","Files",lambda:FileManagerDialog(self).exec_()),
            ("✏","Editor",self._open_editor),
            ("⏰","Alarms",self._open_alarms),
            ("📧","Email",lambda:EmailDialog(self).exec_()),
            ("🎵","Media",self._focus_media_tab),
            ("🔊","Toggle Mic",self._toggle_voice),
            ("⏹","Stop TTS",self._stop_speaking),
            ("🗑","Clear Chat",self._clear_chat),
            ("🖥","System",lambda:self.tabs.setCurrentIndex(2)),
            ("🔒","Lock",lambda:self._deliver(lock_system())),
        ]
        tgrid = QGridLayout(); tgrid.setSpacing(2)
        for i,(ico,tip,fn) in enumerate(tools):
            b=QPushButton(ico); b.setFixedSize(38,28); b.setToolTip(tip)
            b.setStyleSheet(
                f"QPushButton{{background:rgba(0,180,255,8);color:{CYAN};"
                f"border:1px solid rgba(0,180,255,25);border-radius:4px;font-size:11px;}}"
                f"QPushButton:hover{{background:rgba(0,180,255,28);border-color:rgba(0,240,255,90);}}"
                f"QPushButton:pressed{{background:rgba(0,180,255,55);}}")
            b.clicked.connect(fn); tgrid.addWidget(b,i//4,i%4)
        lp.addLayout(tgrid)
        lp.addWidget(self._div())

        log_lbl = QLabel("◈  SYSTEM LOG")
        log_lbl.setStyleSheet(f"color:{CYAN_DIM};font:7px Consolas;background:transparent;")
        log_lbl.setAlignment(Qt.AlignCenter); lp.addWidget(log_lbl)
        self.console = QTextEdit(readOnly=True)
        self.console.setStyleSheet(
            f"QTextEdit{{background:rgba(3,8,20,200);color:{CYAN};font-family:Consolas;"
            f"font-size:8px;border:1px solid rgba(0,180,255,20);border-radius:4px;}}"
            "QScrollBar:vertical{width:3px;background:transparent;}"
            "QScrollBar::handle:vertical{background:rgba(0,180,255,45);border-radius:1px;}")
        self.console.append(f'<span style="color:{GREEN}">▶ J.A.R.V.I.S v10 BOOT</span>')
        self.console.append(f'<span style="color:{PURPLE}">▶ Amina | Hamna | Eesha</span>')
        lp.addWidget(self.console)

        cred_lbl = QLabel("Amina Sikandar  |  Hamna Rubab  |  Eesha Jewan")
        cred_lbl.setAlignment(Qt.AlignCenter)
        cred_lbl.setStyleSheet(f"color:rgba(0,120,160,160);font:7px Consolas;padding:2px;background:transparent;")
        lp.addWidget(cred_lbl)
        root.addWidget(left_panel)

        # ════ CENTER PANEL ════
        center_panel = QFrame()
        center_panel.setStyleSheet("QFrame{background:transparent;}")
        cp = QVBoxLayout(center_panel)
        cp.setContentsMargins(0,0,0,0); cp.setSpacing(0)

        top_bar = QFrame(); top_bar.setFixedHeight(56)
        top_bar.setStyleSheet(f"QFrame{{background:rgba(2,8,22,230);border-bottom:1px solid rgba(0,180,255,30);}}")
        tbl = QHBoxLayout(top_bar); tbl.setContentsMargins(14,0,14,0); tbl.setSpacing(10)
        tbl.addWidget(HUDCorner("tl",26))
        self.time_lbl = QLabel("--:--:--")
        self.time_lbl.setFont(QFont("Consolas",20,QFont.Bold))
        self.time_lbl.setStyleSheet(f"color:{CYAN_GLOW};letter-spacing:3px;background:transparent;")
        tbl.addWidget(self.time_lbl)
        self.date_lbl = QLabel("")
        self.date_lbl.setStyleSheet(f"color:{CYAN_DIM};font:10px Consolas;background:transparent;")
        tbl.addWidget(self.date_lbl)
        tbl.addStretch()
        title_c = QLabel("J.A.R.V.I.S  —  ULTRA PRO AI ASSISTANT")
        title_c.setStyleSheet(f"color:{CYAN};font:bold 12px Consolas;letter-spacing:4px;background:transparent;")
        title_c.setAlignment(Qt.AlignCenter); tbl.addWidget(title_c)
        tbl.addStretch()
        self.status_lbl = QLabel("◎  Awaiting your command, sir…")
        self.status_lbl.setStyleSheet(f"color:{GREEN};font:bold 9px Consolas;background:transparent;")
        tbl.addWidget(self.status_lbl)
        for ico,tip,fn in [("🔊","Voice",self._toggle_voice),
                           ("⏹","Stop",self._stop_speaking),
                           ("⚙","Settings",self._open_settings)]:
            b=QPushButton(ico); b.setFixedSize(36,34); b.setToolTip(tip)
            b.setStyleSheet(f"QPushButton{{background:transparent;color:{CYAN};"
                            f"border:1px solid rgba(0,180,255,30);border-radius:6px;font-size:13px;}}"
                            f"QPushButton:hover{{background:rgba(0,180,255,22);}}")
            b.clicked.connect(fn); tbl.addWidget(b)
        tbl.addWidget(HUDCorner("tr",26)); cp.addWidget(top_bar)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane{{border:none;background:transparent;}}
            QTabBar::tab{{background:rgba(0,30,70,180);color:{CYAN_DIM};
                padding:9px 24px;border:1px solid rgba(0,180,255,25);
                border-bottom:none;border-radius:6px 6px 0 0;
                margin-right:2px;font-family:Consolas;font-size:10px;}}
            QTabBar::tab:selected{{background:rgba(0,60,120,200);color:{CYAN_GLOW};
                border-bottom:2px solid {CYAN_GLOW};}}
            QTabBar::tab:hover{{background:rgba(0,50,100,180);}}""")

        # ── CHAT TAB ──
        chat_tab = QWidget(); chat_tab.setStyleSheet("background:transparent;")
        chat_lay = QVBoxLayout(chat_tab)
        chat_lay.setContentsMargins(0,0,0,0); chat_lay.setSpacing(0)

        main_row = QHBoxLayout(); main_row.setSpacing(0)
        self.chat_area = ChatArea()
        self.chat_area.add_system("◈  J.A.R.V.I.S v10.0  —  Ultra Pro Mode  —  All Systems Online")
        main_row.addWidget(self.chat_area, 3)

        center_col = QFrame(); center_col.setFixedWidth(296)
        center_col.setStyleSheet("QFrame{background:transparent;}")
        ccl = QVBoxLayout(center_col); ccl.setContentsMargins(4,4,4,4)
        ccl.setAlignment(Qt.AlignCenter); ccl.setSpacing(4)
        ccl.addStretch()
        self.ironman = IronManFigure(280, 400)
        ccl.addWidget(self.ironman, alignment=Qt.AlignCenter)
        self.voice_orb = VoiceOrb(120)
        ccl.addWidget(self.voice_orb, alignment=Qt.AlignCenter)
        self.voice_status_lbl = QLabel("🎤  Say 'Jarvis <command>'")
        self.voice_status_lbl.setAlignment(Qt.AlignCenter)
        self.voice_status_lbl.setWordWrap(True)
        self.voice_status_lbl.setStyleSheet(
            f"color:{GREEN};font:bold 9px Consolas;padding:4px;"
            f"background:rgba(0,255,100,6);border:1px solid rgba(0,255,100,20);border-radius:5px;")
        ccl.addWidget(self.voice_status_lbl)
        self.power_display = QLabel("POWER LEVEL AT 100 PERCENT AND HOLDING STEADY.")
        self.power_display.setAlignment(Qt.AlignCenter); self.power_display.setWordWrap(True)
        self.power_display.setStyleSheet(
            f"color:{GREEN};font:bold 8px Consolas;padding:3px;"
            f"background:rgba(0,255,100,5);border:1px solid rgba(0,255,100,18);border-radius:4px;")
        ccl.addWidget(self.power_display)
        ccl.addStretch()
        main_row.addWidget(center_col, 0)
        chat_lay.addLayout(main_row)

        # Quick ribbon
        ribbon = QFrame()
        ribbon.setStyleSheet(f"QFrame{{background:rgba(2,8,22,220);border-top:1px solid rgba(0,180,255,25);}}")
        rl = QVBoxLayout(ribbon); rl.setContentsMargins(6,3,6,3); rl.setSpacing(2)
        quick_rows = [
            [("🌐 Google","open google"),("▶ YouTube","open youtube"),
             ("📧 Gmail","open gmail"),("💼 LinkedIn","open linkedin"),
             ("📰 News","latest news today"),("🌤 Weather","weather today"),
             ("😄 Joke","tell me a joke"),("💡 Idea","give me a project idea"),
             ("💪 Motivate","motivate me"),("🕐 Time","what time is it")],
            [("💻 Sys Info","system info"),("🔋 Battery","battery status"),
             ("📸 Screenshot","take screenshot"),("📝 Notepad","open notepad"),
             ("🧮 Calc","open calculator"),("⌨ CMD","open cmd"),
             ("🗂 Explorer","open file explorer"),("⏰ Set Alarm","set alarm"),
             ("🎨 DALL-E","generate image of a futuristic iron man city"),
             ("🧠 Memory","what do you remember")],
        ]
        for row_data in quick_rows:
            row_w = QHBoxLayout(); row_w.setSpacing(2)
            for label,cmd in row_data:
                btn = QPushButton(label); btn.setFixedHeight(22)
                btn.setStyleSheet(
                    f"QPushButton{{background:rgba(0,180,255,8);color:{CYAN_DIM};"
                    f"border:1px solid rgba(0,180,255,22);border-radius:4px;"
                    f"font-family:Consolas;font-size:8px;padding:0 4px;}}"
                    f"QPushButton:hover{{background:rgba(0,180,255,25);color:{CYAN};"
                    f"border-color:rgba(0,240,255,80);}}"
                    f"QPushButton:pressed{{background:rgba(0,180,255,50);}}")
                btn.clicked.connect(lambda _,c=cmd:(SoundFX.click(),self.execute_command(c)))
                row_w.addWidget(btn)
            rl.addLayout(row_w)
        chat_lay.addWidget(ribbon)

        # Input bar
        inp_frame = QFrame(); inp_frame.setFixedHeight(62)
        inp_frame.setStyleSheet(f"QFrame{{background:rgba(2,8,22,230);border-top:1px solid rgba(0,180,255,25);}}")
        ifl = QHBoxLayout(inp_frame); ifl.setContentsMargins(10,10,10,10); ifl.setSpacing(5)
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Type command or ask anything in English / Urdu — or just say 'Jarvis…'")
        self.inp.returnPressed.connect(self._on_typed)
        self.inp.setStyleSheet(
            f"QLineEdit{{background:rgba(3,10,30,200);border:1px solid rgba(0,180,255,35);"
            f"color:{CYAN_GLOW};font-size:13px;font-family:Consolas;"
            f"border-radius:10px;padding:7px 14px;}}"
            f"QLineEdit:focus{{border-color:rgba(0,240,255,100);}}")
        ifl.addWidget(self.inp)
        for ico,tip,slot in [("⏎","Send",self._on_typed),
                              ("🎤","Toggle Mic",self._toggle_voice),
                              ("⏹","Stop TTS",self._stop_speaking),
                              ("📧","Email",lambda:EmailDialog(self).exec_()),
                              ("✏","Editor",self._open_editor),
                              ("📝","Notes",self._open_notes)]:
            b = QPushButton(ico); b.setFixedSize(40,40); b.setToolTip(tip)
            b.setStyleSheet(
                f"QPushButton{{background:rgba(0,180,255,10);color:{CYAN};"
                f"border:1px solid rgba(0,180,255,30);border-radius:8px;font-size:13px;}}"
                f"QPushButton:hover{{background:rgba(0,180,255,30);border-color:rgba(0,240,255,90);}}"
                f"QPushButton:pressed{{background:rgba(0,180,255,55);}}")
            b.clicked.connect(slot); ifl.addWidget(b)
        chat_lay.addWidget(inp_frame)
        self.tabs.addTab(chat_tab, "💬  CHAT")

        # ── MEDIA TAB ──
        media_tab = QWidget(); media_tab.setStyleSheet(f"background:{BG_DEEP};")
        ml = QVBoxLayout(media_tab); ml.setContentsMargins(20,16,20,16); ml.setSpacing(10)
        mp_hdr = QLabel("◈  MEDIA PLAYER")
        mp_hdr.setStyleSheet(f"color:{GREEN};font:bold 12px Consolas;")
        mp_hdr.setAlignment(Qt.AlignCenter); ml.addWidget(mp_hdr)
        mp_frame = QFrame()
        mp_frame.setStyleSheet(f"QFrame{{background:rgba(0,20,60,180);border:1px solid rgba(0,255,140,25);border-radius:14px;}}")
        mpfl = QVBoxLayout(mp_frame); mpfl.setContentsMargins(18,18,18,18)
        self.media_player = MediaPlayerWidget(); mpfl.addWidget(self.media_player)
        ml.addWidget(mp_frame); ml.addStretch()
        self.tabs.addTab(media_tab, "🎵  MEDIA")

        # ── SYSTEM TAB ──
        sys_tab = QWidget(); sys_tab.setStyleSheet(f"background:{BG_DEEP};")
        sl = QVBoxLayout(sys_tab); sl.setContentsMargins(10,10,10,10); sl.setSpacing(6)
        sys_hdr = QLabel("◈  SYSTEM STATUS")
        sys_hdr.setStyleSheet(f"color:{CYAN};font:bold 12px Consolas;")
        sys_hdr.setAlignment(Qt.AlignCenter); sl.addWidget(sys_hdr)
        self.sys_box = QTextEdit(readOnly=True)
        self.sys_box.setStyleSheet(
            f"QTextEdit{{background:rgba(0,20,55,200);color:#4a9abb;"
            f"font-family:Consolas;font-size:11px;"
            f"border:1px solid rgba(0,180,255,25);border-radius:8px;padding:8px;}}")
        self.sys_box.setFixedHeight(170); sl.addWidget(self.sys_box)

        # System action buttons
        sys_btn_row = QHBoxLayout()
        for label,cmd in [("Full Info","detailed system info"),("Processes","list processes"),
                          ("Network","network info"),("Disk","disk space info")]:
            b=QPushButton(label); b.setStyleSheet(BTN_STYLE)
            b.clicked.connect(lambda _,c=cmd:self.execute_command(c))
            sys_btn_row.addWidget(b)
        sl.addLayout(sys_btn_row)

        sl.addWidget(QLabel("◈  FILE BROWSER"))
        self.fs_model2 = QFileSystemModel()
        self.fs_model2.setRootPath(os.path.expanduser("~"))
        self.tree2 = QTreeView(); self.tree2.setModel(self.fs_model2)
        self.tree2.setRootIndex(self.fs_model2.index(os.path.expanduser("~")))
        self.tree2.setHeaderHidden(True)
        for c in (1,2,3): self.tree2.hideColumn(c)
        self.tree2.doubleClicked.connect(
            lambda idx: open_path(self.fs_model2.filePath(idx))
            if os.path.isfile(self.fs_model2.filePath(idx)) else None)
        self.tree2.setStyleSheet(
            f"QTreeView{{background:rgba(0,20,55,200);color:#b0c8d8;"
            f"border:1px solid rgba(0,180,255,25);border-radius:8px;font-size:10px;}}"
            "QTreeView::item:hover{background:rgba(0,180,255,14);}"
            "QTreeView::item:selected{background:rgba(0,180,255,35);}"
            "QScrollBar:vertical{width:4px;background:transparent;}"
            "QScrollBar::handle:vertical{background:rgba(0,180,255,45);border-radius:2px;}")
        sl.addWidget(self.tree2)
        self.tabs.addTab(sys_tab, "🖥  SYSTEM")

        cp.addWidget(self.tabs)
        root.addWidget(center_panel)

        # ════ RIGHT PANEL ════
        right_panel = QFrame(); right_panel.setFixedWidth(242)
        right_panel.setStyleSheet(f"QFrame{{background:rgba(2,8,22,230);border-left:1px solid rgba(0,180,255,28);}}")
        rp = QVBoxLayout(right_panel); rp.setContentsMargins(8,10,8,8); rp.setSpacing(5)

        rtop = QHBoxLayout(); rtop.setContentsMargins(0,0,0,0)
        rtop.addWidget(HUDCorner("tl",24))
        rp_lbl = QLabel("SYSTEM")
        rp_lbl.setFont(QFont("Consolas",11,QFont.Bold))
        rp_lbl.setStyleSheet(f"color:{CYAN_GLOW};letter-spacing:4px;background:transparent;")
        rp_lbl.setAlignment(Qt.AlignCenter); rtop.addWidget(rp_lbl)
        rtop.addWidget(HUDCorner("tr",24)); rp.addLayout(rtop)
        rp.addWidget(self._div())

        self.bat_lbl = QLabel("🔋  --")
        self.bat_lbl.setStyleSheet(f"color:{AMBER};font:bold 10px Consolas;"
                                   f"background:rgba(255,180,0,8);border:1px solid rgba(255,180,0,22);"
                                   f"border-radius:4px;padding:4px;")
        self.bat_lbl.setAlignment(Qt.AlignCenter); rp.addWidget(self.bat_lbl)

        self.uptime_lbl = QLabel("⏱  Uptime: --")
        self.uptime_lbl.setStyleSheet(f"color:{CYAN_DIM};font:9px Consolas;background:transparent;")
        self.uptime_lbl.setAlignment(Qt.AlignCenter); rp.addWidget(self.uptime_lbl)

        self.ip_lbl = QLabel("🌐  IP: --")
        self.ip_lbl.setStyleSheet(f"color:{CYAN_DIM};font:9px Consolas;background:transparent;")
        self.ip_lbl.setAlignment(Qt.AlignCenter); rp.addWidget(self.ip_lbl)
        try:
            ip=socket.gethostbyname(socket.gethostname())
            self.ip_lbl.setText(f"🌐  {ip}")
        except: pass

        self.host_lbl = QLabel(f"🖥  {socket.gethostname()}")
        self.host_lbl.setStyleSheet(f"color:{CYAN_DIM};font:9px Consolas;background:transparent;")
        self.host_lbl.setAlignment(Qt.AlignCenter); rp.addWidget(self.host_lbl)
        rp.addWidget(self._div())

        self.days_frame = QFrame()
        self.days_frame.setStyleSheet(
            f"QFrame{{background:rgba(0,200,255,6);border:1px solid rgba(0,200,255,25);border-radius:8px;padding:2px;}}")
        df = QVBoxLayout(self.days_frame); df.setContentsMargins(6,6,6,6); df.setSpacing(2)
        now = datetime.datetime.now()
        year_end = datetime.datetime(now.year,12,31)
        days_left = (year_end-now).days
        for lbl_text, val in [
            ("DAYS LEFT", str(days_left)),
            ("WEEKS LEFT", str(days_left//7)),
            ("MONTHS LEFT", str(12-now.month)),
            (f"IN YEAR", str(now.year)),
        ]:
            row = QHBoxLayout()
            lw = QLabel(lbl_text); lw.setStyleSheet(f"color:{CYAN_DIM};font:7px Consolas;")
            vw = QLabel(val); vw.setStyleSheet(f"color:{CYAN_GLOW};font:bold 11px Consolas;")
            vw.setAlignment(Qt.AlignRight)
            row.addWidget(lw); row.addWidget(vw); df.addLayout(row)
        rp.addWidget(self.days_frame)
        rp.addWidget(self._div())

        radar_row = QHBoxLayout(); radar_row.setAlignment(Qt.AlignCenter)
        radar_row.addWidget(RadarWidget(110,"STATUS")); rp.addLayout(radar_row)
        rp.addWidget(self._div())

        proc_lbl = QLabel("◈  TOP PROCESSES")
        proc_lbl.setStyleSheet(f"color:{CYAN_DIM};font:7px Consolas;background:transparent;")
        proc_lbl.setAlignment(Qt.AlignCenter); rp.addWidget(proc_lbl)
        self.proc_box = QTextEdit(readOnly=True)
        self.proc_box.setStyleSheet(
            f"QTextEdit{{background:rgba(3,8,20,180);color:#5599aa;"
            f"font-family:Consolas;font-size:8px;"
            f"border:1px solid rgba(0,180,255,18);border-radius:4px;}}"
            "QScrollBar:vertical{width:3px;background:transparent;}"
            "QScrollBar::handle:vertical{background:rgba(0,180,255,45);border-radius:1px;}")
        self.proc_box.setFixedHeight(110); rp.addWidget(self.proc_box)
        rp.addWidget(self._div())

        self.voice_status_right = QLabel("🎤  VOICE: INITIALISING…")
        self.voice_status_right.setAlignment(Qt.AlignCenter)
        self.voice_status_right.setWordWrap(True)
        self.voice_status_right.setStyleSheet(
            f"color:{AMBER};font:bold 8px Consolas;padding:4px;"
            f"background:rgba(255,180,0,6);border:1px solid rgba(255,180,0,22);border-radius:4px;")
        rp.addWidget(self.voice_status_right)
        rp.addStretch()

        cred2 = QLabel("AMINA  |  HAMNA  |  EESHA")
        cred2.setAlignment(Qt.AlignCenter)
        cred2.setStyleSheet(f"color:rgba(0,120,160,150);font:7px Consolas;padding:2px;")
        rp.addWidget(cred2)
        root.addWidget(right_panel)

        QTimer(self, timeout=self._update_stats, interval=1000).start()

    def _div(self):
        d=QFrame(); d.setFrameShape(QFrame.HLine)
        d.setStyleSheet("color:rgba(0,180,255,22);margin:1px 4px;"); return d

    # ─── VOICE ENGINE ──────────────────────────────────────────────────────
    def _start_voice(self):
        self.vw = VoiceWorker(self)
        self.vw._mic_device_idx = self._mic_device_idx
        self.vw.set_always_on(self._always_on_voice)
        self.vw.text_received.connect(self._on_voice)
        self.vw.state_changed.connect(self._on_voice_state)
        self.vw.level_changed.connect(self.voice_orb.set_level)
        self.vw.log_msg.connect(self._do_log)
        self.vw.start()
        self._do_log("[VOICE] Mic initialising…")

    def _on_voice_state(self, state):
        self.voice_orb.set_state(state)
        cmap = {
            "listening"   : (GREEN,  "🎤  Listening — speak now, sir"),
            "processing"  : (AMBER,  "⟳  Processing command…"),
            "speaking"    : (CYAN,   "◎  Speaking…"),
            "thinking"    : (PURPLE, "⋯  Thinking…"),
            "calibrating" : (AMBER,  "⊛  Calibrating mic…"),
            "idle"        : (GREEN,  "🎤  Say 'Jarvis <command>'"),
        }
        if state in cmap:
            c, label = cmap[state]
            if state == "idle" and self._always_on_voice:
                label = "🎤  Always-on — speak freely"
            self.voice_status_lbl.setText(label)
            self.voice_status_lbl.setStyleSheet(
                f"color:{c};font:bold 9px Consolas;padding:4px;"
                f"background:rgba(0,255,100,6);border:1px solid rgba(0,255,100,20);border-radius:5px;")
            self.voice_status_right.setText(f"🎤  VOICE: {state.upper()}")
            self.voice_status_right.setStyleSheet(
                f"color:{c};font:bold 8px Consolas;padding:4px;"
                f"background:rgba(0,255,100,6);border:1px solid rgba(0,255,100,20);border-radius:4px;")

    def _toggle_voice(self):
        self._voice_active = not self._voice_active
        SoundFX.click()
        if self._voice_active:
            self.vw.resume(); self._say("Voice reactivated, sir.")
        else:
            self.vw.pause(); self._say("Voice muted, sir.")

    def _stop_speaking(self):
        self.tts.clear_queue()
        self._tts_busy = False
        self.voice_orb.set_state("idle")
        QTimer.singleShot(400, self._safe_resume_voice)

    def _safe_resume_voice(self):
        if not self._tts_busy and self._voice_active:
            self.vw.resume()

    def _recalibrate_mic(self):
        self._do_log("[VOICE] Recalibrating…")
        self.voice_orb.set_state("calibrating")
        self.vw.stop()
        QTimer.singleShot(1500, self._restart_voice)

    def _restart_voice(self):
        self._start_voice(); self._say("Mic recalibrated, sir.")

    @pyqtSlot(str)
    def _on_voice(self, text):
        if not self._voice_active: return
        if text == "_wake_":
            SoundFX.ack(); self._do_live_status("Wake word detected…")
            self._say("Yes sir, listening."); return
        SoundFX.ack()
        self._do_live_status(f'🎤 "{text}"')
        self._do_log(f"[🎤 VOICE] {text}")
        self.chat_area.add_message("user", text)
        self.vw.pause()
        self.execute_command(text)

    def _on_tts_done(self):
        self._tts_busy = False
        self.voice_orb.set_state("idle")
        QTimer.singleShot(600, self._safe_resume_voice)

    def _say(self, text):
        if not text: return
        self._tts_busy = True
        self.voice_orb.set_state("speaking")
        self.voice_orb.set_level(random.randint(60,95))
        self.vw.pause()
        self.tts.speak(text)

    # ─── HELPERS ───────────────────────────────────────────────────────────
    def _do_log(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        cmap = {"[JARVIS]":CYAN,"[🎤":GREEN,"[ERROR":RED_HUD,
                "[ALARM":AMBER,"[AI":PURPLE,"[VOICE":CYAN_DIM}
        c = "#1a3040"
        for k,v in cmap.items():
            if str(msg).startswith(k): c=v; break
        self.console.append(
            f'<span style="color:#0d1e2c">[{ts}]</span> '
            f'<span style="color:{c}">{html.escape(str(msg))}</span>')
        self.console.ensureCursorVisible()

    def _do_live_status(self, msg):
        if msg:
            self.status_lbl.setText(str(msg)[:110]+("…" if len(str(msg))>110 else ""))

    @pyqtSlot()
    def _on_typed(self):
        cmd = self.inp.text().strip()
        if not cmd: return
        SoundFX.click()
        self.chat_area.add_message("user", cmd)
        self._do_log(f"> {cmd}")
        self._do_live_status(cmd)
        self.inp.clear()
        self.execute_command(cmd)

    def _clear_chat(self):
        while self.chat_area._layout.count() > 1:
            item = self.chat_area._layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.chat_area.add_system("Chat cleared. Ready, sir.")

    def _focus_media_tab(self): self.tabs.setCurrentIndex(1)

    # ─── STATS UPDATE ──────────────────────────────────────────────────────
    def _update_stats(self):
        try:
            self._tick_count += 1
            cpu  = psutil.cpu_percent()
            ram  = psutil.virtual_memory().percent
            du   = _disk_usage_safe()
            disk = du.percent if du else 0

            self.cpu_gauge.set_value(cpu)
            self.ram_gauge.set_value(ram)
            self.disk_gauge.set_value(disk)
            self.cpu_bar.set_value(cpu)
            self.ram_bar.set_value(ram)
            self.arc.set_energy(1.0 - cpu/180.0)

            net = psutil.net_io_counters()
            up   = (net.bytes_sent - self._last_net.bytes_sent) / 1024
            down = (net.bytes_recv - self._last_net.bytes_recv) / 1024
            self._last_net = net
            self.net_wave.push(min((up+down)/400.0, 1.0))
            self.net_lbl.setText(f"↑{up:.0f}  ↓{down:.0f} KB/s")
            self.net_bar.set_value(min(100, (up+down)/8))

            self._power_val = max(85, min(100, self._power_val + random.uniform(-0.5,0.5)))
            self.power_display.setText(f"POWER LEVEL AT {int(self._power_val)} PERCENT AND HOLDING STEADY.")

            now = datetime.datetime.now()
            self.time_lbl.setText(now.strftime("%H:%M:%S"))
            self.date_lbl.setText(now.strftime("%a, %d %b %Y"))

            bat = psutil.sensors_battery()
            if bat:
                icon = "⚡" if bat.power_plugged else "🔋"
                self.bat_lbl.setText(f"{icon}  {bat.percent:.0f}%  {'CHARGING' if bat.power_plugged else 'ON BATTERY'}")

            bt = datetime.datetime.fromtimestamp(psutil.boot_time())
            up_td = datetime.datetime.now()-bt
            h,r = divmod(int(up_td.total_seconds()),3600); m2,s = divmod(r,60)
            self.uptime_lbl.setText(f"⏱  Uptime: {h}h {m2}m {s}s")

            if self._tick_count % 5 == 0:
                self._refresh_sys(); self._refresh_procs()
        except: pass

    def _refresh_sys(self):
        try:
            vm  = psutil.virtual_memory()
            du  = _disk_usage_safe()
            bat = psutil.sensors_battery()
            bat_s = (f"{bat.percent:.0f}% {'⚡' if bat.power_plugged else '🔋'}" if bat else "N/A")
            cpu_f = psutil.cpu_freq()
            info=(
                f"CPU   : {psutil.cpu_percent():.0f}%  "
                f"({psutil.cpu_count(False)}P/{psutil.cpu_count()}L"
                f"{f' @ {cpu_f.current:.0f}MHz' if cpu_f else ''})\n"
                f"RAM   : {vm.percent:.0f}%  ({vm.available//1024**2} MB free)\n"
                f"DISK  : {(f'{du.percent:.0f}% ({du.free//1024**3} GB free)') if du else 'N/A'}\n"
                f"BATT  : {bat_s}\n"
                f"HOST  : {socket.gethostname()}\n"
                f"OS    : {platform.system()} {platform.release()}\n"
                f"VOICE : {'ACTIVE' if self._voice_active else 'MUTED'}\n"
                f"AI    : {AI_ENGINE.upper()}\n"
                f"TTS   : {'OPENAI '+TTS_VOICE.upper() if (OPENAI_OK and OPENAI_API_KEY) else 'PYTTSX3' if TTS_PYTTS else 'NONE'}"
            )
            self.sys_box.setPlainText(info)
        except: pass

    def _refresh_procs(self):
        try:
            procs = sorted(psutil.process_iter(['name','cpu_percent','memory_percent']),
                           key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:8]
            lines = []
            for proc in procs:
                try:
                    n = (proc.info['name'] or '')[:18]
                    c = proc.info['cpu_percent'] or 0
                    m = proc.info['memory_percent'] or 0
                    lines.append(f"{n:<18} CPU:{c:4.1f}% MEM:{m:4.1f}%")
                except: pass
            self.proc_box.setPlainText("\n".join(lines))
        except: pass

    # ─── DIALOG OPENERS ────────────────────────────────────────────────────
    def _open_notes(self):   NotesDialog(self.mem, self).exec_()
    def _open_alarms(self):  AlarmDialog(self.alarms, self.reminders, self).exec_()

    def _open_editor(self, filename="", content=""):
        if isinstance(filename, bool): filename = ""
        if isinstance(content,  bool): content  = ""
        filename = "" if filename is None else str(filename)
        content  = "" if content  is None else str(content)
        d = TextEditorDialog(filename, content, self)
        if d.exec_() == QDialog.Accepted and d.result_msg:
            self._do_log(f"[FILE] {d.result_msg}")

    def _open_settings(self):
        global TTS_VOICE
        d = SettingsDialog(TTS_VOICE, self._always_on_voice, self._mic_device_idx, self)
        if d.exec_() == QDialog.Accepted:
            TTS_VOICE = d.selected_voice
            self._always_on_voice  = d.selected_always_on
            self._mic_device_idx   = d.selected_mic_idx
            self.vw.set_always_on(self._always_on_voice)
            self.vw._mic_device_idx = self._mic_device_idx
            mode = "always-on" if self._always_on_voice else "wake-word"
            self._say(f"Settings updated. Voice in {mode} mode, sir.")
            self._on_voice_state("idle")

    # ══════════════════════════════════════════════════════════════════════
    #  COMMAND ENGINE  — COMPREHENSIVE & COMPLETE
    # ══════════════════════════════════════════════════════════════════════
    @pyqtSlot(str)
    def execute_command(self, cmd):
        cmd = cmd.strip()
        if not cmd: return
        self.voice_orb.set_state("processing")
        SoundFX.thinking()
        resp = self._resolve(cmd.lower(), cmd)
        if resp is not None:
            self._deliver(resp)

    def _deliver(self, resp):
        if not resp: return
        self._do_live_status(resp[:120])
        self._do_log(f"[JARVIS] {resp[:120]}")
        self.chat_area.add_message("assistant", resp)
        self._say(resp)

    def _resolve(self, cmd, raw):
        # ── STOP / SILENCE ─────────────────────────────────────────────────
        if any(p in cmd for p in ("stop speaking","be quiet","shut up","stop talking",
                                  "silence","band karo","chup","khamosh")):
            self._stop_speaking(); return "Understood, sir."

        if cmd.strip() == "_wake_":
            return "Yes sir, I am listening. What shall I do?"

        # ── VOICE CONTROLS ─────────────────────────────────────────────────
        if any(p in cmd for p in ("toggle always on","always on mode","enable always on","disable always on")):
            self._always_on_voice = not self._always_on_voice
            self.vw.set_always_on(self._always_on_voice)
            self._on_voice_state("idle")
            return f"Always-on {'enabled' if self._always_on_voice else 'disabled'}, sir."

        if any(p in cmd for p in ("recalibrate","calibrate mic","calibrate microphone",
                                  "reset microphone","fix microphone")):
            QTimer.singleShot(100, self._recalibrate_mic)
            return "Recalibrating microphone, sir."

        if any(p in cmd for p in ("toggle voice","mute voice","unmute voice",
                                  "turn off voice","turn on voice")):
            self._toggle_voice(); return None

        # ── GREETINGS ──────────────────────────────────────────────────────
        if any(w in cmd for w in ("hello","hi jarvis","hey jarvis","good morning","good evening",
                                  "good afternoon","good night","salam","aadab","assalam")):
            h = datetime.datetime.now().hour
            g = "Good morning" if h<12 else "Good afternoon" if h<18 else "Good evening"
            return f"{g} sir. J A R V I S ultra pro, fully operational and at your service."

        # ── EMAIL ──────────────────────────────────────────────────────────
        email_m = re.search(
            r"send\s+(?:an?\s+)?email\s+to\s+([\w.@]+)\s+(?:with\s+)?subject\s+(.+?)\s+"
            r"(?:and\s+)?(?:body|message|saying)\s+(.+)", raw, re.IGNORECASE)
        if email_m:
            return send_email(email_m.group(1).strip(), email_m.group(2).strip(), email_m.group(3).strip())

        if any(p in cmd for p in ("open email","compose email","send email","write email")):
            if any(p in cmd for p in ("open gmail","go to gmail")):
                webbrowser.open("https://mail.google.com"); return "Opening Gmail, sir."
            QTimer.singleShot(0, lambda: EmailDialog(self).exec_())
            return "Opening email composer, sir."

        # ── NOTES ──────────────────────────────────────────────────────────
        if any(p in cmd for p in ("write note","save note","add note","note karo","take note",
                                  "note down","make note","create note")):
            content = re.sub(r"(write note|save note|add note|note karo|take note|"
                             r"note down|make note|create note)","",raw,flags=re.IGNORECASE).strip()
            if content: return self.mem.add_note(content)
            return "Please say what to note, sir."

        if any(p in cmd for p in ("show notes","read notes","list notes","my notes","all notes")):
            return self.mem.get_notes()

        m_del = re.search(r"delete note\s*(\d+)", cmd)
        if m_del: return self.mem.delete_note(m_del.group(1))
        if any(p in cmd for p in ("delete all notes","clear notes","clear all notes")):
            return self.mem.delete_note()

        # ── MEMORY ─────────────────────────────────────────────────────────
        m = re.search(r"(remember|store)\s+(.+?)\s+(is|=|hai)\s+(.+)", cmd)
        if m:
            self.mem.remember(m.group(2).strip(), m.group(4).strip())
            return f"Remembered: {m.group(2)} equals {m.group(4)}, sir."

        mr = re.search(r"recall\s+(.+)", cmd)
        if mr: return self.mem.recall(mr.group(1).strip())

        if any(p in cmd for p in ("what do you remember","show memory","all memory","my memory")):
            return self.mem.all_memory()

        mf = re.search(r"forget\s+(.+)", cmd)
        if mf: return self.mem.forget(mf.group(1).strip())

        # ── MEDIA: SPECIFIC FILE ───────────────────────────────────────────
        pf = re.search(r"play\s+(?:file\s+)?(.+\.(mp3|mp4|wav|ogg|flac|avi|mkv|m4a|aac|wma))",
                       cmd, re.IGNORECASE)
        if pf:
            fname = pf.group(1).strip()
            for base in [fname,
                         os.path.join(os.path.expanduser("~"),"Music",fname),
                         os.path.join(os.path.expanduser("~"),"Downloads",fname),
                         os.path.join(os.path.expanduser("~"),"Videos",fname)]:
                if os.path.isfile(base):
                    msg = self.media_player.load_and_play(base)
                    self.tabs.setCurrentIndex(1); return msg
            return "Media file not found, sir."

        # ── MEDIA: FOLDER ──────────────────────────────────────────────────
        if re.search(r"play\s+(music|audio|songs?|gana|tracks?)\s*(?:from\s+)?(\w+)?", cmd):
            fm = re.search(r"from\s+(\w+)", cmd)
            fp = _folder_path(fm.group(1) if fm else "music")
            files = []
            for ext in ("*.mp3","*.wav","*.ogg","*.flac","*.m4a","*.aac"):
                files.extend(glob.glob(os.path.join(fp,ext)))
            if files:
                random.shuffle(files)
                msg = self.media_player.load_playlist(files)
                self.tabs.setCurrentIndex(1)
                return f"Found {len(files)} audio files. {msg}"
            return "No audio files found in that location, sir."

        # ── YOUTUBE ───────────────────────────────────────────────────────
        if re.search(r"play\s+(.+)\s+on\s+youtube", cmd):
            q = re.sub(r"play|on youtube","",cmd).strip()
            webbrowser.open("https://www.youtube.com/results?search_query="+q.replace(" ","+"))
            return f"Searching YouTube for {q}, sir."

        # ── MEDIA CONTROLS ────────────────────────────────────────────────
        if any(p in cmd for p in ("pause music","pause video","pause media","pause")):
            self.media_player.toggle_play(); return "Media paused, sir."
        if any(p in cmd for p in ("resume music","resume media","unpause","continue playing")):
            self.media_player.toggle_play(); return "Resuming playback, sir."
        if any(p in cmd for p in ("stop music","stop video","stop media")):
            self.media_player._player.stop(); return "Media stopped, sir."
        if any(p in cmd for p in ("next track","next song","skip","next")):
            self.media_player.next_track(); return "Next track, sir."
        if any(p in cmd for p in ("previous track","prev track","back track","previous song")):
            self.media_player.prev_track(); return "Previous track, sir."
        if any(p in cmd for p in ("volume up","louder","increase volume","aawaz barho")):
            v = min(100, self.media_player.vol_sl.value()+15)
            self.media_player.vol_sl.setValue(v); return f"Volume {v} percent, sir."
        if any(p in cmd for p in ("volume down","quieter","decrease volume","aawaz kam")):
            v = max(0, self.media_player.vol_sl.value()-15)
            self.media_player.vol_sl.setValue(v); return f"Volume {v} percent, sir."
        vol_m = re.search(r"set volume\s+(?:to\s+)?(\d+)", cmd)
        if vol_m:
            v = max(0, min(100,int(vol_m.group(1))))
            self.media_player.vol_sl.setValue(v); return f"Volume set to {v}, sir."

        # ── ALARMS ────────────────────────────────────────────────────────
        if any(p in cmd for p in ("set alarm","alarm lagao","alarm at","alarm for","create alarm")):
            th = re.search(r"at\s+(\d{1,2})[:\s]?(\d{2})?\s*(am|pm)?", cmd)
            mm = re.search(r"in\s+(\d+)\s+minute", cmd)
            hm = re.search(r"in\s+(\d+)\s+hour", cmd)
            lm = re.search(r"(?:for|named?|label)\s+(.+?)(?:\s+at|\s+in|$)", cmd)
            label = "Alarm"
            if lm:
                raw_label = re.sub(r"(set|karo|lagao|alarm|for|label|named?)","",lm.group(1)).strip()
                if raw_label: label = raw_label
            now2 = datetime.datetime.now()
            if th:
                hour=int(th.group(1)); minute=int(th.group(2) or 0); ampm=th.group(3)
                if ampm=="pm" and hour<12: hour+=12
                if ampm=="am" and hour==12: hour=0
                when=now2.replace(hour=hour,minute=minute,second=0,microsecond=0)
                if when<=now2: when+=datetime.timedelta(days=1)
                return self.alarms.add_alarm(label,when)
            elif mm:
                return self.alarms.add_alarm(label,now2+datetime.timedelta(minutes=int(mm.group(1))))
            elif hm:
                return self.alarms.add_alarm(label,now2+datetime.timedelta(hours=int(hm.group(1))))
            QTimer.singleShot(0, self._open_alarms); return "Opening alarm manager, sir."

        if any(p in cmd for p in ("list alarms","show alarms","my alarms")):
            return self.alarms.list_alarms()
        if any(p in cmd for p in ("delete alarm","remove alarm","clear alarms","cancel alarm")):
            idx_m = re.search(r"\d+", cmd)
            return self.alarms.delete_alarm(int(idx_m.group()) if idx_m else None)

        # ── REMINDERS ─────────────────────────────────────────────────────
        if any(p in cmd for p in ("remind me","set reminder","yaad dilao","reminder lagao")):
            try:
                mm2 = re.search(r"in\s+(\d+)\s+minute", cmd)
                mh  = re.search(r"in\s+(\d+)\s+hour", cmd)
                mt  = re.search(r"\bto\b\s+(.+)", cmd)
                if (mm2 or mh) and mt:
                    mins = (int(mm2.group(1)) if mm2 else int(mh.group(1))*60)
                    task = mt.group(1).strip().rstrip(".")
                    self.reminders.add(task, datetime.datetime.now()+datetime.timedelta(minutes=mins))
                    return f"Reminder set, sir. I will alert you in {mins} minutes to {task}."
                return "Please say: remind me in X minutes to do something, sir."
            except: return "Could not parse reminder, sir."

        if any(p in cmd for p in ("list reminders","show reminders","my reminders")):
            return self.reminders.list_all()

        # ── FILE CRUD ─────────────────────────────────────────────────────
        wf = re.search(r"create\s+(?:a\s+)?(?:file|document)\s+(.+?)\s+with\s+content\s+(.+)",
                       raw, re.IGNORECASE)
        if wf: return create_file_doc(wf.group(1).strip(), wf.group(2).strip())

        rf = re.search(r"(?:read|show)\s+file\s+(.+)", raw, re.IGNORECASE)
        if rf: return read_file_doc(rf.group(1).strip())

        df2 = re.search(r"delete\s+file\s+(.+)", raw, re.IGNORECASE)
        if df2: return delete_file_doc(df2.group(1).strip())

        lf = re.search(r"list\s+files?\s+(?:in\s+)?(.+)", raw, re.IGNORECASE)
        if lf: return list_files_in(lf.group(1).strip())

        if any(p in cmd for p in ("open editor","text editor","open text editor")):
            QTimer.singleShot(0, lambda: self._open_editor()); return "Opening text editor, sir."

        # ── FOLDER SHORTCUTS ───────────────────────────────────────────────
        for k in ("documents","downloads","desktop","pictures","music","videos"):
            if f"open {k}" in cmd or f"go to {k}" in cmd or f"{k} folder" in cmd:
                return open_path(_folder_path(k)) or f"Opening {k}, sir."

        # ── CLOSE APP ─────────────────────────────────────────────────────
        close_m = re.search(r"(?:close|kill|terminate)\s+(.+)", cmd)
        if close_m and not any(p in cmd for p in ("close tab","close window")):
            return close_window_by_name(close_m.group(1).strip())

        # ── POWER COMMANDS ────────────────────────────────────────────────
        if any(p in cmd for p in ("shutdown","shut down computer","power off","turn off computer")):
            if QMessageBox.question(self,"Shutdown","Shutdown your computer?",
                                    QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
                shutdown_system(); return "Shutting down in 5 seconds, sir. Goodbye!"
            return "Shutdown cancelled, sir."

        if any(p in cmd for p in ("restart computer","reboot","restart system")):
            if QMessageBox.question(self,"Restart","Restart your computer?",
                                    QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
                restart_system(); return "Restarting, sir."
            return "Restart cancelled, sir."

        if any(p in cmd for p in ("lock computer","lock pc","lock screen","lock workstation")):
            return lock_system()

        # ── TIME / DATE ───────────────────────────────────────────────────
        if any(p in cmd for p in ("what time","current time","time is it","waqt kya","tell me the time")):
            return f"It is {datetime.datetime.now().strftime('%I:%M:%S %p')}, sir."

        if any(p in cmd for p in ("what date","today date","current date","aaj ki tarikh","what day")):
            return "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y") + ", sir."

        if any(p in cmd for p in ("what year","current year","konsa saal")):
            return f"The year is {datetime.datetime.now().year}, sir."

        # ── SYSTEM INFO ───────────────────────────────────────────────────
        if any(p in cmd for p in ("detailed system info","full system info","complete system info")):
            return get_system_info_full()

        if any(p in cmd for p in ("system info","system status","computer info","hardware info")):
            vm = psutil.virtual_memory()
            return (f"Running {platform.system()} {platform.release()}, CPU at "
                    f"{psutil.cpu_percent():.0f} percent, RAM at {vm.percent:.0f} percent "
                    f"with {vm.available//1024**2} megabytes free, sir.")

        if "battery" in cmd or "charging" in cmd:
            bat = psutil.sensors_battery()
            if bat: return f"Battery at {bat.percent:.0f} percent, {'charging' if bat.power_plugged else 'discharging'}, sir."
            return "No battery sensor detected, sir."

        if any(p in cmd for p in ("uptime","system uptime","how long running")):
            bt = datetime.datetime.fromtimestamp(psutil.boot_time())
            up = datetime.datetime.now()-bt
            h,r = divmod(int(up.total_seconds()),3600); m2,s = divmod(r,60)
            return f"System has been running for {h} hours, {m2} minutes, and {s} seconds, sir."

        if any(p in cmd for p in ("disk space","storage space","free space","hard drive")):
            du = _disk_usage_safe()
            if du: return f"Disk: {du.total//1024**3} gigabytes total, {du.free//1024**3} gigabytes free, sir."
            return "Could not read disk info, sir."

        if any(p in cmd for p in ("ip address","my ip","local ip","ip batao")):
            try:
                ip = socket.gethostbyname(socket.gethostname())
                return f"Local IP address is {ip}, sir."
            except: return "Could not retrieve IP address, sir."

        if any(p in cmd for p in ("network info","network details","show network")):
            try:
                net_addrs = psutil.net_if_addrs()
                net_stats = psutil.net_if_stats()
                lines = []
                for iface, addrs in list(net_addrs.items())[:4]:
                    stat = net_stats.get(iface)
                    status = "UP" if (stat and stat.isup) else "DOWN"
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            lines.append(f"{iface}: {addr.address} ({status})")
                return ("Network interfaces: " + ", ".join(lines)) if lines else "No network interfaces found, sir."
            except: return "Could not retrieve network info, sir."

        if any(p in cmd for p in ("list processes","running processes","process list","top processes")):
            try:
                procs = sorted(psutil.process_iter(['name','cpu_percent','memory_percent']),
                               key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:5]
                lines = [f"{(p.info['name'] or 'Unknown')[:20]}: CPU {p.info['cpu_percent']:.1f}%" for p in procs]
                return "Top processes: " + ", ".join(lines) + ", sir."
            except: return "Could not list processes, sir."

        # ── MATH ──────────────────────────────────────────────────────────
        calc_trig = ("calculate","compute","math","evaluate","how much is","kitna hai","solve")
        if any(p in cmd for p in calc_trig) and any(c.isdigit() for c in cmd):
            expr = re.sub(r"(calculate the?|calculate|compute|how much is|math|evaluate|kitna hai|solve)","",cmd).strip()
            expr = re.sub(r"\b(times|multiplied by|into|x)\b","*",expr)
            expr = re.sub(r"\b(divided by|over)\b","/",expr)
            expr = re.sub(r"\b(plus|added to)\b","+",expr)
            expr = re.sub(r"\bminus\b|\bsubtract\b","-",expr)
            expr = re.sub(r"\b(to the power of|\^)\b","**",expr)
            expr = re.sub(r"[^0-9+\-*/().\s%]","",expr).strip()
            if expr and re.search(r"\d",expr):
                try:
                    result = eval(expr,{"__builtins__":{},"pow":pow,"abs":abs,"round":round})
                    return f"The result is {result:,g}, sir."
                except: pass

        if any(p in cmd for p in ("square root","sqrt","root of")):
            nums = re.findall(r"\d+\.?\d*", cmd)
            if nums: return f"Square root of {nums[0]} is {math.sqrt(float(nums[0])):.6g}, sir."

        # ── UNIT CONVERSION ───────────────────────────────────────────────
        if any(p in cmd for p in ("convert","to fahrenheit","to celsius","to miles","to km",
                                  "to kg","to lbs","to meters","to feet")):
            m2 = re.search(r"(\d+\.?\d*)\s*(km|miles?|kg|lbs?|pounds?|celsius|fahrenheit|"
                           r"meters?|feet|foot|inches?|liters?|gallons?|cm|inches?)", cmd)
            if m2:
                val=float(m2.group(1)); u=m2.group(2).lower().rstrip("s")
                conv={
                    "km":(val*.621371,"miles"),"mile":(val*1.60934,"km"),
                    "kg":(val*2.20462,"lbs"),"lb":(val*.453592,"kg"),
                    "pound":(val*.453592,"kg"),"celsius":(val*9/5+32,"Fahrenheit"),
                    "fahrenheit":((val-32)*5/9,"Celsius"),"meter":(val*3.28084,"feet"),
                    "foot":(val*.3048,"meters"),"feet":(val*.3048,"meters"),
                    "inch":(val*2.54,"centimeters"),"cm":(val*.393701,"inches"),
                    "liter":(val*.264172,"gallons"),"gallon":(val*3.78541,"liters")
                }
                if u in conv:
                    rv,tu = conv[u]; return f"{val} {m2.group(2)} equals {rv:.4g} {tu}, sir."

        # ── CLIPBOARD ─────────────────────────────────────────────────────
        if any(p in cmd for p in ("show clipboard","clipboard content","clipboard")):
            t = QApplication.clipboard().text()
            return f"Clipboard: {t[:200]}" if t else "Clipboard is empty, sir."

        if re.match(r"^copy ", cmd):
            t = raw[5:].strip()
            if t: QApplication.clipboard().setText(t); return "Copied to clipboard, sir."

        # ── SCREENSHOT ────────────────────────────────────────────────────
        if any(p in cmd for p in ("screenshot","capture screen","take screenshot","screen shot")):
            try:
                pix = QApplication.primaryScreen().grabWindow(0)
                path = os.path.join(os.path.expanduser("~"),"Desktop",
                    f"jarvis_ss_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                pix.save(path,"PNG"); return f"Screenshot saved to Desktop as {os.path.basename(path)}, sir."
            except Exception as e: return f"Screenshot failed: {e}"

        # ── IMAGE GENERATION ──────────────────────────────────────────────
        if any(p in cmd for p in ("generate image","create image","dall-e","draw ",
                                  "generate a picture","make art","image banao")):
            prompt = re.sub(r"(generate image of?|create image of?|draw|dall-e|"
                            r"generate a picture of?|make art of?|image banao)","",cmd).strip() or raw
            worker = ImageGenWorker(prompt, self)
            worker.done.connect(self._on_image_ready)
            worker.fail.connect(self._on_ai_err)
            worker.finished.connect(lambda: self._safe_remove_worker(worker))
            self._active_workers.append(worker); worker.start()
            return "Generating image with DALL-E 3, sir. One moment."

        # ── SYSTEM APP LAUNCHER (COMPREHENSIVE) ───────────────────────────
        # Windows Built-in Apps
        win_apps = {
            "notepad":        "notepad.exe",
            "calculator":     "calc.exe",
            "paint":          "mspaint.exe",
            "ms paint":       "mspaint.exe",
            "cmd":            "cmd.exe",
            "command prompt": "cmd.exe",
            "terminal":       "cmd.exe",
            "powershell":     "powershell.exe",
            "task manager":   "taskmgr.exe",
            "file explorer":  "explorer.exe",
            "explorer":       "explorer.exe",
            "control panel":  "control.exe",
            "snipping tool":  "SnippingTool.exe",
            "snip":           "SnippingTool.exe",
            "magnifier":      "magnify.exe",
            "on screen keyboard": "osk.exe",
            "sticky notes":   "StickyNotes.exe",
            "character map":  "charmap.exe",
            "registry editor":"regedit.exe",
            "device manager": "devmgmt.msc",
            "disk management":"diskmgmt.msc",
            "event viewer":   "eventvwr.msc",
            "services":       "services.msc",
            "msconfig":       "msconfig.exe",
            "system properties": "sysdm.cpl",
            "display settings": "desk.cpl",
            "sound settings":   "mmsys.cpl",
            "network connections": "ncpa.cpl",
            "programs":       "appwiz.cpl",
            "add remove programs": "appwiz.cpl",
            "windows update": "ms-settings:windowsupdate",
            "settings":       "ms-settings:",
            "store":          "ms-windows-store:",
            "camera":         "microsoft.windows.camera:",
            "maps":           "bingmaps:",
            "mail":           "outlookmail:",
            "calendar":       "outlookcal:",
            "clock":          "ms-clock:",
            "alarm":          "ms-clock:",
            "phone":          "ms-settings:phone",
            "bluetooth":      "ms-settings:bluetooth",
            "wifi":           "ms-settings:network-wifi",
            "airplane mode":  "ms-settings:network-airplanemode",
            "accessibility":  "ms-settings:easeofaccess",
            "narrator":       "ms-settings:easeofaccess-narrator",
        }

        # Third-party Apps
        app_map = {
            "word":               "winword.exe",
            "microsoft word":     "winword.exe",
            "excel":              "excel.exe",
            "microsoft excel":    "excel.exe",
            "powerpoint":         "powerpnt.exe",
            "microsoft powerpoint": "powerpnt.exe",
            "outlook":            "outlook.exe",
            "microsoft outlook":  "outlook.exe",
            "access":             "msaccess.exe",
            "onenote":            "ONENOTE.EXE",
            "teams":              "teams.exe",
            "microsoft teams":    "teams.exe",
            "skype":              "skype.exe",
            "vs code":            "code",
            "visual studio code": "code",
            "vscode":             "code",
            "visual studio":      "devenv.exe",
            "pycharm":            "pycharm64.exe",
            "pycharm64":          "pycharm64.exe",
            "intellij":           "idea64.exe",
            "android studio":     "studio64.exe",
            "atom":               "atom.exe",
            "sublime":            "sublime_text.exe",
            "sublime text":       "sublime_text.exe",
            "notepad++":          "notepad++.exe",
            "vlc":                "vlc.exe",
            "media player":       "wmplayer.exe",
            "windows media player": "wmplayer.exe",
            "chrome":             "chrome.exe",
            "google chrome":      "chrome.exe",
            "firefox":            "firefox.exe",
            "mozilla firefox":    "firefox.exe",
            "edge":               "msedge.exe",
            "microsoft edge":     "msedge.exe",
            "brave":              "brave.exe",
            "opera":              "opera.exe",
            "internet explorer":  "iexplore.exe",
            "spotify":            "spotify.exe",
            "discord":            "discord.exe",
            "zoom":               "zoom.exe",
            "obs":                "obs64.exe",
            "obs studio":         "obs64.exe",
            "steam":              "steam.exe",
            "epic games":         "epicgameslauncher.exe",
            "origin":             "origin.exe",
            "battle.net":         "battle.net.exe",
            "7zip":               "7zfm.exe",
            "7-zip":              "7zfm.exe",
            "winrar":             "winrar.exe",
            "wireshark":          "wireshark.exe",
            "putty":              "putty.exe",
            "filezilla":          "filezilla.exe",
            "gimp":               "gimp-2.10.exe",
            "photoshop":          "photoshop.exe",
            "premiere":           "premiere.exe",
            "after effects":      "afterfx.exe",
            "audacity":           "audacity.exe",
            "virtualbox":         "virtualbox.exe",
            "vmware":             "vmware.exe",
            "anaconda":           "anaconda-navigator.exe",
            "jupyter":            "jupyter-notebook.exe",
            "postman":            "postman.exe",
            "docker":             "docker desktop.exe",
            "git bash":           "git-bash.exe",
            "github desktop":     "githubdesktop.exe",
            "telegram":           "telegram.exe",
            "whatsapp":           "whatsapp.exe",
            "signal":             "signal.exe",
            "slack":              "slack.exe",
            "notion":             "notion.exe",
            "figma":              "figma.exe",
            "blender":            "blender.exe",
            "unity":              "unity.exe",
            "unreal":             "ue4editor.exe",
            "taskmgr":            "taskmgr.exe",
        }

        all_apps = {**win_apps, **app_map}

        for name, exe in all_apps.items():
            if (f"open {name}" in cmd or f"launch {name}" in cmd or
                    f"run {name}" in cmd or f"start {name}" in cmd or cmd.strip()==name):
                try:
                    if exe.startswith("ms-") or exe.endswith(":"):
                        subprocess.Popen(f"start {exe}", shell=True)
                    else:
                        subprocess.Popen(exe, shell=True)
                    return f"Opening {name.title()}, sir."
                except Exception as e:
                    return f"Could not open {name.title()}: {e}, sir."

        # ── WEBSITES (COMPREHENSIVE) ───────────────────────────────────────
        site_map = {
            "youtube":          "https://youtube.com",
            "google":           "https://google.com",
            "facebook":         "https://facebook.com",
            "instagram":        "https://instagram.com",
            "twitter":          "https://twitter.com",
            "x.com":            "https://x.com",
            "github":           "https://github.com",
            "gmail":            "https://mail.google.com",
            "whatsapp web":     "https://web.whatsapp.com",
            "whatsapp":         "https://web.whatsapp.com",
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
            "figma":            "https://figma.com",
            "daraz":            "https://daraz.pk",
            "geo news":         "https://geo.tv",
            "geo tv":           "https://geo.tv",
            "ary news":         "https://arynews.tv",
            "dawn":             "https://dawn.com",
            "bbc":              "https://bbc.com",
            "bbc news":         "https://bbc.com/news",
            "cnn":              "https://cnn.com",
            "google drive":     "https://drive.google.com",
            "google docs":      "https://docs.google.com",
            "google sheets":    "https://sheets.google.com",
            "google slides":    "https://slides.google.com",
            "kaggle":           "https://kaggle.com",
            "hugging face":     "https://huggingface.co",
            "tiktok":           "https://tiktok.com",
            "pinterest":        "https://pinterest.com",
            "ebay":             "https://ebay.com",
            "alibaba":          "https://alibaba.com",
            "aliexpress":       "https://aliexpress.com",
            "paypal":           "https://paypal.com",
            "medium":           "https://medium.com",
            "quora":            "https://quora.com",
            "coursera":         "https://coursera.org",
            "udemy":            "https://udemy.com",
            "edx":              "https://edx.org",
            "khan academy":     "https://khanacademy.org",
            "w3schools":        "https://w3schools.com",
            "mdn":              "https://developer.mozilla.org",
            "npm":              "https://npmjs.com",
            "pypi":             "https://pypi.org",
            "docker hub":       "https://hub.docker.com",
            "trello":           "https://trello.com",
            "notion":           "https://notion.so",
            "jira":             "https://jira.atlassian.com",
            "slack":            "https://slack.com",
            "zoom":             "https://zoom.us",
            "microsoft":        "https://microsoft.com",
            "apple":            "https://apple.com",
            "imdb":             "https://imdb.com",
            "wolframalpha":     "https://wolframalpha.com",
            "google news":      "https://news.google.com",
        }
        for name,url in site_map.items():
            if (f"open {name}" in cmd or f"go to {name}" in cmd or
                    f"launch {name}" in cmd or f"browse {name}" in cmd or
                    f"visit {name}" in cmd):
                webbrowser.open(url); return f"Opening {name.title()} in your browser, sir."

        # ── WEB SEARCH ────────────────────────────────────────────────────
        if any(p in cmd for p in ("search for","google for","look up","find online","dhundo",
                                  "talash karo","search online","google search","search google")):
            q = re.sub(r"(search for|google for|look up|find online|dhundo|talash karo|"
                       r"search online|google search|search google)","",cmd).strip()
            if q:
                webbrowser.open("https://www.google.com/search?q="+q.replace(" ","+"))
                return f"Searching Google for {q}, sir."

        # ── WEATHER ───────────────────────────────────────────────────────
        if any(p in cmd for p in ("weather","mausam","forecast","barish","humidity",
                                  "rain","sunny","temperature","weather in","weather today")):
            city = re.sub(r"(weather|mausam|temperature|in|at|for|current|aaj|ka|"
                          r"forecast|batao|today|rain|sunny|cloudy|how is|what is|the)","",cmd).strip()
            if not city or len(city) < 2: city = "Karachi"
            if REQ_OK:
                try:
                    r2 = requests.get(f"https://wttr.in/{city.replace(' ','+')}?format=3",timeout=6)
                    if r2.status_code==200 and r2.text.strip():
                        return r2.text.strip()+", sir."
                except: pass
            webbrowser.open(f"https://www.google.com/search?q=weather+{city.replace(' ','+')}")
            return f"Opening weather for {city}, sir."

        # ── NEWS ──────────────────────────────────────────────────────────
        if any(p in cmd for p in ("latest news","breaking news","news today","khabar","headlines",
                                  "news pakistan","news update")):
            topic = re.sub(r"(latest|news|khabar|headlines|today|breaking|pakistan|update)","",cmd).strip()
            q = (topic+" news today") if topic else "world news today"
            webbrowser.open("https://news.google.com/search?q="+q.replace(" ","+"))
            return "Opening latest news in your browser, sir."

        # ── JOKES ─────────────────────────────────────────────────────────
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
            "There are 10 types of people: those who understand binary, and those who do not.",
            "Debugging is like being the detective in a mystery where you are also the murderer.",
            "Why do Java developers wear glasses? Because they do not C sharp, sir.",
            "Ek programmer ki biwi ne kaha bazaar jao, doodh lo, ande milein to 12 lo. Woh 12 litre doodh le aaya sir.",
            "My code has no bugs. It has undocumented features, sir.",
            "An algorithm walks into a bar. The bartender says what will it be. It says depends on the input.",
            "Why do Python programmers prefer snake_case? Because they are literally snake people, sir.",
            "The first rule of debugging: check if the code is plugged in, sir.",
        ]
        if any(p in cmd for p in ("joke","funny","mazaak","lataifa","tell me a joke","make me laugh","hasao")):
            return random.choice(jokes)

        # ── MOTIVATION ────────────────────────────────────────────────────
        quotes = [
            "The only way to do great work is to love what you do. Steve Jobs, sir.",
            "Khudi ko kar buland itna ke har taqdir se pehle. Allama Iqbal, sir.",
            "Any sufficiently advanced technology is indistinguishable from magic. Arthur Clarke, sir.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. Churchill, sir.",
            "Your limitation is only your imagination. Go build something extraordinary, sir.",
            "In the middle of every difficulty lies opportunity. Einstein, sir.",
            "The future belongs to those who believe in the beauty of their dreams. Eleanor Roosevelt, sir.",
        ]
        if any(p in cmd for p in ("motivate","inspire","quote","motivation","himmat","encourage","boost")):
            return random.choice(quotes)

        # ── CONVERSATIONAL ────────────────────────────────────────────────
        if any(p in cmd for p in ("thank","shukriya","meherbani","thanks","thank you","shukran")):
            return random.choice(["You are welcome, sir.","Shukriya qabool karein, sir.",
                                  "My pleasure, sir.","Always at your service, sir.",
                                  "That is what I am here for, sir."])

        if any(p in cmd for p in ("how are you","kaise ho","theek ho","you ok","how do you do")):
            return "All systems nominal, sir. Arc reactor at peak efficiency. How may I assist you?"

        if any(p in cmd for p in ("what is your name","your name","who are you","tum kaun ho","introduce yourself","apna naam batao")):
            return ("I am J A R V I S, Just A Rather Very Intelligent System, version 10 ultra pro, "
                    "your AI desktop assistant. Developed as a final year project by Amina Sikandar, Hamna Rubab, and Eesha Jewan, sir.")

        if any(p in cmd for p in ("who made you","who created you","kisne banaya","who built you","developer","creator")):
            return ("I was developed as a final year project by three talented engineers: "
                    "Amina Sikandar, Hamna Rubab, and Eesha Jewan, sir. International expo edition.")

        if any(p in cmd for p in ("goodbye","bye","shut down jarvis","khuda hafiz","allah hafiz",
                                  "alvida","exit jarvis","quit jarvis","band karo")):
            QTimer.singleShot(3500, QApplication.quit)
            return "Goodbye sir. J A R V I S shutting down. Allah Hafiz."

        if any(p in cmd for p in ("help","what can you do","capabilities","features","commands","meri madad")):
            return ("I handle voice commands in English and Urdu, sir. "
                    "I play music and video, send emails, set alarms and reminders, "
                    "manage files, open any application, browse websites, search the web, "
                    "check weather and news, do math and conversions, take screenshots, "
                    "manage notes and memory, generate DALL-E images, "
                    "answer any question via AI, and much more. "
                    "Just say Jarvis followed by your command.")

        if any(p in cmd for p in ("idea","project idea","suggest","kya banao","koi idea do")):
            ideas = [
                "Build a real-time face recognition attendance system using OpenCV, sir.",
                "Create a stock market prediction tool using LSTM neural networks, sir.",
                "Develop a smart home automation dashboard using Raspberry Pi, sir.",
                "Build a natural language to SQL converter using GPT-4, sir.",
                "Design a blockchain-based transparent voting system, sir.",
                "Create a sign language recognition app using computer vision, sir.",
                "Build an AI-powered resume analyzer and job matcher, sir.",
            ]
            return random.choice(ideas)

        if any(p in cmd for p in ("ping","check internet","am i online","network check","internet check")):
            try:
                socket.create_connection(("8.8.8.8",53),timeout=3)
                return "Internet connection active, sir. All systems connected."
            except: return "No internet connection detected, sir. Check your network."

        # ── FACTUAL QUERIES ───────────────────────────────────────────────
        factual_triggers = (
            r"^(what\s+is\s+|what\s+are\s+|who\s+is\s+|who\s+was\s+|"
            r"tell\s+me\s+about\s+|explain\s+|define\s+|what\s+does\s+|"
            r"how\s+does\s+|how\s+do\s+|describe\s+|information\s+(?:on|about)\s+|"
            r"history\s+of\s+|biography\s+of\s+|"
            r"kya\s+hai\s+|kon\s+hai\s+|kon\s+tha\s+|batao\s+|ke\s+baare\s+mein\s+)"
        )
        factual_m = re.match(factual_triggers, cmd, re.IGNORECASE)
        if factual_m:
            topic = cmd[factual_m.end():].strip()
            if topic and len(topic) > 1:
                # AI first: Wikipedia summaries are stiff and can't reason,
                # so if a real AI brain is configured, prefer it.
                if AI_ENGINE != "none":
                    self._dispatch_ai(raw); return None
                if WIKI_OK:
                    try:
                        s = wikipedia.summary(topic, sentences=3, auto_suggest=True)
                        return re.sub(r"\[\[.*?\]\]","",s).strip()
                    except wikipedia.exceptions.DisambiguationError as e:
                        if e.options:
                            try: return wikipedia.summary(e.options[0], sentences=3).strip()
                            except: pass
                    except: pass
                webbrowser.open("https://www.google.com/search?q="+topic.replace(" ","+"))
                return (f"My AI brain is not configured, sir — no API key found. "
                        f"Opening a Google search for {topic} instead.")

        # ── WIKIPEDIA FALLBACK ────────────────────────────────────────────
        if WIKI_OK:
            for tr in ("tell me about","explain","information on","information about",
                       "history of","biography of","ke baare mein","describe","batao"):
                if tr in cmd:
                    q = cmd[cmd.find(tr)+len(tr):].strip()
                    if q and len(q)>1:
                        try:
                            s = wikipedia.summary(q, sentences=3, auto_suggest=True)
                            return re.sub(r"\[\[.*?\]\]","",s).strip()
                        except wikipedia.exceptions.DisambiguationError as e:
                            if e.options:
                                try: return wikipedia.summary(e.options[0],sentences=3).strip()
                                except: pass
                        except: pass
                    break

        # ── AI FALLBACK ───────────────────────────────────────────────────
        if AI_ENGINE != "none":
            self._dispatch_ai(raw); return None

        # ── ABSOLUTE FALLBACK ─────────────────────────────────────────────
        webbrowser.open("https://www.google.com/search?q="+raw.replace(" ","+"))
        return (f"No AI engine is configured, sir — set ANTHROPIC_API_KEY or "
                f"OPENAI_API_KEY as an environment variable to enable me. "
                f"Searching Google for: {raw[:50]} for now.")

    def _dispatch_ai(self, raw):
        self.voice_orb.set_state("thinking")
        self._do_log(f"[AI ▶ {AI_ENGINE.upper()}] {raw[:80]}")
        self._do_live_status("Connecting AI brain…")
        has_urdu = bool(re.search(r"[ا-ی]",raw)) or any(
            w in raw.lower() for w in ["kya","kon","kaise","batao","hai","nahi","mujhe",
                                        "aaj","kal","waqt","aur","bhi","karo","ap","hum"])
        context = "Reply in Roman Urdu if user wrote Roman Urdu." if has_urdu else ""
        worker = AIWorker(raw, self._chat_history, context, self)
        worker.response_ready.connect(self._on_ai_resp)
        worker.error_occurred.connect(self._on_ai_err)
        worker.finished.connect(lambda: self._safe_remove_worker(worker))
        self._active_workers.append(worker); worker.start()
        self._chat_history.append({"role":"user","content":raw})

    def _safe_remove_worker(self, worker):
        try:
            if worker in self._active_workers: self._active_workers.remove(worker)
        except: pass

    @pyqtSlot(str)
    def _on_ai_resp(self, text):
        self._chat_history.append({"role":"assistant","content":text})
        if len(self._chat_history) > 30:
            self._chat_history = self._chat_history[-30:]
        self._deliver(text)

    @pyqtSlot(str)
    def _on_ai_err(self, err):
        self._do_log(f"[ERROR] {err}")
        self.voice_orb.set_state("idle")
        SoundFX.error()
        self._deliver("I encountered an error, sir. Check your internet in Settings.")

    @pyqtSlot(str,str)
    def _on_image_ready(self, prompt, url):
        webbrowser.open(url)
        self._deliver("Image generated and opened in your browser, sir.")

    def _on_reminder(self, text):
        self._do_log(f"[REMINDER] {text}"); SoundFX.alert()
        QMessageBox.information(self,"⏰ Reminder",f"{text}")
        self._say(f"Sir, your reminder: {text}")

    def _on_alarm(self, label):
        self._do_log(f"[ALARM] {label}"); SoundFX.alarm_beep()
        QMessageBox.information(self,"🔔 Alarm",f"ALARM: {label}")
        self._say(f"Sir, alarm activated. {label}")

    # ─── PAINT / RESIZE ────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(3,8,22))
        p.setPen(QPen(QColor(0,50,100,5),1))
        for x in range(0,self.width(),50): p.drawLine(x,0,x,self.height())
        for y in range(0,self.height(),50): p.drawLine(0,y,self.width(),y)
        gr = QRadialGradient(self.width()/2, self.height()/2, self.width()*.55)
        gr.setColorAt(0.0, QColor(0,35,90,22))
        gr.setColorAt(1.0, QColor(0,0,0,0))
        p.fillRect(self.rect(), QBrush(gr))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.hex_bg.setGeometry(0,0,self.width(),self.height())
        self.hex_bg.lower()

    def closeEvent(self, e):
        try: self.vw.stop()
        except: pass
        try: self.tts.stop()
        except: pass
        if PYGAME_OK:
            try: pygame.mixer.quit()
            except: pass
        e.accept()