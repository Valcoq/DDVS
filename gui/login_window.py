from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal
import bcrypt
from database import get_db

class LoginWindow(QMainWindow):
    login_success = pyqtSignal(int, bool)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.username_input = QLineEdit(placeholderText="Benutzername")
        self.password_input = QLineEdit(placeholderText="Passwort", echoMode=QLineEdit.EchoMode.Password)
        self.login_btn = QPushButton("Login", clicked=self.authenticate)

        layout = QVBoxLayout()
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text().encode()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash, is_admin FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user:
                print(f"Gespeicherter Hash: {user[1]}")
                print(f"Eingegebenes Passwort: {password}")
                if bcrypt.checkpw(password, user[1]):
                    print("Passwort korrekt!")
                    self.login_success.emit(user[0], user[2])
                else:
                    print("Falsches Passwort!")
                    QMessageBox.warning(self, "Fehler", "Falsches Anmeldedaten!")
            else:
                print("Benutzer nicht gefunden!")
                QMessageBox.warning(self, "Fehler", "Falsche Anmeldedaten!")