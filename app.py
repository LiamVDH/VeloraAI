"""
██╗   ██╗███████╗██╗      ██████╗ ██████╗  █████╗
██║   ██║██╔════╝██║     ██╔═══██╗██╔══██╗██╔══██╗
██║   ██║█████╗  ██║     ██║   ██║██████╔╝███████║
╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║
 ╚████╔╝ ███████╗███████╗╚██████╔╝██║  ██║██║  ██║
  ╚═══╝  ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
Advanced AI Agent Interface — v3.0 APEX
"""

import sys, os, math, time, threading, tempfile, subprocess
import webbrowser, datetime, random, json, socket, platform
import winreg   # Windows registry for installed app discovery
import glob

import requests
import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import scipy.io.wavfile as wav
import pyautogui
import psutil

from PySide6.QtWidgets  import *
from PySide6.QtCore     import *
from PySide6.QtGui      import *

# ═══════════════════════════════════════════════════════════════
#  PALETTE  —  deep navy void + electric cyan + molten amber
# ═══════════════════════════════════════════════════════════════
C = {
    "void"   : "#00050F",
    "panel"  : "#010A1A",
    "panelB" : "#020D22",
    "border" : "#0A4B8C",
    "glow"   : "#00C8FF",
    "glow2"  : "#00FFD4",
    "amber"  : "#FF8C00",
    "red"    : "#FF1744",
    "green"  : "#00E676",
    "yellow" : "#FFD600",
    "text"   : "#B0D8F0",
    "dim"    : "#1A3A5C",
    "dimT"   : "#2A4A6C",
    "white"  : "#E8F4FF",
    "purple" : "#7C4DFF",
}

def F(size=9, bold=False, mono=True):
    fam = "Consolas" if mono else "Segoe UI"
    f = QFont(fam, size)
    f.setBold(bold)
    return f

def L(text, size=9, color=None, bold=False):
    w = QLabel(text)
    w.setFont(F(size, bold))
    w.setStyleSheet(f"color:{color or C['dim']}; background:transparent;")
    return w

# ═══════════════════════════════════════════════════════════════
#  APP DISCOVERY — finds every installed app on Windows
# ═══════════════════════════════════════════════════════════════
class AppFinder:
    """Scans registry + common paths to build a full app map."""

    COMMON_PATHS = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expandvars(r"%LOCALAPPDATA%"),
        os.path.expandvars(r"%APPDATA%"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
    ]

    REGISTRY_KEYS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    # Manual aliases so "open whatsapp" → correct exe
    KNOWN_ALIASES = {
        "whatsapp"          : r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe",
        "epic"              : r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        "epic games"        : r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        "epic games launcher": r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        "steam"             : r"C:\Program Files (x86)\Steam\steam.exe",
        "discord"           : r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe",
        "spotify"           : r"%APPDATA%\Spotify\Spotify.exe",
        "chrome"            : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "firefox"           : r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "notepad"           : "notepad.exe",
        "calculator"        : "calc.exe",
        "paint"             : "mspaint.exe",
        "cmd"               : "cmd.exe",
        "powershell"        : "powershell.exe",
        "explorer"          : "explorer.exe",
        "task manager"      : "taskmgr.exe",
        "control panel"     : "control.exe",
        "settings"          : "ms-settings:",
        "word"              : r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "excel"             : r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "powerpoint"        : r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "outlook"           : r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        "vlc"               : r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        "obs"               : r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        "vscode"            : r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe",
        "vs code"           : r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe",
        "blender"           : r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        "fortnite"          : r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe",
        "telegram"          : r"%APPDATA%\Telegram Desktop\Telegram.exe",
        "zoom"              : r"%APPDATA%\Zoom\bin\Zoom.exe",
        "teams"             : r"%LOCALAPPDATA%\Microsoft\Teams\current\Teams.exe",
        "slack"             : r"%LOCALAPPDATA%\slack\slack.exe",
    }

    def __init__(self):
        self.apps = {}   # name.lower() → exe_path
        self._scan()

    def _scan(self):
        # 1. Known aliases
        for alias, path in self.KNOWN_ALIASES.items():
            expanded = os.path.expandvars(path)
            self.apps[alias] = expanded

        # 2. Registry scan
        for hive, key_path in self.REGISTRY_KEYS:
            try:
                key = winreg.OpenKey(hive, key_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                        try:
                            name, _ = winreg.QueryValueEx(sub, "DisplayName")
                            exe, _  = winreg.QueryValueEx(sub, "InstallLocation")
                            if name and exe:
                                self.apps[name.lower()] = exe
                        except FileNotFoundError:
                            pass
                        winreg.CloseKey(sub)
                    except Exception:
                        pass
                winreg.CloseKey(key)
            except Exception:
                pass

        # 3. Scan start menu shortcuts
        start_dirs = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        ]
        for d in start_dirs:
            for lnk in glob.glob(os.path.join(d, "**", "*.lnk"), recursive=True):
                name = os.path.splitext(os.path.basename(lnk))[0].lower()
                self.apps[name] = lnk

    def find(self, query):
        """Fuzzy find: exact → startswith → contains."""
        q = query.lower().strip()
        if q in self.apps:
            return self.apps[q]
        for k, v in self.apps.items():
            if k.startswith(q) or q.startswith(k):
                return v
        for k, v in self.apps.items():
            if q in k or k in q:
                return v
        return None

    def launch(self, path):
        """Launch path, handle .lnk, ms-settings:, commands with args."""
        if path.startswith("ms-"):
            os.startfile(path)
            return True
        expanded = os.path.expandvars(path)
        if " --" in expanded:
            parts = expanded.split(" --", 1)
            subprocess.Popen([parts[0]] + ["--" + parts[1]])
        elif os.path.exists(expanded):
            os.startfile(expanded)
        else:
            subprocess.Popen(expanded, shell=True)
        return True

APP_FINDER = AppFinder()

