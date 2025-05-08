
# 📂 DDVS – Daten- und Dokumentverwaltungssoftware

> *Ein sicheres System zur Verwaltung und Weitergabe sensibler Dokumente – direkt in der Anwendung, ganz ohne offene Serverordner.*

---

## 🔐 Was ist DDVS?

DDVS steht für **Daten- und Dokumentverwaltungssoftware**.  
Es handelt sich um ein in Python entwickeltes System zur sicheren Speicherung, Anzeige und Verwaltung von Dokumenten – inklusive Benutzerverwaltung und Zugriffsschutz.  

💡 Ideal für Umgebungen, in denen vertrauliche Unterlagen **nicht öffentlich auf einem Server sichtbar sein dürfen** und trotzdem **intern bearbeitet und geteilt** werden sollen.

---

## ✨ Aktueller Funktionsumfang

- 👤 **Benutzerverwaltung**
  - Admin kann neue Benutzer anlegen & löschen
  - Standard-Admin: `admin` / `admin`

- 📑 **Dokumentenhandling**
  - Benutzer können Dokumente **hochladen**, **herunterladen** und **ansehen**
  - Dokumente werden **intern abgespeichert**, nicht sichtbar im Dateisystem

---

## 🧰 Verwendete Technologien

- 🐍 Python 3
- 🖼️ PyQt6 (inkl. `QtWebEngine` für integrierte Anzeige)
- 🗃️ SQLite (lokale Datenbank für Benutzer und Dokumente)
- 🖨️ `fitz` (PyMuPDF) für PDF-Verarbeitung
- 🖌️ Pillow für Bildvorverarbeitung

---

## 🔒 Ziel der Anwendung

> Eine **geschlossene Umgebung** zur Dokumentenverwaltung und Zusammenarbeit – ohne Datei-Explorer, ohne Web-Zugriff, ohne Datenlecks.

🛡️ Dokumente sollen:
- **ausschließlich über die App** zugänglich sein
- **gezielt mit Benutzern geteilt** werden können
- **nicht durch Dritte eingesehen** werden

Später geplant:  
- 📝 Digitale Unterschriften  
- 📤 Interne Freigabe-Workflows  
- 👁️‍🗨️ Revisionssichere Anzeige

---

## 🚀 Installation & Start

1. 📦 Repository klonen:
```bash
git clone https://github.com/Valcoq/DDVS.git
cd DDVS
```

2. 🧪 Virtuelle Umgebung einrichten (empfohlen):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. 📜 Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. 🖥️ Anwendung starten:
```bash
python main.py
```

> ⚠️ Admin-Login: `admin` / `admin`

---

## 📌 Hinweise

- 🔐 Dokumente werden verschlüsselt gespeichert (später geplant)
- 📂 Kein direkter Dateisystem-Zugriff – volle Kontrolle über die GUI
- 📅 Workflows und Benutzerrechte kommen in zukünftigen Versionen

---

## 🧠 Mitmachen & Feedback

Das Projekt befindet sich in der frühen Entwicklung.  
Feedback, Ideen oder Feature-Wünsche? Gerne per GitHub-Issue oder Pull Request!

---

## 📜 Lizenz

MIT License – siehe [LICENSE](LICENSE)

---

> 👨‍💻 *„Wer Ordnung will, braucht Struktur. Wer Sicherheit will, braucht Kontrolle. Wer beides will, braucht DDVS.“ – Valcoq*
