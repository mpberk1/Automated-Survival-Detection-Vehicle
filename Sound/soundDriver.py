from pydub import AudioSegment
from pydub.playback import play

# Load the MP3 file
audio = AudioSegment.from_mp3("LifeCheck.mp3")

# Play the audio
play(audio)
