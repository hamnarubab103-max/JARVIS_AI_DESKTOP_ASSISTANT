import speech_recognition as sr
import pyttsx3
import webbrowser
import os

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        speak("Sorry, I didn't understand.")
        return ""

def open_website(command):
    if "google" in command:
        webbrowser.open("https://www.google.com")
    elif "youtube" in command:
        webbrowser.open("https://www.youtube.com")
    elif "facebook" in command:
        webbrowser.open("https://www.facebook.com")
    elif "instagram" in command:
        webbrowser.open("https://www.instagram.com")
    elif "github" in command:
        webbrowser.open("https://www.github.com")

def open_application(command):
    if "notepad" in command:
        os.system("notepad")
    elif "calculator" in command:
        os.system("calc")
    elif "chrome" in command:
        os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    elif "vs code" in command:
        os.startfile("C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")

def jarvis():
    speak("Hello, I am Jarvis. How can I help you?")
    while True:
        command = take_command()

        if "open" in command:
            open_website(command)
            open_application(command)

        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break

        elif command != "":
            speak("I can open websites and applications for you.")

# Run JARVIS
jarvis()
