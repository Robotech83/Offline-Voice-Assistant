🤖 Sonny — Offline Voice + Vision Humanoid Robot (InMoov)

Sonny is a fully offline-capable humanoid robot assistant built on an InMoov platform, powered by a Raspberry Pi 4 and controlled through an Arduino Mega.

This project integrates speech recognition, computer vision, servo control, and multilingual speech synthesis into a single real-time robotic system.

🧠 System Architecture

Main Controller

Raspberry Pi 4 (Debian Bookworm recommended)

Motion Controller

Arduino Mega 2560 (serial communication)

Vision

OpenCV (Haar cascade face detection)

Real-time head pan/tilt tracking

Speech Recognition

Vosk (offline speech-to-text)

Speech Synthesis

eSpeak-NG (English phoneme-driven lip sync)

gTTS (Igbo support with amplitude-based lip sync)

🎯 Capabilities

Sonny can:

👀 Track human faces and follow them with head movement

🗣️ Respond to voice commands after wake word activation

💬 Speak in English or Igbo

😄 Tell jokes and randomized responses

🧠 Answer identity and creator questions

🎮 Control servos for:

Mouth (lip-sync)

Head pan

Head tilt

📦 Core Features

✅ Fully offline speech recognition (Vosk)

✅ Real-time face tracking

✅ Serial-based servo control via Arduino Mega (/dev/ttyACM0)

✅ Multilingual speech system

✅ Extensible command_dict for adding new commands

✅ Randomized personality responses

⚙️ Requirements
	🔌 Hardware
			Raspberry Pi 4
			Arduino Mega 2560
			USB Webcam or Pi Camera
			Servos (mouth, pan, tilt)

💻 System Packages (Raspberry Pi)
	sudo apt update
	sudo apt install -y python3-opencv espeak-ng portaudio19-dev ffmpeg

🐍 Python Dependencies
	pip install -r requirements.txt

If installing manually:

	pip install vosk pyaudio pyserial opencv-python gTTS pydub simpleaudio

📥 Install Vosk Model

	mkdir -p ~/Documents/Sonny
	cd ~/Documents/Sonny
	wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
	unzip vosk-model-small-en-us-0.15.zip

🚀 Running Sonny
	Connect Arduino Mega via USB (/dev/ttyACM0 default)
	Connect camera
	Ensure Vosk model is installed

Run:
	python3 Control_Sonny.py

Say:
	Hello or Sonny
to activate.

🎙️ Available Voice Commands
		Wake Word - Hello or Sonny

🕒 General
	"What time is it?"
	"What is today’s date?"
	"Tell me a joke"
	"Make me laugh"
	"What is your name?"
	"Who made you?"

🤖 Status / Motion
	"How are you?"
	"Center head"

🌍 Language Switching
	"Switch to Igbo"
	"Speak Igbo"
	"Switch to English"
	"Speak English"

🔚 Exit
	"Goodbye"

🛠️ Configuration Notes

If encodings.pickle not found appears, disable face recognition or generate encodings.
Tune servo angles in:
	move_head()
	mouth_open()
	mouth_close()

Adjust amplitude thresholds in speak_igbo() for smoother lip-sync.

Logging level defaults to logging.INFO.

🎥 Demo (Add This Next)


Screenshot of terminal running
