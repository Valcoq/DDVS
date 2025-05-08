from PyQt6.QtWidgets import (
    QPushButton,
    QMenu,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
from database import get_db

class NotificationBadge(QPushButton):
    def __init__(self):
        super().__init__("Ö")
        self.setFont(QFont("Arial", 14))
        self.setStyleSheet("QPushButton { border: none; }")
        self.menu = QMenu()
        self.setMenu(self.menu)
        self.load_notifications()

    def load_notifications(self):
        self.menu.clear()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT message, timestamp FROM notifications WHERE is_read = FALSE")
            for msg, timestamp in cursor.fetchall():
                self.menu.addAction(f"{timestamp}: {msg}").triggered.connect(
                    lambda _, msg=msg: self.mark_as_read(msg)
                )

    def mark_as_read(self, message):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = TRUE WHERE message = ?", (message,))
            conn.commit()
        self.load_notifications()