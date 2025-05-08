from PyQt6.QtWidgets import (
    QMainWindow, 
    QTableWidget, 
    QTableWidgetItem, 
    QHeaderView, 
    QPushButton,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QMessageBox,
    QWidget
)
from PyQt6.QtCore import Qt
import bcrypt
import sqlite3
import os
from database import get_db

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        self.setWindowTitle("Admin Panel")

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Benutzername", "Admin"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.add_user_btn = QPushButton("Neuen Benutzer erstellen", clicked=self.open_add_user_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.add_user_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_users(self):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, is_admin FROM users")
            users = cursor.fetchall()

            self.table.setRowCount(len(users))
            for row, (user_id, username, is_admin) in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(str(user_id)))
                self.table.setItem(row, 1, QTableWidgetItem(username))
                self.table.setItem(row, 2, QTableWidgetItem("Ja" if is_admin else "Nein"))

                delete_btn = QPushButton("Löschen")
                delete_btn.setStyleSheet("background-color: #ff4444; color: white;")
                delete_btn.clicked.connect(lambda _, uid=user_id: self.delete_user(uid))
                self.table.setCellWidget(row, 3, delete_btn)

    def delete_user(self, user_id):
        confirm = QMessageBox.question(self, "Benutzer löschen", "Soll der Benutzer gelöscht werden?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            with get_db() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    self.load_users()
                    QMessageBox.information(self, "Erfolg", "Benutzer gelöscht!")
                except sqlite3.IntegrityError:
                    QMessageBox.critical(self, "Fehler", "Benutzer hat noch Dokumente! Lösche diese zuerst.")
    
    def delete_user_with_documents(self, user_id):
        confirm = QMessageBox.question(
            self,
            "Benutzer löschen",
            "Soll der Benutzer und ALLE seine Dokumente gelöscht werden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            with get_db() as conn:
                cursor = conn.cursor()
                try:
                    # 1. Dokumentpfade und Thumbnails abfragen
                    cursor.execute("SELECT file_path, thumbnail_path FROM documents WHERE owner_id = ?", (user_id,))
                    documents = cursor.fetchall()
                    
                    # 2. Dateien löschen
                    for file_path, thumb_path in documents:
                        try:
                            if file_path and os.path.exists(file_path):
                                os.remove(file_path)
                            if thumb_path and os.path.exists(thumb_path):
                                os.remove(thumb_path)
                        except Exception as e:
                            print(f"Fehler beim Löschen der Dateien: {e}")

                    # 3. Datenbankeinträge löschen
                    cursor.execute("DELETE FROM documents WHERE owner_id = ?", (user_id,))
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    
                    self.load_users()
                    QMessageBox.information(self, "Erfolg", "Benutzer und Dokumente wurden gelöscht!")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Fehler", f"Löschen fehlgeschlagen: {str(e)}")
                    conn.rollback()

    def open_add_user_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Neuer Benutzer")

        self.username_input = QLineEdit(placeholderText="Benutzername")
        self.password_input = QLineEdit(placeholderText="Passwort", echoMode=QLineEdit.EchoMode.Password)
        self.is_admin_checkbox = QCheckBox("Admin_Berechtigungen")
        submit_btn = QPushButton("Erstellen", clicked=lambda: self.create_user(dialog))

        layout = QVBoxLayout()
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.is_admin_checkbox)
        layout.addWidget(submit_btn)

        dialog.setLayout(layout)
        dialog.exec()
   
    def create_user(self, dialog):
        username = self.username_input.text()
        password = self.password_input.text().encode()
        is_admin = self.is_admin_checkbox.isChecked()

        if not username or not password:
            QMessageBox.warning(self, "Fehler", "Benutzername und Passwort dürfen nicht leer sein!")
            return
        
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                    (username, hashed_pw, is_admin)
                )
                conn.commit()
                self.load_users()
                dialog.close()
                QMessageBox.information(self, "Erfolg", "Benutzer wurde erstellt!")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Fehler", "Benutzername existiert bereits!")