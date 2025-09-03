from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QPushButton

class ManageKeysWindow(QDialog):
    def __init__(self, passkey_manager, username):
        super().__init__()
        self.passkey_manager = passkey_manager
        self.username = username
        
        self.setWindowTitle("Hantera dina Passkeys")
        self.setLayout(QVBoxLayout())
        
        self.keys_list = QListWidget()
        self.layout().addWidget(self.keys_list)
        
        self.btn_remove = QPushButton("Ta bort vald Passkey")
        self.btn_remove.clicked.connect(self.remove_selected)
        self.layout().addWidget(self.btn_remove)
        
        self.load_keys()
    
    def load_keys(self):
        self.keys_list.clear()
        credentials = self.passkey_manager.get_user_credentials(self.username)
        for cred in credentials:
            self.keys_list.addItem(f"Passkey: {cred['id'][:8].hex()}...")
    
    def remove_selected(self):
        selected = self.keys_list.currentRow()
        if selected >= 0:
            credentials = self.passkey_manager.get_user_credentials(self.username)
            if selected < len(credentials):
                cred_id = credentials[selected]['id']
                if self.passkey_manager.remove_credential(cred_id):
                    self.load_keys()