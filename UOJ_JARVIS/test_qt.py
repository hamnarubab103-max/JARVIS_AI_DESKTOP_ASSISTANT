import speech_recognition as sr 
import pyttsx3
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    try:
        print("Listenting....")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(source)
        print(text)
    except:
        print("Sorry")
    