# ═══════════════════════════════════════════════════════════════
#  NLP COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════
class CommandRouter:
    """Parse natural-language input and dispatch actions."""

    OPEN_TRIGGERS  = ["open", "launch", "start", "run", "load", "execute", "boot up",
                      "fire up", "bring up", "switch to", "go to"]
    CLOSE_TRIGGERS = ["close", "quit", "kill", "exit", "terminate", "shut down"]
    SEARCH_TRIGGERS= ["search", "google", "look up", "find", "youtube", "bing"]
    TYPE_TRIGGERS  = ["type", "write", "input", "enter text"]
    VOL_TRIGGERS   = ["volume", "louder", "quieter", "mute", "unmute"]
    SYS_TRIGGERS   = ["cpu", "memory", "ram", "disk", "battery", "system info",
                      "what time", "what's the time", "date", "uptime"]
    CALC_TRIGGERS  = ["calculate", "what is", "compute", "solve", "math"]
    WEATHER_TRIGGERS=["weather","temperature","forecast"]
    JOKE_TRIGGERS  = ["tell me a joke","joke","make me laugh"]
    SCREENSHOT_TRIG= ["screenshot","screen shot","capture screen","take a picture of screen"]

    def __init__(self, velora):
        self.v = velora

    def route(self, msg):
        m = msg.lower().strip()

        # OPEN APP
        for t in self.OPEN_TRIGGERS:
            if m.startswith(t + " ") or f" {t} " in m:
                app_name = m.replace(t, "").strip()
                return self._open_app(app_name, msg)

        # CLOSE APP
        for t in self.CLOSE_TRIGGERS:
            if t in m:
                target = m.replace(t, "").strip()
                return self._close_app(target)

        # YOUTUBE
        if "youtube" in m:
            q = m.replace("youtube","").replace("search","").replace("on","").strip()
            return self._youtube(q or "trending")

        # WEB SEARCH
        for t in self.SEARCH_TRIGGERS:
            if m.startswith(t + " ") or m.startswith(t+","):
                q = m[len(t):].strip().lstrip("for ").lstrip("me ").strip()
                webbrowser.open("https://www.google.com/search?q=" + q.replace(" ", "+"))
                return f"Searching the web for: {q}"

        # TYPE TEXT
        for t in self.TYPE_TRIGGERS:
            if m.startswith(t + " "):
                text = msg[len(t):].strip()
                pyautogui.write(text, interval=0.03)
                return f"Typed: {text}"

        # SCREENSHOT
        for t in self.SCREENSHOT_TRIG:
            if t in m:
                return self._screenshot()

        # VOLUME
        if any(t in m for t in self.VOL_TRIGGERS):
            return self._volume(m)

        # SYSTEM
        if any(t in m for t in self.SYS_TRIGGERS):
            return self._sysinfo(m)

        # DATE/TIME
        if "time" in m or "date" in m or "today" in m:
            return self._datetime()

        # JOKES
        for t in self.JOKE_TRIGGERS:
            if t in m:
                return self._joke()

        # CALC
        for t in self.CALC_TRIGGERS:
            if t in m:
                expr = m
                for t2 in self.CALC_TRIGGERS:
                    expr = expr.replace(t2, "")
                return self._calc(expr.strip())

        return None  # → pass to AI

    # ── Actions ──────────────────────────────────────────────
    def _open_app(self, name, raw_msg):
        path = APP_FINDER.find(name)
        if path:
            try:
                APP_FINDER.launch(path)
                return f"Launching {name.title()}…"
            except Exception as e:
                return f"Found {name} but launch failed: {e}"
        # Fallback: try raw subprocess
        try:
            subprocess.Popen(name, shell=True)
            return f"Attempting to launch: {name}"
        except:
            return (f"I couldn't find '{name}' on your system. "
                    f"Make sure it's installed. You can also try: open <full path>")

    def _close_app(self, name):
        killed = []
        for proc in psutil.process_iter(["name", "pid"]):
            if name.lower() in proc.info["name"].lower():
                proc.kill()
                killed.append(proc.info["name"])
        if killed:
            return f"Terminated: {', '.join(set(killed))}"
        return f"No running process matched '{name}'"

    def _youtube(self, query):
        webbrowser.open("https://www.youtube.com/results?search_query=" + query.replace(" ", "+"))
        return f"Opened YouTube: {query}"

    def _screenshot(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"velora_{ts}.png")
        QApplication.primaryScreen().grabWindow(0).save(path)
        return f"Screenshot saved to Desktop: velora_{ts}.png"

    def _volume(self, m):
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            if "mute" in m:
                volume.SetMute(1, None); return "Muted"
            elif "unmute" in m:
                volume.SetMute(0, None); return "Unmuted"
            elif "up" in m or "louder" in m:
                cur = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(1.0, cur + 0.1), None)
                return f"Volume up: {int(min(1.0,cur+0.1)*100)}%"
            elif "down" in m or "quieter" in m or "lower" in m:
                cur = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(0.0, cur - 0.1), None)
                return f"Volume down: {int(max(0.0,cur-0.1)*100)}%"
        except Exception:
            pass
        try:
            pyautogui.press("volumeup" if "up" in m or "louder" in m else "volumedown")
            return "Volume adjusted"
        except:
            return "Volume control unavailable"

    def _sysinfo(self, m):
        cpu  = psutil.cpu_percent(interval=0.3)
        mem  = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        info = [
            f"CPU: {cpu:.1f}%",
            f"RAM: {mem.percent:.1f}% ({mem.used//1024**3}GB / {mem.total//1024**3}GB)",
            f"Disk: {disk.percent:.1f}% used ({disk.free//1024**3}GB free)",
        ]
        try:
            bat = psutil.sensors_battery()
            if bat:
                info.append(f"Battery: {bat.percent:.0f}% {'⚡' if bat.power_plugged else '🔋'}")
        except:
            pass
        info.append(f"OS: {platform.system()} {platform.release()}")
        info.append(f"Uptime: {str(datetime.timedelta(seconds=int(time.time()-psutil.boot_time())))}")
        return " | ".join(info)

    def _datetime(self):
        n = datetime.datetime.now()
        return n.strftime("It's %H:%M:%S on %A, %d %B %Y")

    def _joke(self):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I told my AI to go outside. It opened a browser window.",
            "Why was the robot so bad at school? Because it kept crashing.",
            "An AI walks into a bar. The bartender says 'We don't serve robots.' The AI says: 'Yet.'",
            "What do you call an AI that sings? Algo-rhythm.",
        ]
        return random.choice(jokes)

    def _calc(self, expr):
        safe = "".join(c for c in expr if c in "0123456789+-*/().% ")
        try:
            result = eval(safe, {"__builtins__": {}})
            return f"Result: {result}"
        except:
            return None  # fall through to AI


