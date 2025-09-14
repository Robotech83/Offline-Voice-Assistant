import logging
import threading
import time
import difflib
import json
import random
import os
import subprocess
from datetime import datetime

# --- NEW imports for this merged build ---
import serial
import cv2
from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa

from vosk import Model, KaldiRecognizer
import pyaudio

# -----------------------------------------
# Logging
# -----------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------------------
# SERIAL → Arduino (controls PCA9685)
# -----------------------------------------
ARDUINO_PORT = "/dev/ttyACM0"  # change if needed
BAUD = 9600

arduino = None
def init_serial():
    global arduino
    try:
        arduino = serial.Serial(ARDUINO_PORT, BAUD, timeout=1)
        time.sleep(2)  # allow Arduino to reset
        logging.info(f"Connected to Arduino on {ARDUINO_PORT}")
    except Exception as e:
        logging.error(f"Serial open failed: {e}. Mouth/head will be disabled until fixed.")

def set_servo(name, angle):
    if arduino and arduino.is_open:
        msg = f"{name}:{int(angle)}\n".encode()
        arduino.write(msg)

# Servo helpers
MOUTH_CLOSED = 90
MOUTH_OPEN   = 120
def mouth_open():  set_servo("mouth", MOUTH_OPEN)
def mouth_close(): set_servo("mouth", MOUTH_CLOSED)
def move_head(pan, tilt):
    set_servo("pan", int(pan))
    set_servo("tilt", int(tilt))

# -----------------------------------------
# CAMERA + Face Tracking (runs in a thread)
# -----------------------------------------
cap = None
face_enabled = True
pan_angle = 90
tilt_angle = 90

def init_camera():
    global cap, pan_angle, tilt_angle
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.warning("Camera not found. Face tracking disabled.")
            return
        move_head(pan_angle, tilt_angle)  # center
    except Exception as e:
        logging.warning(f"Camera init failed: {e}")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def track_face_once():
    global pan_angle, tilt_angle
    if not cap: return
    ok, frame = cap.read()
    if not ok: return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        cx, cy = x + w // 2, y + h // 2
        fx, fy = frame.shape[1] // 2, frame.shape[0] // 2

        # Deadband 40px, then nudge
        if cx < fx - 40: pan_angle += 2
        elif cx > fx + 40: pan_angle -= 2
        if cy < fy - 40: tilt_angle -= 2
        elif cy > fy + 40: tilt_angle += 2

        # Clamp to safe range; tweak for your mechanics
        pan_angle  = max(60, min(120, pan_angle))
        tilt_angle = max(70, min(110, tilt_angle))
        move_head(pan_angle, tilt_angle)

def tracking_loop():
    while True:
        if face_enabled:
            track_face_once()
        time.sleep(0.05)

# -----------------------------------------
# LIP-SYNC Speech
#   EN: espeak-ng phonemes
#   IG: gTTS + amplitude analysis
# -----------------------------------------
def speak_english(text):
    logging.info(f"Speaking EN: {text}")

    # 1) Get phoneme stream (approximate timing)
    result = subprocess.run(
        ["espeak-ng", "-v", "en", "--pho", text],
        capture_output=True, text=True
    )
    phonemes = [ln for ln in result.stdout.splitlines() if ln.strip()]

    # 2) Play audio concurrently
    audio_thread = threading.Thread(target=lambda: os.system(f'espeak-ng -v en "{text}"'))
    audio_thread.start()

    # 3) Move mouth per phoneme (tweak durations for your servo)
    for _ in phonemes:
        mouth_open()
        time.sleep(0.10)
        mouth_close()
        time.sleep(0.05)

    audio_thread.join()
    mouth_close()

def speak_igbo(text):
    logging.info(f"Speaking IG: {text}")
    # 1) TTS to MP3
    tts = gTTS(text=text, lang="ig")
    tts.save("igbo.mp3")

    # 2) Load audio samples
    audio = AudioSegment.from_mp3("igbo.mp3")
    samples = audio.get_array_of_samples()

    # 3) Play audio
    play_obj = sa.play_buffer(
        samples,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )

    # 4) Amplitude-driven lip-sync
    chunk = 240  # ~5ms @ 48kHz; adjust by frame_rate below
    threshold = 600  # tune for your audio level
    sr = audio.frame_rate
    for i in range(0, len(samples), chunk):
        sect = samples[i:i+chunk]
        if not sect:
            break
        amp = (max(sect) - min(sect)) if len(sect) else 0
        if amp > threshold:
            mouth_open()
        else:
            mouth_close()
        time.sleep(chunk / max(1, sr))

    mouth_close()
    play_obj.wait_done()

# Unified TTS entry
current_lang = "en"  # "en" or "ig"
def text_to_speech(text, lang=None):
    use_lang = lang or current_lang
    if use_lang == "ig":
        speak_igbo(text)
    else:
        speak_english(text)

# -----------------------------------------
# Utilities
# -----------------------------------------
def get_current_time(): return datetime.now().strftime("%I:%M %p")
def get_current_date(): return datetime.now().strftime("%B %d, %Y")

# -----------------------------------------
# Responses
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
    "I was created by my builder, Robotech83. Without them, I’d just be a box of parts.",
    "My maker is Robotech83. They gave me life… well, as close as a robot can get.",
    "Technically, I was designed by Gaël Langevin as InMoov. But the real magic was done by Robotech83.",
    "I was made by Robotech83. If you don’t like how I behave, take it up with them!",
    "My creator is Robotech83. Don’t worry, they programmed me to be nice… I think.",
    "I was brought into existence by Robotech83. Some call them my maker… I call them my human.",
    "I was assembled and programmed by Robotech83. You could say they’re my Dr. Frankenstein—but less spooky."
]

