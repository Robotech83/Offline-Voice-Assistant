from vosk import Model, KaldiRecognizer
import pyaudio
import json

# Load Vosk model
model_path = "/home/Robo/Documents/Sonny/vosk-model-small-en-us-0.15"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Initialize PyAudio
mic = pyaudio.PyAudio()

# --- Automatically find the default input device ---
default_device_index = None
for i in range(mic.get_device_count()):
    dev_info = mic.get_device_info_by_index(i)
    if dev_info.get("maxInputChannels") > 0:  # It's a microphone
        default_device_index = i
        print(f"Using default mic: {dev_info['name']} (index {i})")
        break

if default_device_index is None:
    raise RuntimeError("No microphone input device found!")

# Open the microphone stream
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    input_device_index=default_device_index,  # Auto-selected mic
    frames_per_buffer=8192
)
stream.start_stream()

print("Listening...")
while True:
    data = stream.read(4096, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        print(result.get("text", ""))
