from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class VoiceWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.title = QLabel("VOICE MODULE")
        self.title.setObjectName("PanelTitle")

        self.status = QLabel("Status: Idle")
        self.command = QLabel("Command: ---")

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.command)

        self.setLayout(layout)
