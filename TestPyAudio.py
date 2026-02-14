import pyaudio

p = pyaudio.PyAudio()
print("PyAudio is installed and working!")
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
