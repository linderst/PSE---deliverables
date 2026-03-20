# Projektdokumentation: ICD-10 Prompt Engineer Backend & Frontend (V1.0)
**Datum:** 20. März 2026

Dieses Dokument bietet einen detaillierten, technischen Überblick über die fertige Version 1.0 des KI-gestützten Diagnosesystems – basierend auf der offiziellen ICD-10 Datenbasis des BfArM.

---

## 1. Datenbank-Schema & Importer (`database.sql`, `import_icd.py`, `import_meili.py`)
- **Vektor-Dimensionen**: Die Tabelle `icd_embedding` nutzt das Schema `embedding vector(384)`, passgenau für das verwendete Open-Source SentenceTransformer Modell (`paraphrase-multilingual-MiniLM-L12-v2`).
- **Importer-Härtung (`import_icd.py`)**: Das Skript bereinigt Regex und fehlerhafte Anhängsel der BfArM-Kataloge (z.B. `code.rstrip('+*')`). Unbekannte Codes werden intelligent abgefangen, um PostgreSQL-Abstürze bei unvollständigen XML-Knoten zu vermeiden.
- **Meilisearch (`import_meili.py`)**: Ein dedizierter Importer speichert ICD-Codes samt Titeln in der hochperformanten Suchmaschine Meilisearch für schnelle Text-Indizierung.

---

## 2. Backend & KI API (`main.py`)
Das Backend (FastAPI) fungiert als intelligenter Orchestrator zwischen der ICD-10 Datenbank und der **Google Gemini 2.5 Flash** KI:

- **Hybride Suche (`/api/search`)**: Die primäre Suche erfolgt über **Meilisearch** (fehlertolerant & synonymbasiert). Die lokale Vektorsuche (`pgvector` mit Kosinus-Ähnlichkeit) dient als intelligenter Fallback. Direkte ICD-Codes (wie `R51`) werden sofort erkannt.
- **KI-Verfeinerte Suche (`/api/search/refined`)**: Wenn die reguläre Suche unsicher ist (Score < 0.75), extrahiert Gemini aus dem Laien-Text in Echtzeit 5 medizinische Fachbegriffe und wiederholt die Suche in der Datenbank, um die Trefferquote massiv zu erhöhen.
- **Multi-Prompt Architecture**: Die Analyse wird nicht durch einen riesigen Prompt, sondern durch voneinander getrennte Endpunkte generiert:
  1. `/api/chat/explain`: Erklärt die Diagnose laienverständlich.
  2. `/api/chat/specialist`: Nennt den zuständigen Arzt/Spezialisten.
  3. `/api/chat/guidance`: Beschreibt erste Behandlungsschritte.
- **Kontext-Dialog (`/api/chat/contextual`)**: User können Nachfragen zur gefundenen Diagnose stellen; der Chatbot hält den Kontext des spezifischen ICD-Codes streng im Gedächtnis.
- **Subcode-Hierarchie (`/api/subcodes`)**: Optimierte SQL-Abfrage liefert nur direkte Untercodes (z.B. `I10.x`) samt Relevanz (Synonym-Count) ohne tiefe Verschachtelungen.

---

## 3. Frontend & Benutzeroberfläche (React + Vite)
Das Frontend (`App.jsx`, `App.css`) ist eine produktionsreife, reaktive SPA (Single Page Application):

- **Struktur & Design**: Cleanes, responsives Medical-Design, das Suchergebnisse (mit Genauigkeits-Tachometer), BfArM-Unterkategorien und Gemini-Antworten in strukturierte "Cards" aufteilt.
- **Dynamisches Rendering**: Parallele Lade-Zustände (Skeleton-Loader) für die 3 Gemini-Prompts, sodass der User nicht auf die Gesamtanalyse warten muss.
- **Lokalisierung**: Vollständig ins Deutsche übersetztes User-Interface ("Diagnose erstellen", "Symptome eingeben").
- **Privacy & UX (V1.0 Update)**: Die alte Suchhistorie ("Verlauf") in der Sidebar wurde bewusst entfernt, um den Code zu entschlacken und Datenschutzbedenken bei Diagnosesuchen vorzubeugen. Die App startet schlank und fokussiert.
- **Netzwerk**: Fehlerhafte JSON-Payloads (422 Error) wurden korrigiert und Pydantic-konform an das Backend übermittelt. CORS und Vite Config (`host: true`) erlauben reibungslose Zugriffe im lokalen Netzwerk.
