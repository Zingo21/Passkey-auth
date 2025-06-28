import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from passkey_manager import PasskeyManager
from views.login_window import LoginWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.passkey_manager = PasskeyManager()
        
        # Main window setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout and componenter
        layout = QVBoxLayout()
        self.label = QLabel("Välkommen! Logga in för att fortsätta.")
        layout.addWidget(self.label)
        self.central_widget.setLayout(layout)
        
        # Visa inloggningsfönster
        self.show_login()
    
    def show_login(self):
        self.login_window = LoginWindow(self.passkey_manager)
        self.login_window.login_success.connect(self.handle_login_success)
        self.login_window.exec()
    
    def handle_login_success(self, user):
        self.label.setText(f"Välkommen {user['display_name']}!")
        self.login_window.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())