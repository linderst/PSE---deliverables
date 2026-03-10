# Projektdokumentation: ICD-10 Prompt Engineer Backend & Frontend
**Datum:** 10. März 2026

Dieses Dokument fasst alle technischen Anpassungen, Fehlerbehebungen und Implementierungen des heutigen Tages zusammen, die nötig waren, um das KI-gestützte Diagnosesystem auf Basis der offiziellen BfArM ICD-10-Daten bereitzustellen.

---

## 1. Datenbank-Schema & Vector Dimensions (`database.sql`)
- **Fehlerbehebung (Dimension Mismatch)**: Die Tabelle `icd_embedding` wurde ursprünglich mit einer Vektor-Dimension von `768` konzipiert.
- **Lösung**: Da das verwendete Open-Source SentenceTransformer Modell (`paraphrase-multilingual-MiniLM-L12-v2`) jedoch Matrizen mit 384 Dimensionen generiert, wurde das Schema auf `embedding vector(384)` korrigiert, um pgvector-Crashes beim Import zu verhindern.

---

## 2. Daten-Importer (`import_icd.py`)
Das Python-Skript für den Import der offiziellen BfArM XML- und TXT-Kataloge ins Docker-Backend wurde signifikant robuster gestaltet:
- **Foreign Key Violation Fix**: Einige ICD-Codes in der rein alphabetischen TXT-Datei (z.B. `A01.0+` oder Kürzelspezifische Varianten mit Sternchen `*`) besaßen keine exakte Entsprechung in den systematischen XML-Hauptklassen. Dies führte beim Insert der Synonyme zu PostgreSQL Abstürzen.
- **Datenbereinigung**: Das Skript bereinigt nun aktiv die Regex und Anhängsel der Strings mittels `code.rstrip('+*')`.
- **Intelligentes Überspringen**: Unbekannte Synonym-Codes, die vom BfArM alphabetisch geführt, aber vom XML-Parser nicht geladen wurden, werden nun intelligent gefiltert (`valid_codes` Set-Abgleich). Fehlerhafte TXT-Zeilen stören so den mehrstündigen Importprozess nicht länger.

---

## 3. Backend & KI API (`main.py`)
Die komplette FastAPI-Struktur des Backends wurde geschrieben:
- **CORS-Middleware**: Native Freigabe konfiguriert, damit das separate React-Frontend im Browser auf Port `8000` via localhost kommunizieren darf.
- **Vektorsuche (Cosimus-Ähnlichkeit)**: Eine hochperformante PostgreSQL Abfrage implementiert (`ORDER BY e.embedding <=> %s::vector LIMIT 5;`), die den Text-Input des Arztes als dynamischen Vektor gegen die tausenden ICD-10 BfArM-Vektoren abgleicht.
- **Prompt Engineering Pipeline**:
  1. Der freie Text des Users wird eingebettet.
  2. Die 5 besten Treffer aus der DB werden evaluiert.
  3. Diese Treffer (ICD Code + Diagnosename + Mathematische Übereinstimmung) werden zusammen mit dem initialen User-Input und einer expliziten System-Anweisung zu einem intelligenten Kontext-Prompt konkateniert.
  4. Der Prompt wird live an das **Google Gemini 2.5 Flash** Modell gesendet.
- Neben dem reinen `/api/diagnose` LLM Endpunkt wurde auch ein technischer `/api/search` Endpunkt gebaut, der nur die rohen lokalen Vektoren zurückgibt, um die Qualität der Embeddings isoliert testen zu können.

---

## 4. Frontend & Benutzeroberfläche (React + Vite)
Das rudimentäre Vite "Counter"-Template aus der Docker-Installation wurde durch eine moderne, fertige Medizin-App ausgetauscht.
- **Vite Config (`vite.config.js`)**: Die Dev-Server Bindung wurde explizit auf `server: { host: true }` gestellt, damit sie ausserhalb von isolierten Docker-Containern im Hostnetzwerk (Mac) erreichbar wird.
- **App-Logik (`App.jsx`)**: 
  - Eine saubere, asynchrone React-Komponente mit Loading-States, Fehler-Behandlung und Fetch-Requests gegen das FastAPI Backend (`/api/diagnose`).
  - Besonderer Fokus auf die Lösung des 422 (Unprocessable Entity) Payload-Typisierungsfehlers, sodass saubere JSONs gemäss Pydantic Schema übermittelt werden.
  - Behebung von Crashes bei Array-Mappings der LLM Responses (Zuweisung `result.sources`).
- **Styling (`App.css` & `index.css`)**: Implementierung eines responsiven, cleanen Designs, das offizielle BfArM-Quellen und Gemini's AI-Antwort übersichtlich in strukturierten Cards aufbereitet.
