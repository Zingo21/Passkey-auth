from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal
from ui.login_window import Ui_LoginWindow  # Genererad kod
from passkey_manager import PasskeyManager

class LoginWindow(QDialog, Ui_LoginWindow):
    login_success = pyqtSignal(dict)  # Signal vid lyckad inloggning
    
    def __init__(self, passkey_manager: PasskeyManager):
        super().__init__()
        self.setupUi(self)
        self.passkey_manager = passkey_manager
        
        # Koppla signaler
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_register.clicked.connect(self.show_register)
        
    def handle_login(self):
        username = self.username_input.text()
        if not username:
            QMessageBox.warning(self, "Fel", "Ange användarnamn")
            return
        
        try:
            # Steg 1: Begär autentisering
            auth_data = self.passkey_manager.authenticate_begin(username)
            
            # Steg 2: Visa WebAuthn-dialog (simulerat här)
            credential = {
                "id": "simulated_id",
                "rawId": next(iter(self.passkey_manager.credentials.keys()), b''),
                "type": "public-key",
                "response": {
                    "authenticatorData": b'simulated_data',
                    "clientDataJSON": json.dumps({
                        "type": "webauthn.get",
                        "challenge": auth_data['challenge'].hex(),
                        "origin": self.passkey_manager.origin
                    }).encode(),
                    "signature": b'simulated_signature'
                }
            }
            
            # Steg 3: Verifiera autentisering
            user = self.passkey_manager.authenticate_complete(
                credential,
                auth_data['challenge']
            )
            
            self.login_success.emit(user)
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Inloggningsfel", str(e))

    def show_register(self):
        from views.register_window import RegisterWindow
        self.register_window = RegisterWindow(self.passkey_manager)
        self.register_window.show()

    def handle_login(self):
        username = self.username_input.text()
        if not username:
            QMessageBox.warning(self, "Fel", "Ange användarnamn")
            return
        
        try:
            auth_data = self.passkey_manager.authenticate_begin(username)
            script = self.passkey_manager.get_web_authn_script(
                dict(auth_data['options']), 
                is_registration=False
            )
            
            self.auth_dialog = WebAuthnDialog(script)
            self.auth_dialog.credential_received.connect(
                lambda cred: self.finish_authentication(cred, auth_data['challenge'])
            )
            self.auth_dialog.error_occurred.connect(
                lambda err: QMessageBox.critical(self, "Fel", err)
            )
            self.auth_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Inloggningsfel", str(e))

    def finish_authentication(self, credential, challenge):
        try:
            user = self.passkey_manager.authenticate_complete(credential, challenge)
            self.login_success.emit(user)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Inloggningsfel", str(e))