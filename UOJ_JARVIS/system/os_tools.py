"""
system/os_tools.py  —  File I/O, app launching, power commands,
                        system info, email, screenshot, clipboard.
"""

import os
import re
import glob
import math
import socket
import platform
import datetime
import subprocess
import webbrowser
import smtplib
import email.mime.text
import email.mime.multipart
import shutil

import psutil

from core.config import FILES_DIR, DATA_DIR
from core import config as cfg


# ─── Paths ────────────────────────────────────────────────────────────────
def _folder_path(name: str) -> str:
    hm = os.path.expanduser("~")
    mapping = {
        "documents": os.path.join(hm, "Documents"),
        "downloads": os.path.join(hm, "Downloads"),
        "desktop":   os.path.join(hm, "Desktop"),
        "pictures":  os.path.join(hm, "Pictures"),
        "music":     os.path.join(hm, "Music"),
        "videos":    os.path.join(hm, "Videos"),
        "files":     FILES_DIR,
    }
    return mapping.get(name.lower(), os.path.join(hm, name))


def _disk_usage_safe():
    try:
        return psutil.disk_usage("/")
    except Exception:
        try:
            parts = psutil.disk_partitions()
            if parts:
                return psutil.disk_usage(parts[0].mountpoint)
        except Exception:
            pass
    return None


# ─── File operations ──────────────────────────────────────────────────────
def create_file_doc(filename: str, content: str, folder=None) -> str:
    try:
        base = _folder_path(folder) if folder else os.path.join(
            os.path.expanduser("~"), "Documents")
        if os.path.isabs(filename):
            base     = os.path.dirname(filename)
            filename = os.path.basename(filename)
        os.makedirs(base, exist_ok=True)
        if not any(filename.endswith(x) for x in
                   (".txt", ".py", ".html", ".md", ".csv", ".json", ".log")):
            filename += ".txt"
        path = os.path.join(base, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File created at {path}, sir."
    except Exception as e:
        return f"Could not create file: {e}"


def read_file_doc(filename: str) -> str:
    try:
        for p in [filename,
                  os.path.join(os.path.expanduser("~"), "Documents", filename),
                  os.path.join(os.path.expanduser("~"), filename),
                  os.path.join(FILES_DIR, filename)]:
            if os.path.isfile(p):
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    return f"Contents of {os.path.basename(p)}:\n{f.read(3000)}"
        return f"File '{filename}' not found, sir."
    except Exception as e:
        return f"Could not read file: {e}"


def delete_file_doc(filename: str) -> str:
    try:
        for p in [filename,
                  os.path.join(os.path.expanduser("~"), "Documents", filename),
                  os.path.join(FILES_DIR, filename)]:
            if os.path.isfile(p):
                os.remove(p)
                return "File deleted, sir."
        return f"File '{filename}' not found, sir."
    except Exception as e:
        return f"Could not delete: {e}"


def list_files_in(folder: str) -> str:
    try:
        path  = _folder_path(folder)
        if not os.path.isdir(path):
            return f"Folder '{folder}' not found, sir."
        items = sorted(os.listdir(path))[:25]
        return (f"Files in {folder}: " + ", ".join(items)) if items \
               else f"{folder} is empty, sir."
    except Exception as e:
        return f"Could not list: {e}"


def open_path(path: str) -> str:
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return f"Opened {os.path.basename(path)}, sir."
    except Exception as e:
        return f"Could not open: {e}"


def close_window_by_name(name: str) -> str:
    name_l = name.lower()
    killed = []
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if name_l in (proc.info["name"] or "").lower():
                proc.terminate()
                killed.append(proc.info["name"])
        except Exception:
            pass
    if killed:
        return f"Closed {', '.join(set(killed))}, sir."
    return f"Could not find '{name}' to close, sir."


def open_app(exe: str, name: str) -> str:
    try:
        if exe.startswith("ms-") or exe.endswith(":"):
            subprocess.Popen(f"start {exe}", shell=True)
        else:
            subprocess.Popen(exe, shell=True)
        return f"Opening {name.title()}, sir."
    except Exception as e:
        return f"Could not open {name}: {e}, sir."


# ─── Power commands ───────────────────────────────────────────────────────
def shutdown_system():
    if platform.system() == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "5"])
    else:
        subprocess.run(["sudo", "shutdown", "-h", "now"])


