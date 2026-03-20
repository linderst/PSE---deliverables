# ICD-10 AI Prompt Engineer – Test Anleitung

Diese Anleitung beschreibt detailliert, wie du das Projekt lokal über das Terminal (ohne Docker Desktop UI-Klicks) startest und testest. Die Befehle sind für macOS und Windows aufbereitet.

## 1. Voraussetzungen
- **Docker & Docker Compose** müssen installiert sein und im Hintergrund laufen (z.B. durch das Öffnen der Docker Desktop App).
- Ein **Google Gemini API Key**.
- **Node.js** (v20+) für das Frontend.

---

## 2. Einrichtung (Einmalig)

### 2.1 `.env` Datei erstellen

**🍏 macOS / Linux (Terminal):**
1. Öffne das Terminal (`Cmd + Leertaste`, "Terminal" eingeben).
2. Navigiere in den Projektordner (z.B. `cd CodeProjects/PSE/PSE---deliverables`).
3. Kopiere die Environment-Datei und bearbeite sie:
```bash
cp .env.example .env
nano .env
```
*(Trage bei `GEMINI_API_KEY` deinen Key ein. Speichere mit `Ctrl+O`, bestätige mit `Enter`, und schließe mit `Ctrl+X`)*

**🪟 Windows (PowerShell):**
1. Öffne die PowerShell (`Windows-Taste`, "PowerShell" eingeben).
2. Navigiere in den Projektordner (z.B. `cd C:\CodeProjects\PSE\PSE---deliverables`).
3. Kopiere die Environment-Datei und bearbeite sie:
```powershell
Copy-Item .env.example -Destination .env
notepad .env
```
*(Trage in der sich öffnenden Datei bei `GEMINI_API_KEY` deinen Key ein und speichere die Datei)*

---

### 2.2 Datenbank & Vektor/Meilisearch Import starten
Das Projekt benötigt die BfArM ICD-10 Daten in der lokalen PostgreSQL-Vektordatenbank sowie im Meilisearch-Suchindex. Die Befehle sind für **macOS und Windows (PowerShell)** identisch:

Führe in deinem Terminal / PowerShell auf der Ebene der `docker-compose.yml` aus:
```bash
# 1. Image für den Importer bauen
docker compose --profile import build

# 2. PGVector Embeddings generieren (Dauert ca. 30 Minuten!)
docker compose --profile import run --rm importer

# 3. Meilisearch Index befüllen (Dauert wenige Sekunden bis Minuten)
docker compose --profile import run --rm meili-importer
```

---

## 3. App starten

Sobald der Import erfolgreich war, starte die gesamte Umgebung (Datenbank, Backend für API und Frontend) im Hintergrund. Auch hier ist der Befehl systemübergreifend:

```bash
docker compose up -d --build
```
*(Das Frontend läuft automatisch auf `http://localhost:5173`, das Backend und Meilisearch laufen im Hintergrund mit)*

---

## 4. Testen
Gehe in deinem Browser auf **http://localhost:5173**.

1. Tippe freitextliche Symptome in das Textfeld (z.B. *"pulsierende Kopfschmerzen, Übelkeit und Lichtempfindlichkeit"*).
2. Klicke auf **Diagnose erstellen**.
3. Du erhältst eine Diagnose-Empfehlung von der Gemini KI. Weiter unten wird detailliert aufgeschlüsselt, welche Top-Matches aus der offiziellen BfArM Datenbasis als Ground Truth / System-Prompt an das LLM geschickt wurden.

### Container beenden
Wenn du das Projekt nicht mehr benötigst und stoppen möchtest, führe im Projektordner aus:
```bash
docker compose down
```
