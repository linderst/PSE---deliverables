# ICD-10 AI Prompt Engineer – Test Anleitung

Diese Anleitung beschreibt, wie du das Projekt lokal startest und das Prompt-Engineering Interface testest.

## 1. Voraussetzungen
- **Docker & Docker Compose** müssen installiert sein und laufen.
- Ein **Google Gemini API Key** wird benötigt.
- **Node.js** (v20+) für das Frontend.

---

## 2. Einrichtung (Einmalig)

### 2.1 Umgebungsvariablen definieren
1. Kopiere die Datei `.env.example` und benenne sie in `.env` um.
2. Öffne die `.env` Datei und trage deinen gültigen Google Gemini API Key bei `GEMINI_API_KEY` ein.

### 2.2 Datenbank & Import starten
Das Projekt benötigt die hochgeladenen BfArM ICD-10 Daten in der lokalen PostgreSQL-Vektordatenbank.

Führe im Hauptverzeichnis des Projekts aus:
```bash
docker compose --profile import build importer
docker compose --profile import run --rm importer
```
*Hinweis: Der Import kann ca. 30 Minuten dauern, da über 100.000 vektorielle Text-Embeddings durch das PyTorch-Modell lokal berechnet werden.*

---

## 3. App starten

Sobald der Import erfolgreich war (oder wenn die Datenbank bereits befüllt ist), starte die gesamte Umgebung (Datenbank, Backend und Frontend) im Hintergrund:
```bash
docker compose up -d
```

---

## 4. Testen
Gehe in deinem Browser auf **http://localhost:5173**.

1. Tippe freitextliche Symptome in das Textfeld (z.B. *"pulsierende Kopfschmerzen, Übelkeit und Lichtempfindlichkeit"*).
2. Klicke auf **Generate Diagnosis**.
3. Du erhältst eine Diagnose-Empfehlung von der Gemini KI und siehst weiter unten genau, welche Top-Vektor-Matches aus den offiziellen BfArM Datenbasis als Ground Truth / System-Prompt an die LLM geschickt wurden.

```bash
# Um alle Docker Container am Ende wieder zu stoppen:
docker compose down
```