def restart_system():
    if platform.system() == "Windows":
        subprocess.run(["shutdown", "/r", "/t", "5"])
    else:
        subprocess.run(["sudo", "shutdown", "-r", "now"])


def lock_system() -> str:
    if platform.system() == "Windows":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Workstation locked, sir."
    elif platform.system() == "Darwin":
        subprocess.run(["pmset", "displaysleepnow"])
        return "Display locked, sir."
    return "Lock command sent, sir."


# ─── Email ────────────────────────────────────────────────────────────────
def send_email(to_addr: str, subject: str, body: str) -> str:
    if not cfg.GMAIL_USER or not cfg.GMAIL_PASS:
        return ("Email credentials not configured. "
                "Please set them in Settings, sir.")
    try:
        msg              = email.mime.multipart.MIMEMultipart()
        msg["From"]      = cfg.GMAIL_USER
        msg["To"]        = to_addr
        msg["Subject"]   = subject
        msg.attach(email.mime.text.MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(cfg.GMAIL_USER, cfg.GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return f"Email sent to {to_addr} successfully, sir."
    except Exception as e:
        return f"Failed to send email: {e}"


# ─── System information ───────────────────────────────────────────────────
def get_system_info(full: bool = False) -> str:
    try:
        vm    = psutil.virtual_memory()
        du    = _disk_usage_safe()
        bat   = psutil.sensors_battery()
        cpu_f = psutil.cpu_freq()

        if not full:
            return (
                f"Running {platform.system()} {platform.release()}, "
                f"CPU at {psutil.cpu_percent():.0f} percent, "
                f"RAM at {vm.percent:.0f} percent "
                f"with {vm.available//1024**2} megabytes free, sir."
            )

        lines = [
            f"OS: {platform.system()} {platform.release()} {platform.version()}",
            f"Machine: {platform.machine()}  |  Processor: {platform.processor()[:60]}",
            f"CPU Cores: {psutil.cpu_count(False)} physical, {psutil.cpu_count()} logical",
        ]
        if cpu_f:
            lines.append(
                f"CPU Freq: {cpu_f.current:.0f} MHz (max {cpu_f.max:.0f} MHz)"
            )
        lines.append(f"CPU Usage: {psutil.cpu_percent()}%")
        lines.append(
            f"RAM: {vm.total//1024**3} GB total, "
            f"{vm.used//1024**3} GB used ({vm.percent}%)"
        )
        if du:
            lines.append(
                f"Disk: {du.total//1024**3} GB total, "
                f"{du.free//1024**3} GB free ({du.percent}% used)"
            )
        if bat:
            lines.append(
                f"Battery: {bat.percent:.0f}% "
                f"{'(Charging)' if bat.power_plugged else '(On Battery)'}"
            )
        lines.append(f"Hostname: {socket.gethostname()}")
        try:
            lines.append(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
        except Exception:
            pass
        bt2 = datetime.datetime.fromtimestamp(psutil.boot_time())
        up  = datetime.datetime.now() - bt2
        h, r = divmod(int(up.total_seconds()), 3600)
        m2, s = divmod(r, 60)
        lines.append(f"Uptime: {h}h {m2}m {s}s")
        return "\n".join(lines)
    except Exception as e:
        return f"System info error: {e}"


def get_battery() -> str:
    bat = psutil.sensors_battery()
    if bat:
        return (f"Battery at {bat.percent:.0f} percent, "
                f"{'charging' if bat.power_plugged else 'discharging'}, sir.")
    return "No battery sensor detected, sir."


def get_uptime() -> str:
    bt = datetime.datetime.fromtimestamp(psutil.boot_time())
    up = datetime.datetime.now() - bt
    h, r = divmod(int(up.total_seconds()), 3600)
    m2, s = divmod(r, 60)
    return (f"System has been running for {h} hours, "
            f"{m2} minutes, and {s} seconds, sir.")


def get_disk_info() -> str:
    du = _disk_usage_safe()
    if du:
        return (f"Disk: {du.total//1024**3} gigabytes total, "
                f"{du.free//1024**3} gigabytes free, sir.")
    return "Could not read disk info, sir."


def get_ip_address() -> str:
    try:
        ip = socket.gethostbyname(socket.gethostname())
        return f"Local IP address is {ip}, sir."
    except Exception:
        return "Could not retrieve IP address, sir."


def get_network_info() -> str:
    try:
        net_addrs = psutil.net_if_addrs()
        net_stats = psutil.net_if_stats()
        lines     = []
        for iface, addrs in list(net_addrs.items())[:4]:
            stat   = net_stats.get(iface)
            status = "UP" if (stat and stat.isup) else "DOWN"
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    lines.append(f"{iface}: {addr.address} ({status})")
        return ("Network interfaces: " + ", ".join(lines)) if lines \
               else "No network interfaces found, sir."
    except Exception:
        return "Could not retrieve network info, sir."


def get_processes() -> str:
    try:
        procs = sorted(
            psutil.process_iter(["name", "cpu_percent", "memory_percent"]),
            key=lambda p: p.info["cpu_percent"] or 0,
            reverse=True,
        )[:5]
        lines = [
            f"{(p.info['name'] or 'Unknown')[:20]}: "
            f"CPU {p.info['cpu_percent']:.1f}%"
            for p in procs
        ]
        return "Top processes: " + ", ".join(lines) + ", sir."
    except Exception:
        return "Could not list processes, sir."


def check_internet() -> str:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "Internet connection active, sir. All systems connected."
    except Exception:
        return "No internet connection detected, sir. Check your network."


# ─── Math helpers ─────────────────────────────────────────────────────────
def evaluate_math(raw: str, cmd: str) -> str:
    expr = re.sub(
        r"(calculate the?|calculate|compute|how much is|math|"
        r"evaluate|kitna hai|solve)", "", cmd
    ).strip()
    expr = re.sub(r"\b(times|multiplied by|into)\b", "*", expr)
    expr = re.sub(r"\b(divided by|over)\b",           "/", expr)
    expr = re.sub(r"\b(plus|added to)\b",             "+", expr)
    expr = re.sub(r"\b(minus|subtract)\b",             "-", expr)
    expr = re.sub(r"\b(to the power of|\^)\b",        "**", expr)
    expr = re.sub(r"[^0-9+\-*/().\s%]", "", expr).strip()
    if expr and re.search(r"\d", expr):
        try:
            result = eval(
                expr,
                {"__builtins__": {}, "pow": pow, "abs": abs, "round": round},
            )
            return f"The result is {result:,g}, sir."
        except Exception:
            pass
    return "Could not evaluate that expression, sir."


def convert_units(raw: str, cmd: str) -> str:
    m = re.search(
        r"(\d+\.?\d*)\s*(km|miles?|kg|lbs?|pounds?|celsius|fahrenheit|"
        r"meters?|feet|foot|inches?|liters?|gallons?|cm)", cmd
    )
    if not m:
        return "Could not parse the conversion, sir."
    val = float(m.group(1))
    u   = m.group(2).lower().rstrip("s")
    table = {
        "km":         (val * 0.621371,  "miles"),
        "mile":       (val * 1.60934,   "km"),
        "kg":         (val * 2.20462,   "lbs"),
        "lb":         (val * 0.453592,  "kg"),
        "pound":      (val * 0.453592,  "kg"),
        "celsius":    (val * 9/5 + 32,  "Fahrenheit"),
        "fahrenheit": ((val-32)*5/9,    "Celsius"),
        "meter":      (val * 3.28084,   "feet"),
        "foot":       (val * 0.3048,    "meters"),
        "feet":       (val * 0.3048,    "meters"),
        "inch":       (val * 2.54,      "centimeters"),
        "cm":         (val * 0.393701,  "inches"),
        "liter":      (val * 0.264172,  "gallons"),
        "gallon":     (val * 3.78541,   "liters"),
    }
    if u in table:
        rv, tu = table[u]
        return f"{val} {m.group(2)} equals {rv:.4g} {tu}, sir."
    return f"No conversion available for '{m.group(2)}', sir."


def get_weather(city: str) -> str:
    """Try wttr.in then fall back to browser."""
    from core.deps import REQ_OK, requests
    import webbrowser
    if REQ_OK:
        try:
            r = requests.get(
                f"https://wttr.in/{city.replace(' ','+')}?format=3",
                timeout=6,
            )
            if r.status_code == 200 and r.text.strip():
                return r.text.strip() + ", sir."
        except Exception:
            pass
    webbrowser.open(
        f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}"
    )
    return f"Opening weather for {city} in your browser, sir."