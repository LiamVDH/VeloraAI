import ollama
import pyttsx3
import sounddevice as sd
import speech_recognition as sr
import os, datetime, subprocess, webbrowser

engine = pyttsx3.init()
engine.setProperty("rate", 170)
history = []   # conversation memory

def speak(text):
    print("VELORA:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("VOICE ERROR:", e)

def listen():
    recognizer = sr.Recognizer()
    print("\nListening...")
    try:
        audio = sd.rec(int(5 * 44100), samplerate=44100, channels=1, dtype="int16")
        sd.wait()
        audio_data = sr.AudioData(audio.tobytes(), 44100, 2)
        text = recognizer.recognize_google(audio_data)
        print("YOU:", text)
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print("MIC ERROR:", e)
        return ""

def ask_ai(message):
    history.append({"role": "user", "content": message})
    if len(history) > 20:
        history.pop(0)
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content":
                 "You are Velora, a futuristic personal AI. Be smart, concise, and direct."}
            ] + history
        )
        answer = response.message.content   # correct dot notation
        history.append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        return "AI ERROR: " + str(e)

APPS = {
    "chrome":      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad":     "notepad.exe",
    "calculator":  "calc.exe",
    "paint":       "mspaint.exe",
    "explorer":    "explorer.exe",
    "discord":     os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe"),
    "spotify":     os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
    "steam":       r"C:\Program Files (x86)\Steam\steam.exe",
    "epic games":  r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
    "whatsapp":    os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
    "vscode":      os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    "vs code":     os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
}

def commands(text):
    # Open apps — fuzzy match
    if text.startswith("open ") or "launch " in text or "start " in text:
        target = text.replace("open","").replace("launch","").replace("start","").strip()
        for name, path in APPS.items():
            if name in target:
                try:
                    os.startfile(path)
                    return f"Opening {name}."
                except:
                    try:
                        subprocess.Popen(path, shell=True)
                        return f"Opening {name}."
                    except Exception as e:
                        return f"Could not open {name}: {e}"
        # fallback: try raw
        try:
            subprocess.Popen(target, shell=True)
            return f"Trying to open {target}."
        except:
            return f"I couldn't find {target} on your system."

    if "youtube" in text:
        q = text.replace("youtube","").replace("search","").strip()
        webbrowser.open("https://youtube.com/results?search_query=" + q.replace(" ","+"))
        return "Opening YouTube."

    if "google" in text or "search" in text:
        q = text.replace("google","").replace("search","").strip()
        webbrowser.open("https://google.com/search?q=" + q.replace(" ","+"))
        return f"Searching for {q}."

    if "time" in text:
        return "The time is " + datetime.datetime.now().strftime("%H:%M")

    if "date" in text:
        return "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y")

    if "screenshot" in text:
        import pyautogui
        path = os.path.join(os.path.expanduser("~"), "Desktop",
                            f"velora_{datetime.datetime.now().strftime('%H%M%S')}.png")
        pyautogui.screenshot(path)
        return f"Screenshot saved to Desktop."

    if "shutdown" in text:
        os.system("shutdown /s /t 10")
        return "Shutting down in 10 seconds."

    if "restart" in text:
        os.system("shutdown /r /t 10")
        return "Restarting in 10 seconds."

    return None

speak("Velora online. How can I help?")

while True:
    user = listen()
    if not user:
        continue
    if "exit" in user or "quit" in user or "goodbye" in user:
        speak("Goodbye.")
        break
    result = commands(user)
    if result:
        speak(result)
    else:
        speak(ask_ai(user))
