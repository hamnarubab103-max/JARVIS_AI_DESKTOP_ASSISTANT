from automation.web_controller import open_website
from system.system_monitor import get_system_status
import datetime

def route_command(command: str):

    command = command.lower()

    if "open youtube" in command:
        open_website("https://www.youtube.com")
        return "Opening YouTube"

    elif "open google" in command:
        open_website("https://www.google.com")
        return "Opening Google"

    elif "time" in command:
        return f"The time is {datetime.datetime.now().strftime('%H:%M')}"

    elif "system status" in command:
        return get_system_status()

    else:
        return "Sorry, I did not understand that command"
