# 🤖 Sonny — Offline Voice-Controlled Humanoid Robot (InMoov)

Sonny is an InMoov humanoid robot assistant powered by a Raspberry Pi 4 and controlled through an Arduino Mega.

This project integrates offline speech recognition, multilingual speech synthesis, and real-time servo control into a single embedded robotics system.

---

## 🧠 System Overview

**Main Controller**
- Raspberry Pi 4 (Debian Bookworm recommended)

**Motion Controller**
- Arduino Mega 2560 (serial communication)

**Speech Recognition**
- Vosk (fully offline speech-to-text)

**Speech Synthesis**
- eSpeak-NG (English with phoneme-based lip sync)
- gTTS (Igbo with amplitude-based lip sync)

---

## 🎯 Current Capabilities

Sonny can:

- 🗣️ Respond to voice commands after wake word activation
- 💬 Speak in English or Igbo
- 😄 Tell jokes and randomized responses
- 🧠 Answer identity and creator questions
- 🎮 Control servos for:
  - Mouth (lip sync)
  - Head pan
  - Head tilt

---

## 📦 Core Features

- ✅ Fully offline speech recognition (Vosk)
- ✅ Multilingual speech system
- ✅ Serial-based servo control via Arduino Mega (`/dev/ttyACM0`)
- ✅ Randomized personality responses
- ✅ Extensible `command_dict` for adding new commands

---

## 📂 Project Structure
.
├── Control_Sonny.py # Main integrated script (voice + motion)
├── vosk-model-small-en-us-0.15/ # Offline Vosk model
├── requirements.txt # Python dependencies
└── README.md # Documentation


---

## ⚙️ Requirements

### 🔌 Hardware

- Raspberry Pi 4
- Arduino Mega 2560
- USB microphone
- Speaker
- Servos (mouth, pan, tilt)

---

### 💻 System Packages (Raspberry Pi)

	sudo apt update
	sudo apt install -y python3-opencv espeak-ng portaudio19-dev ffmpeg

---

### 🐍 Python Dependencies
	pip install -r requirements.txt
If installing manually:
	pip install vosk pyaudio pyserial opencv-python gTTS pydub simpleaudio


---

## 📥 Install Vosk Model
- mkdir -p ~/Documents/Sonny
- cd ~/Documents/Sonny
- wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
- unzip vosk-model-small-en-us-0.15.zip
  
---

## 🚀 Running Sonny

1. Connect Arduino Mega via USB (`/dev/ttyACM0` default)
2. Ensure microphone and speaker are connected
3. Make sure Vosk model is installed
4. Run: python3 Control_Sonny.py
5. Say: Hello or Sonny


to activate.

---

## 🎙️ Available Voice Commands

### Wake Word
- Hello
- Sonny

### General
- What time is it?
- What is today’s date?
- Tell me a joke
- Make me laugh
- What is your name?
- Who made you?

### Status / Motion
- How are you?
- Center head

### Language Switching
- Switch to Igbo
- Speak Igbo
- Switch to English
- Speak English

### Exit
- Goodbye

---

## 🛠️ Configuration Notes

- Servo angles in `move_head()`, `mouth_open()`, and `mouth_close()` must be tuned for your robot.
- Adjust amplitude thresholds in `speak_igbo()` for smoother lip sync.
- Logging level defaults to `logging.INFO`.

---

## 🎥 Demo (Recommended Next Step)

Add:
- Screenshot of Sonny
- Screenshot of terminal running
- Short 20–40 second demo video

This greatly improves project presentation.

---




