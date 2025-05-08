from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSignal
import shutil
import os
from datetime import datetime
from database import get_db
from thumbnail import generate_thumbnail

class UploadWWindow(QDialog):
    upload_complete = pyqtSignal()

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("PDF hochladen")
        self.setFixedSize(400, 200)

        self.file_label = QLabel("Keine Datei ausgewählt")
        self.upload_btn = QPushButton("Datei auswählen", clicked=self.select_file)
        self.confirm_btn = QPushButton("Hochladen", clicked=self.upload_file)

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.confirm_btn)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF auswählen", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))

    def upload_file(self):
        if hasattr(self, 'file_path'):
            file_size = os.path.getsize(self.file_path)
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            thumbnail_path = generate_thumbnail(self.file_path)
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                        INSERT INTO documents (name, file_path, file_size, upload_date, owner_id, current_holder_id, thumbnail_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        os.path.basename(self.file_path),
                        self.file_path,
                        file_size,
                        upload_date,
                        self.user_id,
                        self.user_id,
                        thumbnail_path
                    ))
                conn.commit()
            save_dir = "documents"
            # os.makedirs(save_dir, exist_ok=True)
            # save_path = os.path.join(save_dir, f"{self.user_id}_{os.path.basename(self.file_path)}")
            # shutil.copy(self.file_path, save_path)
            self.upload_complete.emit()
            #self.close()