greetings = [
    "Hello there, human!",
    "Hi! Ready for action.",
    "Greetings! How can I assist you?",
    "Hey! Systems are running smoothly.",
    "Hello! Always good to see you.",
    "Ọ dị mma."
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
# Commands
# -----------------------------------------
def command_time():       text_to_speech(f"The current time is {get_current_time()}.", "en")
def command_date():       text_to_speech(f"Today's date is {get_current_date()}.", "en")
def command_talk_back():  text_to_speech(random.choice(greetings))
def command_how_are_you():text_to_speech(random.choice(status_responses))
def command_set_timer():  text_to_speech("Timers are not active in this test version.", "en")
def command_exit():
    text_to_speech(random.choice(goodbyes))
    raise SystemExit

def command_name():    text_to_speech(random.choice(name_responses))
def command_joke():    text_to_speech(random.choice(jokes))
def command_creator(): text_to_speech(random.choice(creator_responses))

# NEW: language switching
def command_lang_igbo():
    global current_lang
    current_lang = "ig"
    text_to_speech("Agbanweela m asụsụ m gaa na Igbo.", "ig")  # I've switched to Igbo.

def command_lang_english():
    global current_lang
    current_lang = "en"
    text_to_speech("I have switched my language to English.", "en")

# NEW: center head
def command_center_head():
    global pan_angle, tilt_angle
    pan_angle, tilt_angle = 90, 90
    move_head(pan_angle, tilt_angle)
    text_to_speech("Centered.", "en")

command_dict = {
    "what time is it": command_time,
    "what is today's date": command_date,
    "hello": command_talk_back,
    "kedu": command_talk_back,
    "how are you": command_how_are_you,
    "set timer": command_set_timer,
    "goodbye": command_exit,
    "what is your name": command_name,
    "tell me a joke": command_joke,
    "make me laugh": command_joke,
    "say something funny": command_joke,
    "who made you": command_creator,
    "who created you": command_creator,
    "who built you": command_creator,
    # language switches
    "switch to igbo": command_lang_igbo,
    "speak igbo": command_lang_igbo,
    "switch to english": command_lang_english,
    "speak english": command_lang_english,
    # head
    "center head": command_center_head,
}

# -----------------------------------------
# Text Cleaning & Matching
# -----------------------------------------
def clean_command(text):
    text = text.lower()
    fillers = ["please", "can you", "could you", "would you", "hey", "sonny", "um"]
    for f in fillers:
        text = text.replace(f, "")
    return text.strip()

def match_command(command_text):
    command_text = clean_command(command_text)
    keys = list(command_dict.keys())
    matches = difflib.get_close_matches(command_text, keys, n=1, cutoff=0.65)
    if matches:
        logging.info(f"Matched '{command_text}' → '{matches[0]}'")
        return command_dict[matches[0]]
    logging.info(f"No matching command for '{command_text}'")
    return None

# -----------------------------------------
# Vosk Speech Recognition (offline)
# -----------------------------------------
vosk_model_path = "/home/Robo/Documents/Sonny/vosk-model-small-en-us-0.15"
vosk_model = Model(vosk_model_path)

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                 input=True, frames_per_buffer=4096)
stream.start_stream()

def listen_for_phrase_vosk(prompt="Listening...", timeout=5):
    # Speak prompt in current language but keep it short to avoid mic feedback
    logging.info(prompt)
    rec = KaldiRecognizer(vosk_model, 16000)
    result_text = ""
    start = time.time()
    while time.time() - start < timeout:
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result_dict = json.loads(rec.Result())
            result_text = result_dict.get("text", "")
            break
    return result_text

def listen_for_wake_word_vosk(timeout=5):
    heard = listen_for_phrase_vosk("Listening for wake word", timeout)
    logging.info(f"Heard for wake: {heard}")
    return "hello" in heard.lower() or "sonny" in heard.lower()

def listen_for_command_vosk(timeout=5):
    heard = listen_for_phrase_vosk("Listening for command", timeout)
    logging.info(f"Heard command: {heard}")
    return heard

# -----------------------------------------
# Command Processing
# -----------------------------------------
def process_commands():
    while True:
        if listen_for_wake_word_vosk(timeout=5):
            text_to_speech(random.choice(greetings))  # speaks in current_lang
            while True:
                cmd_text = listen_for_command_vosk(timeout=6)
                if not cmd_text:
                    continue
                if "cancel" in cmd_text.lower():
                    text_to_speech("Exiting command mode.", "en")
                    break
                func = match_command(cmd_text)
                if func:
                    try:
                        func()
                    except SystemExit:
                        text_to_speech("Shutting down. Goodbye!", "en")
                        os._exit(0)
                else:
                    text_to_speech("I did not understand that command.", "en")

# -----------------------------------------
# Main
# -----------------------------------------
def main():
    init_serial()
    init_camera()

    # Start face tracking thread (daemon)
    threading.Thread(target=tracking_loop, daemon=True).start()

    # Start command loop (daemon)
    threading.Thread(target=process_commands, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: exiting.")
    finally:
        if cap: cap.release()
        if arduino and arduino.is_open: arduino.close()
        stream.stop_stream(); stream.close(); pa.terminate()

if __name__ == "__main__":
    main()
