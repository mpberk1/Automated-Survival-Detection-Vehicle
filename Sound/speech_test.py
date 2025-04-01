import speech_recognition as sr
recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("say something")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    audio=recognizer.listen(source)
try:
    text=recognizer.recognize_google(audio)
    print("you said: ", text)
except sr.UnknownValueError:
    print("canot understand audio")
except sr.RequestError:
    print("API error")
    