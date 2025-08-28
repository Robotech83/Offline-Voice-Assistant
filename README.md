# Offline-Voice-Assistant (Raspberry Pi 4)

## Requirements
- Raspberry Pi 4 running Debian Bookworm
- Microphone
- Python 3.9+
- [Vosk model](https://alphacephei.com/vosk/models)

## Setup
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv portaudio19-dev python3-pyaudio espeak ffmpeg libatlas-base-dev
python3 -m venv ~/sonny-env
source ~/voice-env/bin/activate
pip install pyttsx3 vosk pyaudio
mkdir -p ~/voice
cd ~/voice
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip


Run
source ~/voice-env/bin/activate
python3 voice.py



---

If you want, I can **also make it fully plug-and-play** so **anyone can clone your GitHub repo and just run `python3 voice.py`** without manually downloading the Vosk model.
That would be perfect for sharing.  

Do you want me to do that next?
