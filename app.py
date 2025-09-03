import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox

class PasskeyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Passkey Login & Registration")
        self.setGeometry(100, 100, 400, 200)

        # Layout
        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)

        # Register button
        self.register_button = QPushButton("Register with Passkey")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        # Login button
        self.login_button = QPushButton("Login with Passkey")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def register(self):
        try:
            # Request registration challenge from the backend
            response = requests.get("http://localhost:5000/register")
            data = response.json()

            if "options" in data:
                # Simulate sending passkey data back to the server
                options = data["options"]
                complete_response = requests.post(
                    "http://localhost:5000/complete_registration", json=options
                )
                result = complete_response.json()
                self.status_label.setText(f"Registration: {result.get('status', 'Failed')}")
            else:
                self.status_label.setText("Registration failed: No options received")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def login(self):
        try:
            # Request login challenge from the backend
            response = requests.get("http://localhost:5000/login")
            data = response.json()

            if "options" in data:
                # Simulate sending passkey data back to the server
                options = data["options"]
                complete_response = requests.post(
                    "http://localhost:5000/complete_login", json=options
                )
                result = complete_response.json()
                self.status_label.setText(f"Login: {result.get('status', 'Failed')}")
            else:
                self.status_label.setText("Login failed: No options received")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasskeyApp()
    window.show()
    sys.exit(app.exec_())