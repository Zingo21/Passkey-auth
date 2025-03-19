import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel

class PasskeyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Passkey Desktop App")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.register_button = QPushButton("Register Passkey", self)
        self.register_button.clicked.connect(self.register_passkey)
        layout.addWidget(self.register_button)

        self.login_button = QPushButton("Log in with Passkey", self)
        self.login_button.clicked.connect(self.authenticate_passkey)
        layout.addWidget(self.login_button)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def register_passkey(self):
        username = self.username_input.text()
        if not username:
            self.status_label.setText("Type a username!")
            return

        response = requests.post("http://localhost:5000/register/begin", json={"username": username})
        if response.status_code == 200:
            self.status_label.setText("Passkey registered!")
        else:
            self.status_label.setText("Registration failed!")

    def authenticate_passkey(self):
        username = self.username_input.text()
        if not username:
            self.status_label.setText("Type a username!")
            return

        response = requests.post("http://localhost:5000/authenticate/begin", json={"username": username})
        if response.status_code == 200:
            self.status_label.setText("Logged in with Passkey!")
        else:
            self.status_label.setText("Authentication failed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasskeyApp()
    window.show()
    sys.exit(app.exec())
