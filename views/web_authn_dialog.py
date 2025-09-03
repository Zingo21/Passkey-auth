from PyQt6.QtWidgets import QDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSignal
import tempfile
import os

class WebAuthnDialog(QDialog):
    credential_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, script: str):
        super().__init__()
        self.setWindowTitle("Använd din Passkey")
        self.setGeometry(100, 100, 500, 600)
        
        self.webview = QWebEngineView()
        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)
        
        # Skapa temporär HTML-fil
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.html', 
            delete=False,
            encoding='utf-8'
        )
        self.temp_file.write(f"""
        <html>
        <body>
            <script>
            {script}
            </script>
        </body>
        </html>
        """)
        self.temp_file.close()
        
        # Ladda HTML
        self.webview.load(QUrl.fromLocalFile(self.temp_file.name))
        
        # Exponera Python-funktioner för JavaScript
        self.webview.page().addToJavaScriptWindowObject("pywebview", self)
    
    def handleCredential(self, credential):
        """Anropas från JavaScript"""
        self.credential_received.emit({
            'id': credential['id'],
            'rawId': bytes(credential['rawId']),
            'type': credential['type'],
            'response': {
                'attestationObject': bytes(credential['response']['attestationObject']),
                'clientDataJSON': bytes(credential['response']['clientDataJSON'])
            }
        })
        self.close()
    
    def handleError(self, error):
        """Anropas från JavaScript"""
        self.error_occurred.emit(error)
        self.close()
    
    def closeEvent(self, event):
        """Städa upp temporär fil"""
        os.unlink(self.temp_file.name)
        super().closeEvent(event)