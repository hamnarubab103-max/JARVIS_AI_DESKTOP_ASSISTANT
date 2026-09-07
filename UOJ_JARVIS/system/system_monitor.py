import psutil

def get_system_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"CPU usage is {cpu} percent and RAM usage is {ram} percent"
