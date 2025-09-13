
# 🤖 Sonny – InMoov Robot AI Assistant

This project runs **Sonny**, an InMoov humanoid robot powered by:

- 🧠 Raspberry Pi 4 (main controller)
    
- 🎮 Arduino Mega (servo + motion control)
    
- 👀 OpenCV (face detection + head tracking)
    
- 🗣️ Vosk (offline speech recognition)
    
- 💬 Espeak-NG + gTTS (multilingual speech synthesis with lip-sync)
    

Sonny can:

- Track human faces with head movement
    
- Speak in **English** or **Igbo** with lip-sync
    
- Respond to greetings, jokes, time/date queries, and creator questions
    
- Accept voice commands after a wake word ("Hello" or "Sonny")
    
- Control servos for mouth, head pan, and tilt
    

---

## 📦 Features

- ✅ **Offline Speech Recognition** – Vosk

-  ✅ **Multilingual Speech** – English (Espeak-NG phonemes) & Igbo (gTTS with amplitude-based lipsync)

- ✅ **Face Tracking** – OpenCV Haar cascade + servo pan/tilt

- ✅ **Servo Control** – Arduino Mega (serial link at `/dev/ttyACM0`)

- ✅ **Randomized Responses** – Greetings, jokes, and creator acknowledgments

- ✅ **Extensible Commands** – Add more commands easily in `command_dict`


## 📂 Project Structure

bash
.
├── Control_Sonny.py      # Main merged script (this file)
├── encodings.pickle      # (Optional) Face recognition encodings
├── vosk-model-small-en-us-0.15/  # Vosk model directory
├── requirements.txt      # Python dependencies
└── README.md             # This file


## ⚙️ Requirements

### Hardware

- Raspberry Pi 4 (Debian Bookworm recommended)
    
- Arduino Mega 2560
    
- Webcam or Pi Camera
    
- Servos (for mouth, pan, tilt)
    

### Software

Install dependencies:
	bash
sudo apt update
sudo apt install python3-opencv espeak-ng portaudio19-dev ffmpeg

Install Python modules:
	bash
pip install vosk pyaudio pyserial opencv-python gTTS pydub simpleaudio

## 🚀 Running Sonny

1. Plug in your Arduino Mega via USB (`/dev/ttyACM0` default).
    
2. Connect a camera for face tracking.
    
3. Make sure the Vosk model is installed:
		bash
	mkdir -p ~/Documents/Sonny
	cd ~/Documents/Sonny
	wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
	unzip vosk-model-small-en-us-0.15.zip

4.  Run the main script:
		bash
	python3 Control_Sonny.py
 5.  Say **“Hello”** or **“Sonny”** to activate.


## 🎙️ Available Commands

Wake word → `Hello` or `Sonny`

### General

- "What time is it?"
    
- "What is today’s date?"
    
- "Tell me a joke" / "Make me laugh"
    
- "What is your name?"
    
- "Who made you?"
    

### Status

- "How are you?"
    
- "Center head"
    

### Language Switching

- "Switch to Igbo" / "Speak Igbo"
    
- "Switch to English" / "Speak English"
    

### Exit

- "Goodbye" → shuts down
    

---

## 🛠️ Notes

- If you get `encodings.pickle not found`, disable/skip face recognition or generate encodings first.
    
- Servo angles in `move_head()` and `mouth_open()` / `mouth_close()` must be tuned for your robot.
    
- Adjust **audio thresholds** in `speak_igbo()` for smoother lipsync.
    
- Debug logs are enabled (`logging.INFO`) by default.
✅ Offline Speech Recognition – Vosk

