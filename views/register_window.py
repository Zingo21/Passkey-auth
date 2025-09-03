from PyQt6.QtWidgets import QDialog, QMessageBox
from ui.register_window import Ui_RegisterWindow  # Genererad kod
import json

class RegisterWindow(QDialog, Ui_RegisterWindow):
    def __init__(self, passkey_manager):
        super().__init__()
        self.setupUi(self)
        self.passkey_manager = passkey_manager
        self.btn_register.clicked.connect(self.handle_register)
        
    def handle_register(self):
        username = self.username_input.text()
        if not username:
            QMessageBox.warning(self, "Fel", "Ange användarnamn")
            return
        
        try:
            # Steg 1: Starta registrering
            reg_data = self.passkey_manager.register_begin(username)
            
            # Steg 2: Visa WebAuthn-dialog (simulerat här)
            credential = {
                "id": "simulated_id",
                "rawId": secrets.token_bytes(32),
                "type": "public-key",
                "response": {
                    "attestationObject": b'simulated_attestation',
                    "clientDataJSON": json.dumps({
                        "type": "webauthn.create",
                        "challenge": reg_data['challenge'].hex(),
                        "origin": self.passkey_manager.origin
                    }).encode()
                }
            }
            
            # Steg 3: Slutför registrering
            success = self.passkey_manager.register_complete(
                reg_data['user_id'],
                credential,
                reg_data['challenge']
            )
            
            if success:
                QMessageBox.information(self, "Lyckades", "Passkey registrerad!")
                self.close()
            else:
                QMessageBox.critical(self, "Fel", "Registrering misslyckades")
                
        except Exception as e:
            QMessageBox.critical(self, "Registreringsfel", str(e))