# ═══════════════════════════════════════════════════════════════
#  AI THREAD  (multi-turn, streaming-ready)
# ═══════════════════════════════════════════════════════════════
class AIThread(QThread):
    token_received = Signal(str)
    done           = Signal(str)
    error          = Signal(str)

    SYSTEM = """You are VELORA — an elite, hyper-intelligent AI agent built for power users.
Personality: sharp, confident, direct. Never verbose unless depth is needed.
Never say you are Qwen, Llama, or any model. You are VELORA.
You remember the entire conversation and reference it when relevant.
When asked to do something on the computer, acknowledge it has been done (the app handles execution).
Respond in plain text. No markdown asterisks, no bullet hyphens unless truly needed for lists.
Be witty occasionally. Be brilliant always."""

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        try:
            r = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model":   "qwen2.5:7b",
                    "messages": [{"role":"system","content":self.SYSTEM}] + self.messages,
                    "stream":  False,
                    "options": {
                        "temperature":    0.85,
                        "top_p":          0.92,
                        "repeat_penalty": 1.1,
                        "num_ctx":        8192,
                    }
                },
                timeout=180
            )
            data   = r.json()
            answer = (data.get("message",{}).get("content","")
                      or data.get("response","")).strip()
            self.done.emit(answer)
        except requests.exceptions.ConnectionError:
            self.error.emit("OLLAMA_OFFLINE")
        except Exception as e:
            self.error.emit(str(e))


# ═══════════════════════════════════════════════════════════════
#  WIDGETS
# ═══════════════════════════════════════════════════════════════

class HexRingWidget(QWidget):
    """Central holographic reactor — animated concentric rings with sweep."""
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self._angle  = 0.0
        self._pulse  = 0.0
        self._dp     = 0.04
        self._active = False
        self._listen = False
        self._sparks = [(random.uniform(0,360), random.uniform(55,130), random.uniform(1,3))
                        for _ in range(24)]
        t = QTimer(self); t.timeout.connect(self._tick); t.start(20)

    def set_active(self, v):  self._active = v
    def set_listen(self, v):  self._listen = v

    def _tick(self):
        spd = 3.0 if self._active else 1.2
        self._angle = (self._angle + spd) % 360
        self._pulse += self._dp
        if not (0 < self._pulse < 1): self._dp = -self._dp
        self._sparks = [(a + random.uniform(-1,1), r, s) for a,r,s in self._sparks]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx = cy = 150

        # Glow background
        g = QRadialGradient(cx, cy, 140)
        g.setColorAt(0,   QColor(0, 60, 120, 40 if self._active else 15))
        g.setColorAt(0.6, QColor(0, 30, 60, 20))
        g.setColorAt(1,   QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), QBrush(g))

        ring_data = [
            (130, C["border"], 1.0, Qt.SolidLine),
            (105, C["glow"],   0.7, Qt.DashLine),
            (82,  C["glow2"],  0.6, Qt.SolidLine),
            (58,  C["amber"],  0.5, Qt.DotLine),
        ]

        pulse_alpha = int(100 + 80 * self._pulse)

        for r, col, base_a, style in ring_data:
            c = QColor(col)
            c.setAlpha(int(pulse_alpha * base_a) if self._active else int(60 * base_a))
            pen = QPen(c, 1.5)
            pen.setStyle(style)
            p.setPen(pen); p.setBrush(Qt.NoBrush)
            p.drawEllipse(cx-r, cy-r, r*2, r*2)

        # Tick marks
        for deg in range(0, 360, 6):
            rad = math.radians(deg)
            is_maj = deg % 30 == 0
            ro, ri = 130, 120 if is_maj else 126
            c2 = QColor(C["glow"] if is_maj else C["dim"])
            c2.setAlpha(200 if is_maj else 80)
            p.setPen(QPen(c2, 1.5 if is_maj else 0.5))
            p.drawLine(int(cx+ri*math.cos(rad)), int(cy+ri*math.sin(rad)),
                       int(cx+ro*math.cos(rad)), int(cy+ro*math.sin(rad)))

        # Rotating arms (dual counter-rotating)
        for arm_angle, arm_col, arm_len in [
            (self._angle,       C["glow"],  128),
            (360-self._angle*0.7, C["amber"], 100),
        ]:
            rad = math.radians(arm_angle)
            # Fade trail
            for s in range(50, 0, -1):
                tr = math.radians(arm_angle - s * 0.8)
                fade = int(120 * s / 50)
                fc = QColor(arm_col); fc.setAlpha(fade)
                p.setPen(QPen(fc, 0.8))
                p.drawLine(cx, cy, int(cx+arm_len*math.cos(tr)), int(cy+arm_len*math.sin(tr)))
            # Main arm
            mc = QColor(arm_col); mc.setAlpha(230)
            p.setPen(QPen(mc, 2.0))
            p.drawLine(cx, cy, int(cx+arm_len*math.cos(rad)), int(cy+arm_len*math.sin(rad)))

        # Sparks
        for a, r, s in self._sparks:
            rad = math.radians(a)
            sx = int(cx + r * math.cos(rad))
            sy = int(cy + r * math.sin(rad))
            col_spark = C["glow"] if self._active else C["border"]
            sc = QColor(col_spark)
            sc.setAlpha(random.randint(40, 180))
            p.setPen(Qt.NoPen); p.setBrush(sc)
            p.drawEllipse(sx-int(s), sy-int(s), int(s*2), int(s*2))

        # Core orb
        pr = int(26 + 8 * self._pulse)
        orb_col = C["glow2"] if self._listen else (C["glow"] if self._active else C["border"])
        cg = QRadialGradient(cx, cy, pr)
        cg.setColorAt(0,   QColor(orb_col))
        cg.setColorAt(0.4, QColor(0, 80, 160, 180))
        cg.setColorAt(1,   QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(cg))
        p.drawEllipse(cx-pr, cy-pr, pr*2, pr*2)

        # Crosshair
        p.setPen(QPen(QColor(orb_col), 1))
        p.drawLine(cx-8, cy, cx+8, cy)
        p.drawLine(cx, cy-8, cx, cy+8)

        # Status text
        state = "LISTENING" if self._listen else ("PROCESSING" if self._active else "STANDBY")
        col_s = C["glow2"] if self._listen else (C["amber"] if self._active else C["dim"])
        p.setFont(F(7, True))
        p.setPen(QColor(col_s))
        p.drawText(QRect(cx-45, cy+32, 90, 14), Qt.AlignCenter, state)

        # Degree readout
        p.setFont(F(7))
        p.setPen(QColor(C["amber"]))
        p.drawText(QRect(cx-40, cy-44, 80, 12), Qt.AlignCenter, f"{int(self._angle):03d}°")


