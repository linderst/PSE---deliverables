# Projektdokumentation: ICD-10 Prompt Engineer Backend & Frontend
**Datum:** 20. März 2026 (aktualisiert: 30. März 2026)

//TODO noch Backend einfügen
> **Hinweis:** Für die aktuelle Design-Dokumentation siehe [Frontend Design-Dokumentation](docs/design/frontend_design.md) und das [Benutzerhandbuch](docs/benutzerhandbuch.md).

Dieses Dokument bietet einen detaillierten, technischen Überblick über die Version 1.0 des KI-gestützten Diagnosesystems.
---

## 1. Datenbank-Schema & Importer (`database.sql`, `import_icd.py`, `import_meili.py`)
- **Vektor-Dimensionen**: Die Tabelle `icd_embedding` nutzt das Schema `embedding vector(3072)`, passgenau für die Google Gemini Embedding API (`gemini-embedding-001`).
- **Importer-Härtung (`import_icd.py`)**: Das Skript bereinigt Regex und fehlerhafte Anhängsel der BfArM-Kataloge (z.B. `code.rstrip('+*')`). Unbekannte Codes werden intelligent abgefangen, um PostgreSQL-Abstürze bei unvollständigen XML-Knoten zu vermeiden.
- **Meilisearch (`import_meili.py`)**: Ein dedizierter Importer speichert ICD-Codes samt Titeln in der hochperformanten Suchmaschine Meilisearch für schnelle Text-Indizierung.

---

## 2. Backend & KI API (`main.py`)
Das Backend (FastAPI) fungiert als intelligenter Orchestrator zwischen der ICD-10 Datenbank und der **Google Gemini 2.5 Flash** KI:

- **Der 4-stufige Diagnose-Suchalgorithmus (Backend-Kaskade)**: Die Suche verwendet eine hochperformante Fallback-Kette, um Latenz und KI-Kosten minimal zu halten:
  1. **Direct Match Lookup (Regex)**: Zeigt die Eingabe das Muster eines ICD-Codes (z. B. `I10`), wird dieser sofort in 1ms als Exact Match aus der Datenbank abgefragt ("Zero-Click Search").
  2. **Meilisearch (Text)**: Bei Text-Eingaben wird zuerst die Meilisearch Suchmaschine konsultiert. Sie ist fehlertolerant und rasend schnell, deckt aber nur bekannte Wortüberschneidungen ab.
  3. **PGVector (Semantik)**: Findet Meilisearch keine exakten Wörter, greift die lokale Vektordatenbank ein. Ein KI-Modell (`paraphrase-multilingual-MiniLM-L12-v2`) versteht die *inhaltliche Bedeutung* der Symptome (Raumdistanz). Zusätzlich sorgt ein intelligentes Custom-Clustering in SQL (`0.6 * MAX + 0.4 * AVG`) dafür, dass jene Kategorien gewinnen, deren Untercodes alle gut zum Suchbegriff passen.
  4. **LLM-Refinement (Gemini Fallback)**: Ist die Zuversicht des besten Treffers < 75%, geht das System in einen animierten Ladescreen über. Google Gemini analysiert den Text wie ein echter Arzt und extrahiert exakt 5 hochspezifische lateinisch-medizinische Fachbegriffe. Diese Begriffe werden als "Boost" nochmals gegen Meilisearch (und bei Misserfolg PGVector) geworfen, was extrem akkurate Treffer selbst bei langem Laien-Storytelling erzeugt.
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
