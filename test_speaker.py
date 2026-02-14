import pygame
import time

def test_speaker():
    # Initialize pygame
    pygame.init()

    # Set up the audio mixer
    pygame.mixer.init()

    # Load a test sound (you can replace this with your own sound file)
    # Make sure the sound file is in the same directory as the script or provide the full path
    sound_file = "sample-3s.wav"  # Replace with your sound file
    try:
        sound = pygame.mixer.Sound(sound_file)
    except FileNotFoundError:
        print(f"Error: Sound file '{sound_file}' not found.")
        return

    # Play the sound
    print("Playing test sound...")
    sound.play()

    # Wait for the sound to finish playing
    time.sleep(sound.get_length())  # Wait for the duration of the sound

    # Clean up
    pygame.quit()
    print("Test complete.")

# Run the speaker test
test_speaker()
