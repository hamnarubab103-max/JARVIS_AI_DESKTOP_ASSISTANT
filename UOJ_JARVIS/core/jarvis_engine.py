from voice.speech_to_text import listen
from voice.text_to_speech import speak
from core.command_router import route_command

class JarvisEngine:

    def start(self):
        speak("Jarvis online. How can I help you?")

        while True:
            command = listen()

            if command is None:
                continue

            if "exit" in command or "quit" in command:
                speak("Shutting down. Goodbye.")
                break

            response = route_command(command)
            speak(response)
