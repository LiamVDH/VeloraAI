# -*- mode: python ; coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────
#  VELORA AI — PyInstaller Spec File
#  Build command:  pyinstaller velora.spec
# ─────────────────────────────────────────────────────────────

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ── Hidden imports ────────────────────────────────────────────
# All packages that PyInstaller misses because they are loaded
# at runtime, via plugins, or through ctypes / winreg.
hidden = [
    # Speech recognition internals
    "speech_recognition",
    "speech_recognition.audio",

    # sounddevice / PortAudio
    "sounddevice",
    "_sounddevice_data",

    # scipy WAV writing
    "scipy.io.wavfile",
    "scipy.io",
    "scipy._lib",
    "scipy._lib.messagestream",

    # pyttsx3 driver chain — all three so it works on any Windows machine
    "pyttsx3",
    "pyttsx3.drivers",
    "pyttsx3.drivers.sapi5",
    "pyttsx3.drivers.nsss",
    "pyttsx3.drivers.espeak",

    # Ollama client
    "ollama",
    "httpx",
    "httpcore",
    "anyio",
    "anyio._backends._asyncio",
    "anyio._backends._trio",

    # pyautogui + its deps
    "pyautogui",
    "pyscreeze",
    "mouseinfo",
    "pytweening",

    # psutil (system metrics)
    "psutil",
    "psutil._pswindows",
    "psutil._psutil_windows",

    # Windows registry (stdlib but sometimes missed)
    "winreg",
    "ctypes",
    "ctypes.wintypes",

    # Requests (used by velora_app.py for Ollama REST calls)
    "requests",
    "urllib3",
    "charset_normalizer",
    "certifi",

    # PySide6 — only needed if building the GUI version (velora_app.py)
    # Comment these out if building app.py only to keep the exe smaller.
    "PySide6",
    "PySide6.QtWidgets",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "shiboken6",
]

# ── Collect submodules that use __import__ / importlib internally ─
hidden += collect_submodules("speech_recognition")
hidden += collect_submodules("pyttsx3")
hidden += collect_submodules("ollama")
hidden += collect_submodules("psutil")

# ── Data files (non-Python assets that must travel with the exe) ─
datas = []
datas += collect_data_files("speech_recognition")   # grammar / language data
datas += collect_data_files("sounddevice")           # PortAudio DLL
datas += collect_data_files("pyttsx3")

# ─────────────────────────────────────────────────────────────
#  CHANGE THIS LINE to switch between the two entry points:
#    'app.py'         → terminal voice agent  (no GUI, smaller exe)
#    'velora_app.py'  → full HUD GUI
# ─────────────────────────────────────────────────────────────
ENTRY = 'velora_app.py'

a = Analysis(
    [ENTRY],
    pathex=['.'],                   # look in the project root
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim fat — things Velora definitely does not need
        'tkinter',
        'matplotlib',
        'numpy.distutils',
        'setuptools',
        'pkg_resources',
        'IPython',
        'jupyter',
        'test',
        'unittest',
    ],
    noarchive=False,
    optimize=1,                     # bytecode optimisation (was 0)
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VeloraAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        # These DLLs corrupt when UPX-packed — always exclude them
        'vcruntime140.dll',
        'ucrtbase.dll',
        'python3*.dll',
        'Qt6*.dll',
        'PySide6/*.pyd',
    ],
    runtime_tmpdir=None,
    # ── console=True  → shows a terminal window (good for debugging)
    # ── console=False → silent background process (final release)
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Optional: give the exe a custom icon
    # icon='icon.ico',
)
