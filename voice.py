import logging
import threading
import time
import difflib
import json
import random
from datetime import datetime

import pyttsx3
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
current_voice_index = 0

def text_to_speech(text):
    logging.info(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def change_voice():
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
# Response Sets
# -----------------------------------------
jokes = [
    "I tried to download some cooking skills… but I only got cookies.",
    "Why don’t robots panic? Because we’ve got nerves of steel.",
    "What’s a robot’s favorite music? Heavy metal!",
    "Why did the robot go on a diet? Too many chips.",
    "Humans say I have a dry sense of humor… that’s because my cooling fans work so well.",
    "I told a human a joke yesterday. He didn’t laugh, so I ran a diagnostic. His humor module was offline."
]

creator_responses = [
    "I was created by my builder, Kosi. Without them, I’d just be a box of parts.",
    "My maker is Kosi. They gave me life… well, as close as a robot can get.",
    "Technically, I was designed by Gaël Langevin as InMoov. But the real magic was done by Kosi.",
    "I was made by Kosi. If you don’t like how I behave, take it up with them!",
    "My creator is Kosi. Don’t worry, they programmed me to be nice… I think.",
    "I was brought into existence by Kosi. Some call them my maker… I call them my human.",
    "I was assembled and programmed by Kosi. You could say they’re my Dr. Frankenstein—but less spooky."
]

greetings = [
    "Hello there, human!",
    "Hi! Ready for action.",
    "Greetings! How can I assist you?",
    "Hey! Systems are running smoothly.",
    "Hello! Always good to see you."
]

status_responses = [
    "I am just a robot, but I am feeling functional!",
    "All systems are operational. I feel great.",
    "I’m running at full capacity today.",
    "Better than yesterday—my circuits are freshly charged.",
    "I feel efficient. How about you?"
]

goodbyes = [
    "Goodbye! Powering down… just kidding.",
    "See you later, human.",
    "Goodbye! Don’t forget to charge me.",
    "Until next time!",
    "Shutting down my social module now. Bye!"
]

name_responses = [
    "My name is Uche X.",
    "I am Uche X, your humanoid assistant.",
    "They call me Uche X. Nice to meet you!",
    "I go by Uche X, but I answer to friend too.",
    "Uche X is my name, robotics is my game."
]

# -----------------------------------------
# Command Functions
# -----------------------------------------
def command_time():
    text_to_speech(f"The current time is {get_current_time()}.")

def command_date():
    text_to_speech(f"Today's date is {get_current_date()}.")

def command_talk_back():
    text_to_speech(random.choice(greetings))

def command_how_are_you():
    text_to_speech(random.choice(status_responses))

def command_set_timer():
    text_to_speech("Timers are not active in this test version.")

def command_change_voice():
    change_voice()

def command_exit():
    text_to_speech(random.choice(goodbyes))
    exit(0)

def command_name():
    text_to_speech(random.choice(name_responses))

def command_joke():
    text_to_speech(random.choice(jokes))

def command_creator():
    text_to_speech(random.choice(creator_responses))

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
    "who made you": command_creator,
    "who created you": command_creator,
    "who built you": command_creator,
}

# -----------------------------------------
# Text Cleaning for Better Recognition
# -----------------------------------------
def clean_command(text):
    text = text.lower()
    fillers = ["please", "can you", "could you", "would you", "hey", "Uche X", "um"]
    for f in fillers:
        text = text.replace(f, "")
    return text.strip()

def match_command(command_text):
    command_text = clean_command(command_text)
    keys = list(command_dict.keys())
    matches = difflib.get_close_matches(command_text, keys, n=1, cutoff=0.65)
    if matches:
        logging.info(f"Matched command '{command_text}' to '{matches[0]}'")
        return command_dict[matches[0]]
    else:
        logging.info(f"No matching command found for '{command_text}'")
        return None

# -----------------------------------------
# Vosk Speech Recognition Setup with Custom Grammar
# -----------------------------------------
vosk_model_path = "Your path Here"
vosk_model = Model(vosk_model_path)

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                 input=True, frames_per_buffer=4096)
stream.start_stream()

# Build grammar from command dictionary
command_phrases = [clean_command(cmd) for cmd in command_dict.keys()]
grammar = json.dumps(command_phrases)

def listen_for_phrase_vosk(prompt="Listening...", timeout=5):
    text_to_speech(prompt)
    start_time = time.time()
    rec = KaldiRecognizer(vosk_model, 16000, grammar)
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
