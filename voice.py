
#!/usr/bin/env python3
import logging
import threading
import time
import difflib
import json
from datetime import datetime

import pyttsx3
from vosk import Model, KaldiRecognizer
import pyaudio
import os
import sys

# -----------------------------------------
# Logging Setup
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -----------------------------------------
# Text-to-Speech Engine (Pi Compatible)
# -----------------------------------------
try:
    engine = pyttsx3.init(driverName='espeak')  # Explicitly use espeak on Pi
except Exception as e:
    logging.error(f"Failed to initialize pyttsx3: {e}")
    sys.exit(1)

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)
voices = engine.getProperty('voices')
current_voice_index = 0

def text_to_speech(text):
    logging.info(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def change_voice():
    """Cycle through available voices."""
    global current_voice_index
    current_voice_index = (current_voice_index + 1) % len(voices)
    engine.setProperty('voice', voices[current_voice_index].id)
    text_to_speech("Voice changed.")
    logging.info("Voice changed.")

# -----------------------------------------
# Utility Functions
# -----------------------------------------
def get_current_time():
    return datetime.now().strftime("%I:%M %p")

def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

# -----------------------------------------
# Command Functions
# -----------------------------------------
def command_time():
    text_to_speech(f"The current time is {get_current_time()}.")

def command_date():
    text_to_speech(f"Today's date is {get_current_date()}.")

def command_talk_back():
    text_to_speech("Hello! I am awake and ready for commands.")

def command_how_are_you():
    text_to_speech("I am just a robot, but I am feeling functional!")

def command_set_timer():
    text_to_speech("Timers are not active in this test version.")

def command_change_voice():
    change_voice()

def command_exit():
    text_to_speech("Goodbye!")
    sys.exit(0)

command_dict = {
    "what time is it": command_time,
    "what is today's date": command_date,
    "hello": command_talk_back,
    "how are you": command_how_are_you,
    "set timer": command_set_timer,
    "change voice": command_change_voice,
    "exit": command_exit,
}

def match_command(command_text):
    keys = list(command_dict.keys())
    matches = difflib.get_close_matches(command_text, keys, n=1, cutoff=0.6)
    if matches:
        logging.info(f"Matched command '{command_text}' to '{matches[0]}'")
        return command_dict[matches[0]]
    logging.info(f"No matching command found for '{command_text}'")
    return None

# -----------------------------------------
# Vosk Speech Recognition Setup
# -----------------------------------------
vosk_model_path = os.path.expanduser("~/sonny/vosk-model-small-en-us-0.15")
if not os.path.exists(vosk_model_path):
    logging.error(f"Vosk model not found at {vosk_model_path}. Please download and unzip it.")
    sys.exit(1)

vosk_model = Model(vosk_model_path)

pa = pyaudio.PyAudio()

# Auto-detect the first available microphone
input_device_index = None
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info.get("maxInputChannels") > 0:
        input_device_index = i
        logging.info(f"Using microphone: {info.get('name')} (device {i})")
        break

if input_device_index is None:
    logging.error("No microphone found. Exiting.")
    sys.exit(1)

stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 input_device_index=input_device_index,
                 frames_per_buffer=4096)
stream.start_stream()

def listen_for_phrase_vosk(prompt="Listening...", timeout=5):
    text_to_speech(prompt)
    start_time = time.time()
    rec = KaldiRecognizer(vosk_model, 16000)
    result_text = ""
    while True:
        if time.time() - start_time > timeout:
            break
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result_dict = json.loads(rec.Result())
            result_text = result_dict.get("text", "")
            break
    return result_text

def listen_for_wake_word_vosk(timeout=5):
    result_text = listen_for_phrase_vosk("Listening for wake word", timeout)
    logging.info(f"Heard for wake word: {result_text}")
    return "hey sonny" in result_text.lower()

def listen_for_command_vosk(timeout=5):
    result_text = listen_for_phrase_vosk("Listening for command", timeout)
    logging.info(f"Heard command: {result_text}")
    return result_text

# -----------------------------------------
# Command Processing Loop
# -----------------------------------------
def process_commands():
    while True:
        if listen_for_wake_word_vosk(timeout=5):
            text_to_speech("How can I help you? Say 'cancel' to exit command mode.")
            while True:
                command_text = listen_for_command_vosk(timeout=5)
                if not command_text:
                    continue
                if "cancel" in command_text.lower():
                    text_to_speech("Exiting command mode.")
                    break
                command_func = match_command(command_text)
                if command_func:
                    command_func()
                else:
                    text_to_speech("I did not understand that command.")

# -----------------------------------------
# Main Entry Point
# -----------------------------------------
def main():
    command_thread = threading.Thread(target=process_commands, daemon=True)
    command_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        text_to_speech("Shutting down. Goodbye!")
        logging.info("Assistant shutdown via KeyboardInterrupt.")

if __name__ == "__main__":
    main()