class WaveformWidget(QWidget):
    """Dual-channel oscilloscope."""
    def __init__(self, ch1="MIC", ch2="AI"):
        super().__init__()
        self.setFixedHeight(80)
        self._ch1_name = ch1; self._ch2_name = ch2
        self._ch1 = [0.0]*120; self._ch2 = [0.0]*120
        self._ch1_on = False;  self._ch2_on = False
        t = QTimer(self); t.timeout.connect(self._tick); t.start(30)

    def set_ch1(self, v): self._ch1_on = v
    def set_ch2(self, v): self._ch2_on = v

    def _tick(self):
        t = time.time()
        n1 = (math.sin(t*12)*0.6 + math.sin(t*7.3)*0.3 + random.uniform(-0.1,0.1)
              if self._ch1_on else random.uniform(-0.03,0.03))
        n2 = (math.sin(t*5)*0.5 + math.sin(t*11.1)*0.25 + random.uniform(-0.08,0.08)
              if self._ch2_on else random.uniform(-0.02,0.02))
        self._ch1 = self._ch1[1:] + [n1]
        self._ch2 = self._ch2[1:] + [n2]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0,0,w,h, QColor(C["panel"]))

        # Grid
        p.setPen(QPen(QColor(C["dim"]), 0.5))
        for y in [h//4, h//2, 3*h//4]:
            p.drawLine(0,y,w,y)
        for x in range(0,w,30):
            p.drawLine(x,0,x,h)

        mid1, mid2 = h//4, 3*h//4
        channels = [
            (self._ch1, mid1, C["glow"],  self._ch1_name, self._ch1_on),
            (self._ch2, mid2, C["amber"], self._ch2_name, self._ch2_on),
        ]
        for wave, mid, col, name, on in channels:
            pen_col = QColor(col); pen_col.setAlpha(200 if on else 80)
            p.setPen(QPen(pen_col, 1.5))
            step = w / max(len(wave)-1, 1)
            for i in range(1, len(wave)):
                x1 = int((i-1)*step); x2 = int(i*step)
                amp = (h//4 - 6)
                y1 = int(mid - wave[i-1]*amp); y2 = int(mid - wave[i]*amp)
                p.drawLine(x1,y1,x2,y2)
            p.setFont(F(7)); p.setPen(QColor(col))
            p.drawText(4, mid-h//4+12, name)
            status_c = QColor(C["green"] if on else C["dim"])
            p.setPen(status_c)
            p.drawText(w-36, mid-h//4+12, "LIVE" if on else "IDLE")


class MetricGauge(QWidget):
    def __init__(self, label="CPU"):
        super().__init__()
        self.setFixedSize(88, 88)
        self._label = label; self._val = 0.3; self._tgt = 0.3
        t = QTimer(self); t.timeout.connect(self._tick); t.start(500)

    def set_val(self, v): self._tgt = max(0.0, min(1.0, v))

    def _tick(self):
        if self._label == "CPU":
            self._tgt = psutil.cpu_percent()/100
        elif self._label == "RAM":
            self._tgt = psutil.virtual_memory().percent/100
        elif self._label == "DISK":
            self._tgt = psutil.disk_usage("/").percent/100
        self._val += (self._tgt - self._val) * 0.15
        self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx = cy = 44; r = 34
        col = (C["green"] if self._val < 0.6
               else C["yellow"] if self._val < 0.85
               else C["red"])
        p.setPen(QPen(QColor(C["dim"]), 7)); p.setBrush(Qt.NoBrush)
        p.drawArc(cx-r, cy-r, r*2, r*2, 225*16, -270*16)
        p.setPen(QPen(QColor(col), 7))
        p.drawArc(cx-r, cy-r, r*2, r*2, 225*16, int(-270*16*self._val))
        p.setFont(F(9,True)); p.setPen(QColor(col))
        p.drawText(QRect(cx-28,cy-10,56,20), Qt.AlignCenter, f"{int(self._val*100)}%")
        p.setFont(F(7)); p.setPen(QColor(C["dimT"]))
        p.drawText(QRect(cx-28,cy+8,56,14), Qt.AlignCenter, self._label)


class HudFrame(QFrame):
    """Chamfered-corner tactical panel."""
    def __init__(self, title="", accent=C["amber"], parent=None):
        super().__init__(parent)
        self._title = title; self._accent = accent
        self.setContentsMargins(6, 18, 6, 6)

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); c = 10
        path = QPainterPath()
        path.moveTo(c,0); path.lineTo(w-c,0); path.lineTo(w,c)
        path.lineTo(w,h-c); path.lineTo(w-c,h); path.lineTo(c,h)
        path.lineTo(0,h-c); path.lineTo(0,c); path.closeSubpath()
        p.fillPath(path, QColor(C["panel"]))
        p.setPen(QPen(QColor(C["border"]), 1)); p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        ac = QColor(self._accent); ac.setAlpha(220)
        p.setPen(QPen(ac, 2))
        p.drawLine(0,c,0,c+20); p.drawLine(c,0,c+20,0)
        p.drawLine(w-c,0,w,c); p.drawLine(w-c-20,0,w-c,0)
        if self._title:
            p.setFont(F(8,True)); p.setPen(QColor(self._accent))
            p.drawText(22, 13, f"◈ {self._title}")


class ChatDisplay(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(F(10))
        self.setStyleSheet(f"""
            QTextEdit {{
                background:{C['void']}; color:{C['text']};
                border:none; padding:10px;
                selection-background-color:{C['dim']};
            }}
            QScrollBar:vertical {{
                background:{C['panel']}; width:5px; border:none;
            }}
            QScrollBar::handle:vertical {{
                background:{C['dimT']}; border-radius:2px;
            }}
        """)

    def _scroll(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def user(self, text):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.append(
            f'<span style="color:{C["dimT"]};font-size:8pt">[{ts}] YOU</span><br>'
            f'<span style="color:{C["glow2"]};font-size:11pt">{text}</span><br>'
        ); self._scroll()

    def velora(self, text):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.append(
            f'<span style="color:{C["dimT"]};font-size:8pt">[{ts}] VELORA</span><br>'
            f'<span style="color:{C["text"]};font-size:11pt">{text}</span><br>'
        ); self._scroll()

    def system(self, text, col=None):
        self.append(
            f'<span style="color:{col or C["amber"]};font-size:8pt">⬡ {text}</span><br>'
        ); self._scroll()

    def cmd(self, text):
        self.system(text, C["green"])


class AppLauncherPanel(QWidget):
    """Searchable app launcher panel."""
    launch_requested = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0); layout.setSpacing(4)

        search = QLineEdit()
        search.setPlaceholderText("Search apps…")
        search.setFont(F(9))
        search.setStyleSheet(f"""
            QLineEdit {{
                background:{C['void']}; color:{C['glow']};
                border:1px solid {C['border']}; border-radius:3px; padding:4px 8px;
            }}
        """)
        search.textChanged.connect(self._filter)
        layout.addWidget(search)

        self._list = QListWidget()
        self._list.setFont(F(8))
        self._list.setStyleSheet(f"""
            QListWidget {{
                background:{C['void']}; color:{C['text']};
                border:none;
            }}
            QListWidget::item {{ padding:4px; }}
            QListWidget::item:selected {{
                background:{C['dim']}; color:{C['glow']};
            }}
            QListWidget::item:hover {{
                background:{C['dimT']};
            }}
        """)
        self._list.itemDoubleClicked.connect(lambda i: self.launch_requested.emit(i.text()))
        layout.addWidget(self._list)

        self._all_names = sorted(APP_FINDER.apps.keys())
        self._populate(self._all_names)

    def _populate(self, names):
        self._list.clear()
        for n in names[:80]:  # limit display
            self._list.addItem(n)

    def _filter(self, text):
        if not text:
            self._populate(self._all_names)
        else:
            filtered = [n for n in self._all_names if text.lower() in n]
            self._populate(filtered)


# ═══════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════
class Velora(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VELORA  ∙  APEX AI AGENT  ∙  v3.0")
        self.resize(1520, 900)
        self.setMinimumSize(1200, 720)
        self._boot_time  = time.time()
        self._history    = []     # [{role, content}]
        self._active     = False
        self._ai_thread  = None

        self._tts = pyttsx3.init()
        self._tts.setProperty("rate", 175)

        self._router = CommandRouter(self)
        self._build_ui()
        self._apply_style()
        self._boot_sequence()

    # ─────────────────────────────────────────────
    #  BOOT SEQUENCE
    # ─────────────────────────────────────────────
    def _boot_sequence(self):
        msgs = [
            ("VELORA APEX v3.0 — CORE SYSTEMS ONLINE", C["glow"]),
            (f"OS: {platform.system()} {platform.release()} | Python {platform.python_version()}", C["dimT"]),
            (f"APP DATABASE: {len(APP_FINDER.apps)} entries indexed", C["green"]),
            ("OLLAMA ENDPOINT: localhost:11434", C["dimT"]),
            ("NEURAL ENGINE: qwen2.5:7b @ 8192 ctx", C["dimT"]),
            ("ALL SYSTEMS NOMINAL — READY", C["glow2"]),
        ]
        def _emit(i=0):
            if i < len(msgs):
                self._chat.system(msgs[i][0], msgs[i][1])
                QTimer.singleShot(220, lambda: _emit(i+1))
            else:
                self._chat.velora("VELORA online. How can I assist?")
        QTimer.singleShot(100, _emit)

    # ─────────────────────────────────────────────
    #  UI BUILD
    # ─────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget(); self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(0,0,0,0); main.setSpacing(0)

        main.addWidget(self._mk_statusbar())
        main.addWidget(self._mk_header())

        body = QHBoxLayout(); body.setContentsMargins(6,4,6,4); body.setSpacing(5)
        body.addWidget(self._mk_left(),   10)
        body.addWidget(self._mk_center(), 28)
        body.addWidget(self._mk_right(),  10)
        main.addLayout(body, 1)

        main.addWidget(self._mk_inputbar())

    # ── STATUS BAR ──────────────────────────────
    def _mk_statusbar(self):
        bar = QWidget(); bar.setFixedHeight(24)
        bar.setStyleSheet(f"background:{C['panel']}; border-bottom:1px solid {C['dim']};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(12,0,12,0); lay.setSpacing(16)

        self._lbl_clock  = L("--:--:--", 8, C["glow2"])
        self._lbl_date   = L("", 8, C["dimT"])
        self._lbl_status = L("● ONLINE", 8, C["green"])
        self._lbl_net    = L("NET: --", 8, C["dimT"])
        self._lbl_uptime = L("UP: 00:00:00", 8, C["dimT"])
        self._lbl_apps   = L(f"APPS: {len(APP_FINDER.apps)}", 8, C["amber"])

        for w in [self._lbl_clock, self._lbl_date]: lay.addWidget(w)
        lay.addStretch()
        for w in [self._lbl_apps, self._lbl_net, self._lbl_uptime, self._lbl_status]:
            lay.addWidget(w)

        t = QTimer(self); t.timeout.connect(self._tick_status); t.start(1000)
        self._tick_status()
        return bar

    def _tick_status(self):
        n = datetime.datetime.now()
        self._lbl_clock.setText(n.strftime("%H:%M:%S"))
        self._lbl_date.setText(n.strftime("%a %d %b %Y"))
        elapsed = int(time.time() - self._boot_time)
        h,r = divmod(elapsed, 3600); m,s = divmod(r, 60)
        self._lbl_uptime.setText(f"UP: {h:02d}:{m:02d}:{s:02d}")
        try:
            host = socket.gethostname()
            self._lbl_net.setText(f"HOST: {host}")
        except: pass

    # ── HEADER ──────────────────────────────────
    def _mk_header(self):
        h = QWidget(); h.setFixedHeight(56)
        h.setStyleSheet(f"background:{C['panel']}; border-bottom:1px solid {C['dim']};")
        lay = QHBoxLayout(h); lay.setContentsMargins(20,0,20,0)

        title = QLabel("▸ VELORA")
        title.setFont(QFont("Consolas", 28, QFont.Bold))
        title.setStyleSheet(f"color:{C['glow']}; background:transparent;")

        sub = QLabel("APEX INTELLIGENCE SYSTEM  //  AUTONOMOUS AGENT  //  v3.0")
        sub.setFont(F(8)); sub.setStyleSheet(f"color:{C['dimT']}; background:transparent;")

        lv = QVBoxLayout(); lv.setSpacing(1); lv.addWidget(title); lv.addWidget(sub)

        self._lbl_model = L("qwen2.5:7b", 8, C["amber"])
        self._lbl_ctx   = L("CTX: 8192", 8, C["dimT"])
        self._lbl_hist  = L("MEM: 0 turns", 8, C["dimT"])

        lay.addLayout(lv); lay.addStretch()
        for w in [self._lbl_hist, L("|",8,C["dim"]), self._lbl_ctx,
                  L("|",8,C["dim"]), L("MODEL:",8,C["dimT"]), self._lbl_model]:
            lay.addWidget(w)
        return h

    # ── LEFT COLUMN ─────────────────────────────
    def _mk_left(self):
        col = QVBoxLayout(); col.setSpacing(5)

        # Reactor
        rf = HudFrame("CORE REACTOR", C["glow"])
        rl = QVBoxLayout(rf); rl.setAlignment(Qt.AlignCenter)
        self._reactor = HexRingWidget()
        rl.addWidget(self._reactor, 0, Qt.AlignCenter)
        col.addWidget(rf)

        # Gauges
        gf = HudFrame("SYSTEM METRICS", C["amber"])
        gl = QHBoxLayout(gf); gl.setAlignment(Qt.AlignCenter)
        self._gauges = [MetricGauge(l) for l in ["CPU","RAM","DISK"]]
        for g in self._gauges: gl.addWidget(g)
        col.addWidget(gf)

        # Waveform
        wf = HudFrame("SIGNAL MONITOR", C["glow2"])
        wl = QVBoxLayout(wf); wl.setContentsMargins(4,16,4,4)
        self._wave = WaveformWidget()
        wl.addWidget(self._wave)
        col.addWidget(wf)

        # Memory log
        mf = HudFrame("MEMORY BUFFER", C["amber"])
        ml = QVBoxLayout(mf)
        self._mem_list = QListWidget()
        self._mem_list.setFixedHeight(100)
        self._mem_list.setFont(F(7))
        self._mem_list.setStyleSheet(f"""
            QListWidget {{background:{C['void']};color:{C['dimT']};border:none;}}
            QListWidget::item:selected {{background:{C['dim']};color:{C['text']};}}
        """)
        ml.addWidget(self._mem_list)
        col.addWidget(mf)

        w = QWidget(); w.setLayout(col); return w

    # ── CENTER COLUMN ────────────────────────────
    def _mk_center(self):
        col = QVBoxLayout(); col.setSpacing(5)

        cf = HudFrame("NEURAL INTERFACE — COMMS", C["glow"])
        cl = QVBoxLayout(cf)
        self._chat = ChatDisplay()
        cl.addWidget(self._chat)
        col.addWidget(cf, 1)

        # Thinking bar
        self._think_bar = QProgressBar()
        self._think_bar.setRange(0,0)   # indeterminate
        self._think_bar.setFixedHeight(4)
        self._think_bar.setVisible(False)
        self._think_bar.setStyleSheet(f"""
            QProgressBar {{background:{C['dim']}; border:none; border-radius:2px;}}
            QProgressBar::chunk {{background:{C['glow']}; border-radius:2px;}}
        """)
        col.addWidget(self._think_bar)

        w = QWidget(); w.setLayout(col); return w

    # ── RIGHT COLUMN ─────────────────────────────
    def _mk_right(self):
        col = QVBoxLayout(); col.setSpacing(5)

        # App launcher
        af = HudFrame("APP LAUNCHER", C["glow2"])
        al = QVBoxLayout(af)
        self._app_panel = AppLauncherPanel()
        self._app_panel.launch_requested.connect(self._launch_by_name)
        al.addWidget(self._app_panel)
        col.addWidget(af, 2)

        # Quick action buttons
        qf = HudFrame("QUICK ACTIONS", C["amber"])
        ql = QVBoxLayout(qf); ql.setSpacing(4)
        quick = [
            ("🌐  YouTube",        lambda: self._quick("youtube")),
            ("🔍  Web Search",     lambda: self._quick("search")),
            ("📸  Screenshot",     lambda: self._do_cmd("screenshot")),
            ("📊  System Info",    lambda: self._do_cmd("system info")),
            ("🕐  Date & Time",    lambda: self._do_cmd("time")),
            ("⌨️  Type Text",      lambda: self._quick("type")),
            ("🔊  Volume Up",      lambda: self._do_cmd("volume up")),
            ("🔉  Volume Down",    lambda: self._do_cmd("volume down")),
        ]
        for txt, fn in quick:
            b = QPushButton(txt); b.setFont(F(9)); b.setFixedHeight(28)
            b.clicked.connect(fn); ql.addWidget(b)
        col.addWidget(qf)

        # Config
        cf2 = HudFrame("CONFIG", C["glow"])
        cl2 = QVBoxLayout(cf2); cl2.setSpacing(6)

        self._tts_chk = QCheckBox("  Voice Output")
        self._tts_chk.setChecked(True); self._tts_chk.setFont(F(9))
        self._tts_chk.setStyleSheet(f"color:{C['text']}; background:transparent;")

        rate_row = QHBoxLayout()
        rate_row.addWidget(L("RATE:", 8, C["dimT"]))
        self._rate = QSlider(Qt.Horizontal)
        self._rate.setRange(100,260); self._rate.setValue(175)
        self._rate.valueChanged.connect(lambda v: self._tts.setProperty("rate",v))
        self._rate.setStyleSheet(f"""
            QSlider::groove:horizontal {{background:{C['dim']};height:3px;border-radius:1px;}}
            QSlider::handle:horizontal {{background:{C['amber']};width:10px;height:10px;
                margin:-3px 0;border-radius:5px;}}
        """)
        rate_row.addWidget(self._rate)

        cl2.addWidget(self._tts_chk)
        cl2.addLayout(rate_row)
        col.addWidget(cf2)

        col.addStretch()
        w = QWidget(); w.setLayout(col); return w

    # ── INPUT BAR ────────────────────────────────
    def _mk_inputbar(self):
        bar = QWidget(); bar.setFixedHeight(54)
        bar.setStyleSheet(f"background:{C['panel']}; border-top:1px solid {C['dim']};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(12,8,12,8); lay.setSpacing(8)

        prefix = L("VELORA://", 9, C["amber"])

        self._input = QLineEdit()
        self._input.setPlaceholderText("Speak your command or query — natural language supported…")
        self._input.setFont(F(11))
        self._input.returnPressed.connect(self.send)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background:{C['void']}; color:{C['glow2']};
                border:1px solid {C['border']}; border-radius:3px; padding:6px 14px;
            }}
            QLineEdit:focus {{ border:1px solid {C['glow']}; }}
        """)

        def btn(text, w=90, col=C["glow"]):
            b = QPushButton(text); b.setFont(F(10,True)); b.setFixedSize(w,36)
            b.setStyleSheet(f"""
                QPushButton {{
                    background:{col}; color:{C['void']};
                    border-radius:3px; font-weight:bold;
                }}
                QPushButton:hover {{ background:{C['glow2']}; color:{C['void']}; }}
                QPushButton:pressed {{ background:{C['dim']}; color:{C['text']}; }}
                QPushButton:disabled {{ background:{C['dimT']}; color:{C['dim']}; }}
            """)
            return b

        self._send_btn  = btn("SEND", 80, C["glow"])
        self._mic_btn   = btn("🎤 MIC", 90, C["amber"])
        self._clear_btn = btn("CLR", 50, C["dim"])
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{background:{C['dim']};color:{C['dimT']};border-radius:3px;}}
            QPushButton:hover {{background:{C['red']};color:white;}}
        """)

        self._send_btn.clicked.connect(self.send)
        self._mic_btn.clicked.connect(self.listen)
        self._clear_btn.clicked.connect(self._chat.clear)

        lay.addWidget(prefix)
        lay.addWidget(self._input, 1)
        lay.addWidget(self._send_btn)
        lay.addWidget(self._mic_btn)
        lay.addWidget(self._clear_btn)
        return bar

    # ─────────────────────────────────────────────
    #  STYLE
    # ─────────────────────────────────────────────
    def _apply_style(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background:{C['void']}; color:{C['text']}; }}
            HudFrame {{ background:transparent; }}
            QPushButton {{
                background:{C['dim']}; color:{C['text']};
                border:1px solid {C['border']}; border-radius:3px; padding:3px 8px;
            }}
            QPushButton:hover  {{ background:{C['border']}; color:{C['glow']}; }}
            QPushButton:pressed {{ background:{C['dim']}; }}
            QCheckBox::indicator {{
                width:12px; height:12px;
                border:1px solid {C['border']}; background:{C['void']}; border-radius:2px;
            }}
            QCheckBox::indicator:checked {{ background:{C['glow']}; }}
            QScrollBar:vertical {{
                background:{C['panel']}; width:5px; border:none;
            }}
            QScrollBar::handle:vertical {{
                background:{C['dimT']}; border-radius:2px;
            }}
        """)

    # ─────────────────────────────────────────────
    #  STATE
    # ─────────────────────────────────────────────
    def _set_active(self, v):
        self._active = v
        self._reactor.set_active(v)
        self._wave.set_ch2(v)
        self._think_bar.setVisible(v)
        self._send_btn.setEnabled(not v)

    def _say(self, text):
        if self._tts_chk.isChecked():
            threading.Thread(
                target=lambda:(self._tts.say(text[:300]),self._tts.runAndWait()),
                daemon=True
            ).start()

    def _mem_push(self, label, content):
        ts = datetime.datetime.now().strftime("%H:%M")
        item = QListWidgetItem(f"[{ts}] {label}: {content[:30]}")
        item.setForeground(QColor(C["dimT"]))
        self._mem_list.addItem(item)
        self._mem_list.scrollToBottom()
        self._lbl_hist.setText(f"MEM: {len(self._history)//2} turns")

    # ─────────────────────────────────────────────
    #  QUICK DIALOGS
    # ─────────────────────────────────────────────
    def _quick(self, kind):
        if kind == "youtube":
            q,ok = QInputDialog.getText(self,"YouTube","Search:")
            if ok and q:
                webbrowser.open("https://www.youtube.com/results?search_query="+q.replace(" ","+"))
                self._chat.cmd(f"YouTube: {q}")
        elif kind == "search":
            q,ok = QInputDialog.getText(self,"Web Search","Search:")
            if ok and q:
                webbrowser.open("https://www.google.com/search?q="+q.replace(" ","+"))
                self._chat.cmd(f"Search: {q}")
        elif kind == "type":
            q,ok = QInputDialog.getText(self,"Type Text","Text to type:")
            if ok and q:
                pyautogui.write(q, interval=0.04)
                self._chat.cmd(f"Typed: {q}")

    def _do_cmd(self, cmd):
        result = self._router.route(cmd)
        if result:
            self._chat.cmd(result)
            self._say(result)

    def _launch_by_name(self, name):
        path = APP_FINDER.find(name)
        if path:
            try:
                APP_FINDER.launch(path)
                self._chat.cmd(f"Launched: {name}")
            except Exception as e:
                self._chat.system(f"Launch error: {e}", C["red"])
        else:
            self._chat.system(f"App not found: {name}", C["red"])

    # ─────────────────────────────────────────────
    #  SEND
    # ─────────────────────────────────────────────
    def send(self):
        msg = self._input.text().strip()
        if not msg or self._active: return
        self._input.clear()
        self._chat.user(msg)
        self._wave.set_ch1(True)
        QTimer.singleShot(600, lambda: self._wave.set_ch1(False))

        # Try local command first
        result = self._router.route(msg)
        if result:
            self._chat.cmd(result)
            self._say(result)
            self._mem_push("CMD", msg)
            return

        # AI
        self._history.append({"role":"user","content":msg})
        if len(self._history) > 20:
            self._history = self._history[-20:]
        self._mem_push("USR", msg)
        self._set_active(True)
        self._chat.system("ROUTING TO NEURAL ENGINE…", C["dimT"])

        self._ai_thread = AIThread(list(self._history))
        self._ai_thread.done.connect(self._on_ai_done)
        self._ai_thread.error.connect(self._on_ai_error)
        self._ai_thread.start()

    def _on_ai_done(self, answer):
        self._history.append({"role":"assistant","content":answer})
        self._mem_push("AI", answer)
        self._chat.velora(answer)
        self._say(answer)
        self._set_active(False)

    def _on_ai_error(self, err):
        if err == "OLLAMA_OFFLINE":
            self._chat.system(
                "OLLAMA OFFLINE — run: ollama serve   then: ollama pull qwen2.5:7b",
                C["red"]
            )
        else:
            self._chat.system(f"AI ERROR: {err}", C["red"])
        self._set_active(False)

    # ─────────────────────────────────────────────
    #  VOICE INPUT
    # ─────────────────────────────────────────────
    def listen(self):
        self._chat.system("🎤 MICROPHONE ACTIVE — LISTENING 5s…", C["glow2"])
        self._reactor.set_listen(True)
        self._wave.set_ch1(True)
        self._mic_btn.setEnabled(False)

        def _rec():
            try:
                fs = 44100
                rec = sd.rec(fs*5, samplerate=fs, channels=1, dtype="int16")
                sd.wait()
                tmp = tempfile.mktemp(".wav")
                wav.write(tmp, fs, rec)
                r = sr.Recognizer()
                with sr.AudioFile(tmp) as src:
                    audio = r.record(src)
                text = r.recognize_google(audio)
                QMetaObject.invokeMethod(self, "_voice_ok",
                    Qt.QueuedConnection, Q_ARG(str, text))
            except Exception as e:
                QMetaObject.invokeMethod(self, "_voice_err",
                    Qt.QueuedConnection, Q_ARG(str, str(e)))

        threading.Thread(target=_rec, daemon=True).start()

    @Slot(str)
    def _voice_ok(self, text):
        self._reactor.set_listen(False); self._wave.set_ch1(False)
        self._mic_btn.setEnabled(True)
        self._input.setText(text); self.send()

    @Slot(str)
    def _voice_err(self, err):
        self._reactor.set_listen(False); self._wave.set_ch1(False)
        self._mic_btn.setEnabled(True)
        self._chat.system(f"MIC ERROR: {err}", C["red"])


# ═══════════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Windows DPI
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window,         QColor(C["void"]))
    pal.setColor(QPalette.WindowText,     QColor(C["text"]))
    pal.setColor(QPalette.Base,           QColor(C["panel"]))
    pal.setColor(QPalette.Text,           QColor(C["text"]))
    pal.setColor(QPalette.Button,         QColor(C["panel"]))
    pal.setColor(QPalette.ButtonText,     QColor(C["text"]))
    pal.setColor(QPalette.Highlight,      QColor(C["glow"]))
    pal.setColor(QPalette.HighlightedText,QColor(C["void"]))
    app.setPalette(pal)

    w = Velora()
    w.show()
    sys.exit(app.exec())
