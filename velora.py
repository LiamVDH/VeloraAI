import ollama
import pyttsx3
import sounddevice as sd
import speech_recognition as sr
import os
import datetime


# =========================
# VOICE
# =========================

engine = pyttsx3.init()
engine.setProperty("rate",170)


def speak(text):

    print("VELORA:",text)

    try:
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print("VOICE ERROR:",e)



# =========================
# LISTEN
# =========================

def listen():

    recognizer = sr.Recognizer()

    print("\nListening...")

    try:

        audio = sd.rec(
            int(5*44100),
            samplerate=44100,
            channels=1,
            dtype="int16"
        )

        sd.wait()


        audio_data = sr.AudioData(
            audio.tobytes(),
            44100,
            2
        )


        text = recognizer.recognize_google(
            audio_data
        )


        print("YOU:",text)

        return text.lower()


    except Exception:

        return ""



# =========================
# AI
# =========================

def ask_ai(message):

    try:

        response = ollama.chat(

            model="llama3.2",

            messages=[

                {
                    "role":"system",
                    "content":
                    "You are Velora, a futuristic personal AI assistant. Be helpful, smart and concise."
                },

                {
                    "role":"user",
                    "content":message
                }

            ]

        )


        # FIXED RESPONSE HANDLING

        return response["message"]["content"]


    except Exception as e:

        return "AI ERROR: " + str(e)



# =========================
# COMMANDS
# =========================

def commands(text):


    if "open chrome" in text:

        os.startfile(
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )

        return "Opening Chrome."


    if "open youtube" in text:

        os.system(
            "start https://youtube.com"
        )

        return "Opening YouTube."


    if "time" in text:

        return (
            "The time is "
            +
            datetime.datetime.now().strftime("%H:%M")
        )


    if "shutdown" in text:

        os.system(
            "shutdown /s /t 10"
        )

        return "Shutting down."


    return None




# =========================
# START
# =========================

speak(
    "Velora AI is online. How can I help?"
)


while True:


    user = listen()


    if user == "":
        continue



    if "exit" in user or "quit" in user:

        speak("Goodbye.")

        break



    command = commands(user)


    if command:

        speak(command)


    else:

        answer = ask_ai(user)

        speak(answer)