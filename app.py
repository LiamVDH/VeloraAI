import sys
import os
import requests
import webbrowser
import subprocess
import tempfile
import threading

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import scipy.io.wavfile as wav
import pyautogui


# -------------------------
# VELORA CORE
# -------------------------

class Reactor(QWidget):

    def __init__(self):
        super().__init__()
        self.angle = 0

        timer = QTimer(self)
        timer.timeout.connect(self.update_anim)
        timer.start(30)


    def update_anim(self):
        self.angle += 5
        self.update()


    def paintEvent(self,e):

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        x = self.width()//2
        y = self.height()//2

        for i,c in enumerate(
            ["cyan","blue","magenta","green"]
        ):

            p.setPen(
                QPen(QColor(c),3)
            )

            r = 80+i*40+(self.angle%40)

            p.drawEllipse(
                x-r,
                y-r,
                r*2,
                r*2
            )


        p.setBrush(
            QColor("#00ffff")
        )

        p.drawEllipse(
            x-25,
            y-25,
            50,
            50
        )



class Velora(QMainWindow):


    def __init__(self):

        super().__init__()

        self.resize(1300,800)

        self.setWindowTitle(
            "VELORA AI"
        )


        self.tts = pyttsx3.init()


        self.setStyleSheet("""

        QMainWindow{
        background:#020617;
        }

        QTextEdit,QLineEdit{
        background:#071426;
        color:white;
        border:2px solid cyan;
        border-radius:20px;
        padding:15px;
        }


        QPushButton{
        background:#ff0088;
        color:white;
        border-radius:20px;
        padding:15px;
        }

        """)



        box = QWidget()
        layout = QVBoxLayout()


        title = QLabel(
            "VELORA"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFont(
            QFont("Arial",50,QFont.Bold)
        )


        self.reactor = Reactor()

        self.reactor.setFixedHeight(350)



        self.chat = QTextEdit()

        self.chat.setReadOnly(True)


        self.chat.append(
            "VELORA:\nAI AGENT ONLINE"
        )


        self.input = QLineEdit()


        send = QPushButton(
            "SEND"
        )

        send.clicked.connect(
            self.send
        )


        speak = QPushButton(
            "🎤 SPEAK"
        )

        speak.clicked.connect(
            self.listen
        )


        row = QHBoxLayout()

        row.addWidget(self.input)
        row.addWidget(send)
        row.addWidget(speak)



        layout.addWidget(title)
        layout.addWidget(self.reactor)
        layout.addWidget(self.chat)
        layout.addLayout(row)


        box.setLayout(layout)

        self.setCentralWidget(box)




    def say(self,text):

        threading.Thread(
            target=lambda:
            (
                self.tts.say(text),
                self.tts.runAndWait()
            )
        ).start()



    def clean(self,text):

        for word in [
            "hi",
            "hello",
            "velora",
            "please",
            "can you"
        ]:

            text=text.lower().replace(word,"")

        return text.strip()



    def commands(self,msg):


        clean=self.clean(msg)



        if "youtube" in msg.lower():

            webbrowser.open(
                "https://www.youtube.com/results?search_query="
                +
                clean.replace(" ","+")
            )

            return "Opening YouTube search"



        if msg.lower().startswith("open"):

            app = clean.replace(
                "open",
                ""
            ).strip()


            try:

                subprocess.Popen(
                    app
                )

                return "Opening "+app


            except:

                return "I could not find that app"



        if "type" in msg.lower():

            pyautogui.write(
                clean.replace("type",""),
                interval=0.03
            )

            return "Typing"



        return None





    def send(self):

        msg=self.input.text()


        if not msg:
            return


        self.chat.append(
            "\nYOU:\n"+msg
        )


        self.input.clear()


        cmd=self.commands(msg)


        if cmd:

            self.chat.append(
                "\nVELORA:\n"+cmd
            )

            self.say(cmd)

            return



        self.chat.append(
            "\nVELORA:\nThinking..."
        )



        try:

            r=requests.post(

            "http://localhost:11434/api/generate",

            json={

            "model":"qwen2.5:7b",

            "prompt":
            """
You are Velora AI.
Your name is Velora.
You are a powerful personal assistant.
Never say you are Qwen.

User:
"""+msg,

            "stream":False

            },

            timeout=120
            )


            answer=r.json()["response"]


            self.chat.append(
                "\n"+answer
            )


            self.say(answer)


        except Exception as e:

            self.chat.append(
                "\nOllama error:\n"+str(e)
            )




    def listen(self):

        self.chat.append(
            "\nVELORA:\nListening..."
        )

        try:

            fs=44100

            recording=sd.rec(
                fs*5,
                samplerate=fs,
                channels=1,
                dtype="int16"
            )


            sd.wait()


            file=tempfile.mktemp(".wav")


            wav.write(
                file,
                fs,
                recording
            )


            r=sr.Recognizer()


            with sr.AudioFile(file) as source:

                audio=r.record(source)


            text=r.recognize_google(audio)


            self.input.setText(text)

            self.send()


        except Exception as e:

            self.chat.append(
                "\nMic error:\n"+str(e)
            )




app=QApplication(sys.argv)

window=Velora()

window.show()

sys.exit(app.exec())