[README.md](https://github.com/user-attachments/files/29459022/README.md)
# VELORA AI
### Advanced Personal AI Agent · Voice · Vision · Autonomous Control

```
██╗   ██╗███████╗██╗      ██████╗ ██████╗  █████╗
██║   ██║██╔════╝██║     ██╔═══██╗██╔══██╗██╔══██╗
██║   ██║█████╗  ██║     ██║   ██║██████╔╝███████║
╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║
 ╚████╔╝ ███████╗███████╗╚██████╔╝██║  ██║██║  ██║
  ╚═══╝  ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
```

> A fully local, voice-controlled AI agent with a tactical HUD interface.  
> No cloud. No subscriptions. Runs entirely on your machine.

---

## What is Velora?

Velora is a Python-based AI agent you control by voice or text. It can open any installed app on your PC, answer questions, search the web, control system settings, and hold a full conversation — all powered by a locally running AI model through Ollama.

There are two versions included:

| File | Description |
|---|---|
| `app.py` | Voice-only terminal agent (lightweight) |
| `velora_app.py` | Full GUI — tactical HUD interface with animated reactor, oscilloscope, live gauges, app launcher |

---

## Features

### AI & Conversation
- Powered by **Ollama** running locally — no API keys, no internet required for AI
- Full **multi-turn memory** — Velora remembers the last 20 exchanges in a conversation
- Configurable model — defaults to `qwen2.5:7b` (GUI) or `llama3.2` (terminal)
- Smart system prompt locks Velora's identity — no model bleed
- Temperature and context window tuned for sharp, natural responses

### Voice
- **Speak to Velora** using your microphone — 5-second recording window
- Speech-to-text via Google Speech Recognition
- **Text-to-speech** replies via `pyttsx3` (fully offline)
- Adjustable voice speed via slider (GUI) or hardcoded rate (terminal)

### App Control
- Opens **any installed application** on your Windows PC by name
- Registry scan (32-bit + 64-bit hives) indexes all installed programs at startup
- Start Menu shortcut (`.lnk`) scan for additional coverage
- 30+ hardcoded aliases for common apps:
  - WhatsApp, Discord, Spotify, Steam, Epic Games Launcher
  - Chrome, Firefox, VS Code, OBS, VLC, Zoom, Telegram, Teams, Slack
  - Word, Excel, PowerPoint, Outlook
  - Notepad, Calculator, Paint, Task Manager, Explorer, PowerShell
- **Fuzzy matching** — say "epic", "whats", "vs" and it finds the right app
- Fallback to `shell=True` if the app isn't in the index
- GUI includes a **searchable App Launcher panel** — double-click to launch

### Built-in Commands (no AI needed)
| Say... | Action |
|---|---|
| `open <app name>` | Launches the app |
| `launch / start / fire up <app>` | Same as open |
| `close / kill <app>` | Terminates the process |
| `youtube <query>` | Opens YouTube search |
| `search / google <query>` | Opens Google search |
| `type <text>` | Types text at cursor |
| `screenshot` | Saves screenshot to Desktop |
| `time` / `date` | Returns current time/date |
| `system info` | CPU, RAM, disk, battery, uptime |
| `volume up / down / mute` | Adjusts system volume |
| `shutdown` / `restart` | Schedules system shutdown/restart |
| `exit` / `quit` / `goodbye` | Closes Velora |

### GUI (velora_app.py)
- Deep void-black tactical interface — navy, electric cyan, molten amber
- **Animated HUD reactor** with dual counter-rotating sweep arms and 24 spark particles
- **Dual-channel oscilloscope** — mic channel activates on voice input, AI channel pulses during responses
- **Three live system gauges** — real CPU / RAM / Disk readings
- Chamfered-corner tactical panels throughout
- Timestamped colour-coded chat log
- Searchable app launcher panel with 80+ entries
- Animated memory buffer showing conversation history
- Boot sequence with staggered startup messages
- Indeterminate progress bar while AI is thinking
- Reactor glows cyan when listening · amber when processing · blue on standby

---

## Requirements

### System
- Windows 10 or 11
- Python 3.10+
- Microphone
- [Ollama](https://ollama.com) installed and running

### Python Packages

Install everything at once:

```bash
pip install pyttsx3 SpeechRecognition sounddevice scipy pyautogui requests psutil ollama PySide6
```

Optional (for volume control via `pycaw`):
```bash
pip install pycaw comtypes
```

If `pycaw` is not installed, Velora falls back to `pyautogui` volume keys automatically.

### Ollama Models

Pull the model(s) before running:

```bash
# For the GUI (velora_app.py)
ollama pull qwen2.5:7b

# For the terminal agent (app.py)
ollama pull llama3.2
```

---

## Installation

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/velora-ai.git
cd velora-ai

# 2. Install dependencies
pip install pyttsx3 SpeechRecognition sounddevice scipy pyautogui requests psutil ollama PySide6

# 3. Start Ollama (keep this running in background)
ollama serve

# 4. Pull the AI model
ollama pull qwen2.5:7b

# 5. Run Velora
python velora_app.py      # Full GUI
# or
python app.py             # Terminal voice agent
```

---

## Usage

### Voice Commands
Click **🎤 MIC** (GUI) or wait for the "Listening..." prompt (terminal), then speak naturally:

```
"Open WhatsApp"
"Launch Epic Games"
"What is the speed of light?"
"Search YouTube for lo-fi beats"
"Take a screenshot"
"What time is it?"
"How much RAM am I using?"
"Open VS Code"
"Type Hello World"
"Tell me a joke"
```

### Text Commands (GUI only)
Type anything in the input bar and press **Enter** or click **SEND**.

### App Launcher Panel (GUI only)
The right-side panel lists all indexed apps. Type in the search box to filter, then **double-click** any entry to launch it immediately.

---

## Configuration

### Change the AI Model
In `velora_app.py`, find the `AIThread` class and change:
```python
"model": "qwen2.5:7b"
```
to any model you have pulled, e.g. `"llama3.2"`, `"mistral"`, `"gemma2"`.

In `app.py`, change:
```python
model="llama3.2"
```

### Add Custom Apps
In `app.py`, add entries to the `APPS` dictionary:
```python
APPS = {
    "my app": r"C:\Path\To\MyApp.exe",
    ...
}
```

In `velora_app.py`, add entries to `AppFinder.KNOWN_ALIASES`:
```python
KNOWN_ALIASES = {
    "my app": r"C:\Path\To\MyApp.exe",
    ...
}
```

### Voice Speed
- **GUI**: Use the RATE slider in the CONFIG panel on the right
- **Terminal**: Change `engine.setProperty("rate", 170)` — lower is slower, higher is faster

---

## Project Structure

```
velora-ai/
│
├── velora_app.py      # Full GUI — APEX HUD interface
├── app.py             # Terminal voice agent (lightweight)
└── README.md          # This file
```

---

## Troubleshooting

**Ollama not connecting**
Make sure Ollama is running: `ollama serve`
Check it's accessible: `curl http://localhost:11434`

**Microphone not working**
Make sure your mic is set as the default recording device in Windows Sound Settings.
Try running: `python -c "import sounddevice; print(sounddevice.query_devices())"`

**App won't open**
Say the app name clearly — e.g. "open epic games launcher" not just "epic".
If it still fails, add the exact `.exe` path to `KNOWN_ALIASES` in `velora_app.py`.

**pyttsx3 voice error**
This can happen if the TTS engine locks. Restart Velora. If it persists, try:
```bash
pip install --upgrade pyttsx3
```

**PySide6 not found**
```bash
pip install PySide6
```

---

## Roadmap

- [ ] Streaming AI responses (token-by-token output)
- [ ] Wake word detection ("Hey Velora")
- [ ] File search and management commands
- [ ] Weather integration
- [ ] Reminder and alarm system
- [ ] Multi-monitor screenshot targeting
- [ ] Plugin system for custom commands
- [ ] Linux and macOS support

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with Python · Ollama · PySide6 · pyttsx3 · SpeechRecognition*
