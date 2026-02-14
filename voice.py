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
voices = engine.getProperty("voices")
current_voice_index = 0

# Prevent overlap between speech + listening
speaking_lock = threading.Lock()

def text_to_speech(text):
    logging.info(f"Speaking: {text}")
    with speaking_lock:
        engine.say(text)
        engine.runAndWait()

def change_voice():
    global current_voice_index
    current_voice_index = (current_voice_index + 1) % len(voices)
    engine.setProperty("voice", voices[current_voice_index].id)
    text_to_speech("Voice changed.")

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
    "I was created by my builder, Robotech. Without them, I’d just be a box of parts.",
    "My maker is Robotech. They gave me life… well, as close as a robot can get.",
    "Technically, I was designed by Gaël Langevin as InMoov. But the real magic was done by Robotech.",
    "I was made by Robotech. If you don’t like how I behave, take it up with them!",
    "My creator is Robotech. Don’t worry, they programmed me to be nice… I think.",
    "I was brought into existence by Robotech. Some call them my maker… I call them my human.",
    "I was assembled and programmed by Robotech. You could say they’re my Dr. Frankenstein—but less spooky."
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
    "My name is Sonny.",
    "I am Sonny, your humanoid assistant.",
    "They call me Sonny. Nice to meet you!",
    "I go by Sonny, but I answer to friend too.",
    "Sonny is my name, robotics is my game."
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
    raise SystemExit

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
# Text Cleaning & Matching
# -----------------------------------------
def clean_command(text):
    text = text.lower()
    fillers = ["please", "can you", "could you", "would you", "hey", "sonny", "um"]
    for f in fillers:
        text = text.replace(f, "")
    return " ".join(text.split()).strip()

def match_command(command_text):
    command_text = clean_command(command_text)
    keys = list(command_dict.keys())
    matches = difflib.get_close_matches(command_text, keys, n=1, cutoff=0.65)
    if matches:
        logging.info(f"Matched '{command_text}' -> '{matches[0]}'")
        return command_dict[matches[0]]
    logging.info(f"No matching command for '{command_text}'")
    return None

# -----------------------------------------
# Vosk Speech Recognition Setup
# -----------------------------------------
vosk_model_path = "/home/Robo/Documents/Sonny/vosk-model-small-en-us-0.15"
vosk_model = Model(vosk_model_path)

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                 input=True, frames_per_buffer=4096)
stream.start_stream()

# Grammar helps Vosk focus on your known commands
command_phrases = [clean_command(cmd) for cmd in command_dict.keys()] + ["cancel"]
grammar = json.dumps(command_phrases)

def listen_for_phrase_vosk(prompt="Listening...", timeout=6):
    # IMPORTANT: don't speak the prompt (prevents mic feedback)
    logging.info(prompt)

    # Wait until we are not currently speaking
    while speaking_lock.locked():
        time.sleep(0.05)

    rec = KaldiRecognizer(vosk_model, 16000, grammar)
    result_text = ""
    start_time = time.time()

    while time.time() - start_time < timeout:
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result_dict = json.loads(rec.Result())
            result_text = result_dict.get("text", "")
            break

    return result_text

def listen_for_wake_word_vosk(timeout=12):
    heard = listen_for_phrase_vosk("Listening for wake word...", timeout)
    logging.info(f"Heard for wake: {heard}")
    return "hello" in heard.lower()

def listen_for_command_vosk(timeout=12):
    heard = listen_for_phrase_vosk("Listening for command...", timeout)
    logging.info(f"Heard command: {heard}")
    return heard

# -----------------------------------------
# Command Processing Loop
# -----------------------------------------
def process_commands():
    while True:
        if listen_for_wake_word_vosk(timeout=30):
            text_to_speech("How can I help you?")

            fail_count = 0

            while True:
                cmd_text = listen_for_command_vosk(timeout=30)

                # Nothing heard
                if not cmd_text:
                    fail_count += 1
                    if fail_count >= 3:
                        text_to_speech("I did not hear anything.")
                        fail_count = 0
                    continue

                fail_count = 0

                if "cancel" in cmd_text.lower():
                    text_to_speech("Exiting command mode.")
                    break

                func = match_command(cmd_text)
                if func:
                    try:
                        func()
                    except SystemExit:
                        return
                else:
                    text_to_speech("Can you repeat that?")


# -----------------------------------------
# Main
# -----------------------------------------
def main():
    thread = threading.Thread(target=process_commands, daemon=True)
    thread.start()

    try:
        while thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        text_to_speech("Shutting down. Goodbye!")
        logging.info("Assistant shutdown via KeyboardInterrupt.")
    finally:
        try:
            stream.stop_stream()
            stream.close()
            pa.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()

