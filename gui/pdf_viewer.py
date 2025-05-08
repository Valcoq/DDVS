from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import fitz

class PDFViewer(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        try:
            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl.fromLocalFile(file_path))
            self.setCentralWidget(self.browser)
            self.setWindowTitle("PDF Viewer")
            self.resize(800, 600)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"PDF konnte nicht geladen werden {str(e)}")
        self.file_path = file_path
        self.setup_ui()

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(file_path))
        self.setCentralWidget(self.browser)
        self.resize(800, 600)

    def setup_ui(self):
        self.setWindowTitle("PDF Viewer")
        self.text_browser = QTextBrowser()

        doc = fitz.open(self.file_path)
        text = ""
        for page in doc:
            text += page.get_text()

        self.text_browser.setText(text)

        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
