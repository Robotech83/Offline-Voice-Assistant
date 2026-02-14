import subprocess
import time
import logging
import os

# -----------------------------------------
# Logging Setup
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Paths to your scripts
facial_recognition_script = "/home/Robo/face_rec/Face Recognition/face_recogn.py"
voice_assistant_script = "/home/Robo/Documents/Sonny/Control_Sonny.py"
arduino_control_script = "/home/Robo/Arduino/Tracking/Tracking.ino"
arduino_PIR_script = "/home/Robo/Arduino/pir_test2"

scripts = {
    "Facial Recognition": facial_recognition_script,
    "Voice Assistant": voice_assistant_script,
    "Arduino Control": arduino_control_script,
    "PIR_TEST2": arduino_PIR_script
}

processes = {}

try:
    # Start all scripts
    for name, path in scripts.items():
        if not os.path.exists(path):
            logging.error(f"{name} script not found at {path}")
            continue

        workdir = os.path.dirname(path)
        logging.info(f"Starting {name} from {workdir}...")
        processes[name] = subprocess.Popen(["python3", path], cwd=workdir)

    # Keep the master running
    while True:
        # Check if any process has crashed
        for name, process in list(processes.items()):
            retcode = process.poll()
            if retcode is not None:  # Process has ended
                logging.error(f"{name} stopped unexpectedly (exit code {retcode}). Restarting...")
                workdir = os.path.dirname(scripts[name])
                processes[name] = subprocess.Popen(["python3", scripts[name]], cwd=workdir)
                logging.info(f"{name} restarted successfully.")
        time.sleep(5)

except KeyboardInterrupt:
    logging.info("Shutting down all processes...")
    for name, process in processes.items():
        logging.info(f"Stopping {name}...")
        process.terminate()
