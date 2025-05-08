import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar
from gui.login_window import LoginWindow
from gui.admin_panel import AdminPanel
from gui.user_dashboard import UserDashboard
from gui.notification_badge import NotificationBadge
from database import init_db

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class App:
    def __init__(self):
        init_db()
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.handle_login)
        self.login_window.show()

    def handle_login(self, user_id, is_admin):
        self.login_window.close()
        if is_admin:
            self.admin_panel = AdminPanel()
            self.admin_panel.show()
        else:
            self.user_dashboard = UserDashboard(user_id)
            self.user_dashboard.show()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    App().run()