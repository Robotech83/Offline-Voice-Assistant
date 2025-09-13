import logging
import threading
import time
import difflib
import json
import random  # For random jokes
from datetime import datetime

import pyttsx3
# Vosk and PyAudio imports
from vosk import Model, KaldiRecognizer
import pyaudio

# -----------------------------------------
# Logging Setup
# -----------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------------------
# Text-to-Speech Engine
# -----------------------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)
voices = engine.getProperty('voices')
current_voice_index = 0  # Track current voice

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
    now = datetime.now()
    return now.strftime("%I:%M %p")

def get_current_date():
    now = datetime.now()
    return now.strftime("%B %d, %Y")

# -----------------------------------------
# Jokes List
# -----------------------------------------
jokes = [
    "I tried to download some cooking skills… but I only got cookies.",
    "Why don’t robots panic? Because we’ve got nerves of steel.",
    "What’s a robot’s favorite music? Heavy metal!",
    "Why did the robot go on a diet? Too many chips.",
    "Humans say I have a dry sense of humor… that’s because my cooling fans work so well.",
    "I told a human a joke yesterday. He didn’t laugh, so I ran a diagnostic. His humor module was offline."
]

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
    exit(0)

def command_name():
    text_to_speech("My name is Sonny.")

def command_joke():
    joke = random.choice(jokes)
    text_to_speech(joke)

# -----------------------------------------
# Command Dictionary
# -----------------------------------------
command_dict = {
    "what time is it": command_time,
    "what is today's date": command_date,
    "hello": command_talk_back,
    "how are you": command_how_are_you,
    "set timer": command_set_timer,
    "change voice": command_change_voice,
    "goodbye": command_exit,
    "what is your name": command_name,
    "tell me a joke": command_joke,
    "make me laugh": command_joke,
    "say something funny": command_joke,
}

def match_command(command_text):
    """Fuzzy match the spoken text to a command."""
    keys = list(command_dict.keys())
    matches = difflib.get_close_matches(command_text, keys, n=1, cutoff=0.6)
    if matches:
        logging.info(f"Matched command '{command_text}' to '{matches[0]}'")
        return command_dict[matches[0]]
    else:
        logging.info(f"No matching command found for '{command_text}'")
        return None

# -----------------------------------------
# Vosk Speech Recognition Setup
# -----------------------------------------
vosk_model_path = "/home/Robo/Documents/Sonny/vosk-model-small-en-us-0.15"  # Update path
vosk_model = Model(vosk_model_path)

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                 input=True, frames_per_buffer=4096)
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
    return "hello" in result_text.lower()

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
            text_to_speech("How can I help you?")
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

