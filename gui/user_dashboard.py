from PyQt6.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QFileDialog,
    QComboBox,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QHeaderView,
    QToolBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
import shutil
import os
import pymupdf as fitz
from gui.upload_window import UploadWWindow
from gui.pdf_viewer import PDFViewer
from database import get_user_documents, add_document, get_all_users, get_db
from thumbnail import generate_thumbnail
from gui.notification_badge import NotificationBadge
import datetime

class UserDashboard(QMainWindow):
    update_documents_signal = pyqtSignal()

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        self.load_documents()
        self.update_documents_signal.connect(self.load_documents)

        # Benachrichtigungs-Badge hinzufügen
        self.notification_badge = NotificationBadge()
        toolbar = QToolBar("Benachrichtigungen")
        self.addToolBar(toolbar)
        toolbar.addWidget(self.notification_badge)

    def get_documents_dir(self):
        """Gibt den korrekten Dokumenten-Pfad zurück"""
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs_dir = os.path.join(project_dir, "documents")
        os.makedirs(docs_dir, exist_ok=True)  # Erstellt Ordner falls nicht vorhanden
        return docs_dir

    def upload_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF auswählen", "", "PDF Files (*.pdf)")
        if file_path:
            docs_dir = self.get_documents_dir()  # Korrekter Projektordner
            save_path = os.path.join(docs_dir, f"{self.user_id}_{os.path.basename(file_path)}")
            shutil.copy(file_path, save_path)
            
            # Metadaten in DB speichern
            add_document(
                name=os.path.basename(file_path),
                file_path=save_path,  # Absoluter Pfad
                owner_id=self.user_id,
                file_size=os.path.getsize(file_path),
                upload_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                thumbnail_path=generate_thumbnail(save_path)  # Thumbnail wird im Projektordner erstellt
            )
            self.update_documents_signal.emit()

    def upload_dropped_file(self, file_path):
        docs_dir = self.get_documents_dir()
        save_path = os.path.join(docs_dir, f"{self.user_id}_{os.path.basename(file_path)}")
        
        # Kopiere Datei
        shutil.copy(file_path, save_path)
        
        # Erstelle Eintrag in DB
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents 
                (name, file_path, file_size, upload_date, owner_id, current_holder_id, thumbnail_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                os.path.basename(file_path),
                save_path,
                os.path.getsize(file_path),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.user_id,
                self.user_id,
                generate_thumbnail(save_path)
            ))
            conn.commit()
        
        self.load_documents()

    def setup_ui(self):
        self.setWindowTitle("Dokumentenverwaltung")
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 6 Spalten
        self.table.setHorizontalHeaderLabels(["Thumbnail", "Name", "Größe", "Datum", "Ansehen", "Löschen"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        self.upload_btn = QPushButton("📤 PDF hochladen", clicked=self.open_upload_window)
        
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.upload_btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_upload_window(self):
        self.upload_window = UploadWWindow(self.user_id)
        self.upload_window.upload_complete.connect(self.load_documents)
        self.upload_window.show()

    def load_documents(self):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM documents WHERE owner_id = ? OR current_holder_id = ?", (self.user_id, self.user_id))
                documents = cursor.fetchall()
                print("=== DATENBANKINHALT ===")
            for doc in documents:
                print(f"ID: {doc[0]}, Pfad: {doc[2]}, Existiert: {os.path.exists(doc[2])}")
                self.update_table(documents)
        except Exception as e:
            print(f"Fehler beim Laden der Dokumente: {str(e)}")

    def delete_document(self, doc_id, file_path, thumbnail_path):
        # Sicherheitsabfrage
        confirm = QMessageBox.question(
            self,
            "Dokument löschen",
            "Soll das Dokument wirklich gelöscht werden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # 1. Dateien vom System löschen
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                # 2. Aus Datenbank löschen
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
                    conn.commit()
                
                # 3. Tabelle aktualisieren
                self.load_documents()
                QMessageBox.information(self, "Erfolg", "Dokument wurde gelöscht!")
                
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Löschen fehlgeschlagen: {str(e)}")

    def update_table(self, documents):
        self.table.setRowCount(len(documents))
        for row, document in enumerate(documents):
            doc_id, name, file_path, file_size, upload_date, owner_id, current_holder_id, thumbnail_path = document
            
            # Thumbnail
            thumbnail_label = QLabel()
            pixmap = QPixmap(thumbnail_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            thumbnail_label.setPixmap(pixmap)
            
            # Metadaten
            size_mb = f"{file_size / (1024 * 1024):.2f} MB"
            upload_date = upload_date.split(".")[0]

            # Buttons
            view_btn = QPushButton("👀 Ansehen")
            view_btn.clicked.connect(lambda _, fp=file_path: self.show_pdf(fp))
            
            delete_btn = QPushButton("🗑️ Löschen")
            delete_btn.setStyleSheet("background-color: #ff4444; color: white;")
            delete_btn.clicked.connect(lambda _, d=doc_id, fp=file_path, tp=thumbnail_path: self.delete_document(d, fp, tp))

            # Tabelle füllen
            self.table.setCellWidget(row, 0, thumbnail_label)
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(size_mb))
            self.table.setItem(row, 3, QTableWidgetItem(upload_date))
            self.table.setCellWidget(row, 4, view_btn)
            self.table.setCellWidget(row, 5, delete_btn)  # Lösch-Button hinzufügen

    def download_pdf(self, doc_id):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
                result = cursor.fetchone()
                
                if result:
                    file_path = result[0]
                    if os.path.exists(file_path):
                        os.startfile(file_path)
                    else:
                        QMessageBox.critical(self, "Fehler", "Die PDF-Datei wurde nicht gefunden!")
                else:
                    QMessageBox.critical(self, "Fehler", "Dokument nicht gefunden!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Herunterladen der PDF: {str(e)}")

    def show_pdf(self, file_path):
        try:
            if os.path.exists(file_path):
                self.viewer = PDFViewer(file_path)
                self.viewer.show()
            else:
                QMessageBox.critical(self, "Fehler", "Die PDF-Datei wurde nicht gefunden!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Öffnen der PDF: {str(e)}")