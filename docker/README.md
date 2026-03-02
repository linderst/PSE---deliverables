# Docker

Dockerfiles und `docker-compose`-Konfigurationen für lokale Entwicklung.

## Voraussetzungen

- Docker Desktop installiert (Mac oder Windows)
- `.env`-Datei im Projektstamm anlegen (Vorlage: `.env.example`)

## Erste Inbetriebnahme

```bash
# 1. Umgebungsvariablen einrichten
cp .env.example .env
# .env mit echten Werten befüllen (Gemini API Key etc.)

# 2. Frontend-Projekt initialisieren (einmalig, falls noch nicht vorhanden)
cd src/frontend
npm create vite@latest . -- --template react
cd ../..

# 3. Alle Services starten
docker compose up -d
```

Danach erreichbar unter:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Datenbank: localhost:5432

## ICD-Daten importieren

Die XML- und TXT-Dateien von BfArM in den `data/`-Ordner legen, dann:

```bash
docker compose --profile import run --rm importer
```

Der Importer lauft einmalig durch und beendet sich. Das Embedding-Modell wird
beim ersten Aufruf heruntergeladen (~500 MB) und danach im `model_cache`-Volume
gecacht.

## Übersicht Services

| Service    | Dockerfile                   | Port | Beschreibung                            |
|------------|------------------------------|------|-----------------------------------------|
| `db`       | `pgvector/pgvector:pg16`     | 5432 | PostgreSQL mit pgvector                 |
| `backend`  | `docker/backend/Dockerfile`  | 8000 | FastAPI, Hot-Reload aktiv               |
| `frontend` | `docker/frontend/Dockerfile` | 5173 | React/Vite Dev Server                   |
| `importer` | `docker/backend/Dockerfile`  | -    | ICD-Import (nur mit `--profile import`) |

## Haufige Befehle

```bash
# Alle Services starten
docker compose up -d

# Logs eines Services anzeigen
docker compose logs -f backend

# Alle Services stoppen
docker compose down

# Datenbank-Volume zurücksetzen (Achtung: alle Daten weg)
docker compose down -v
```
