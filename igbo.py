from gtts import gTTS
import os

text = "Ndeewo enyi m, kedu ka ụbọchị gị si aga?"
tts = gTTS(text=text, lang="ig")
tts.save("igbo.mp3")
os.system("mpg123 igbo.mp3")
