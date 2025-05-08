import os
import sqlite3
import bcrypt
from contextlib import contextmanager
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    print("Initialisiere Datenbank...")
    try:
        with get_db() as conn:
        #conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            print("Datenbankverbindung erfolgreich hergestellt.")
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password_hash TEXT NOT NULL,
                                is_admin BOOLEAN DEFAULT FALSE
                    )
            ''')
            print("Tabelle 'users' erstellt.")
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS documents (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                file_path TEXT NOT NULL,
                                file_size INTEGER,
                                upload_date DATETIME,
                                owner_id INTEGER,
                                current_holder_id INTEGER,
                                thumbnail_path TEXT,
                                FOREIGN KEY (owner_id) REFERENCES users(id),
                                FOREIGN KEY (current_holder_id) REFERENCES users(id)
                    )
            ''')
            print("Tabelle 'documents' erstellt.")
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS document_versions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                document_id INTEGER,
                                version INTEGER,
                                file_path TEXT,
                                owner_id INTEGER,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (document_id) REFERENCES documents(id)
                    )
            ''')
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS audit_log (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                action TEXT,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users(id)
                    )
            ''')
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS notifications (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                message TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURENT_TIMESTAMP,
                                is_read BOOLEAN DEFAULT FALSE,
                                FOREIGN KEY(user_id) REFERENCES users(id)
                    )
            ''')
            print("Tabelle 'notifications' erstellt.")
            admin_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt())
            cursor.execute('''
                    INSERT OR IGNORE INTO users (username, password_hash, is_admin)
                    VALUES (?, ?, ?)
                ''', ("admin", admin_hash, True))
            conn.commit()
            print("Admin-Benutzer erfolgreich hinzugefügt")
            print("Datenbank erfolgreich initialisiert")
    except Exception as e:
        print(f"Fehler beim Initialisieren der Datenbank: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def get_user_documents(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
                SELECT id, name, file_path FROM documents
                WHERE current_holder_id = ? OR ownder_id = ?
            ''', (user_id, user_id))
        return cursor.fetchall()
    
def add_document(name, file_path, owner_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
                INERT INTO documents (name, file_path, owner_id, current_holder_id)
                VALUES (? ? ? ?)
            ''', (name, file_path, owner_id, owner_id))
        conn.commit()

def get_all_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        return cursor.fetchall()