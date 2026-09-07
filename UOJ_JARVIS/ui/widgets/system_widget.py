from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
import psutil

class SystemWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.title = QLabel("SYSTEM STATUS")
        self.title.setObjectName("PanelTitle")

        self.cpu_label = QLabel()
        self.ram_label = QLabel()

        layout.addWidget(self.title)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)

        self.setLayout(layout)
        self.update_stats()

    def update_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        self.cpu_label.setText(f"CPU Usage: {cpu}%")
        self.ram_label.setText(f"RAM Usage: {ram}%")
