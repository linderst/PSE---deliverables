# Medcode — ICD-10 Diagnosensuche
## Stand (30.03.2026)
Medcode ist eine KI-gestützte Plattform zur Suche und verständlichen Erklärung medizinischer Diagnosen. Patientinnen und Patienten können ICD-10-Codes oder Freitext-Symptome eingeben und erhalten laienverständliche Erklärungen, Facharzt-Empfehlungen und Behandlungshinweise.

## Benutzung (Beispiel)
---

## Technologie-Stack

| Komponente | Technologie | Version |
|-----------|------------|---------|
| Frontend | React + Vite | 19.2 / 7.3.1 |
| Backend | Python + FastAPI | 3.11 |
| Datenbank | PostgreSQL + pgvector | 16 |
| Volltextsuche | Meilisearch | 1.7 |
| KI-Modell | Google Gemini 2.5 Flash | — |
| Embeddings | gemini-embedding-001 (3072 Dim.) | — |
| Containerisierung | Docker Compose | — |
| Datenquelle | BfArM ICD-10-GM 2026 (XML) | — |

---

## Schnellstart

### Voraussetzungen

- **Docker + Docker Compose** (Version 2.0+)
- **Google Gemini API-Key** 

### 1. Umgebungsvariablen einrichten

```bash
cp .env.example .env
```

Öffne `.env` und tragen deinen Gemini API-Key ein:
```
GEMINI_API_KEY=ihr_api_key_hier
```

### 2. Daten importieren (einmalig, ca. 30 Minuten)

```bash
# Importer-Images bauen
docker compose --profile import build

# ICD-10 Daten + Gemini-Embeddings generieren
docker compose --profile import run --rm importer

# Meilisearch-Index befuellen
docker compose --profile import run --rm meili-importer
```

### 3. Anwendung starten

```bash
docker compose up -d --build
```

Die Anwendung ist nun erreichbar:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Meilisearch:** http://localhost:7700

### 4. Anwendung stoppen

```bash
docker compose down
```

---

## Architektur

Das System implementiert eine **RAG-Architektur** (Retrieval-Augmented Generation) mit einem 4-stufigen Suchalgorithmus:

1. **Direct Match** — Regex erkennt ICD-10-Code-Muster (z.B. I10) -> Sofort-Treffer in 1ms
2. **Meilisearch** — Fehlertolerante Volltextsuche für bekannte Begriffe
3. **pgvector** — Semantische Vektorsuche (Cosinus-Ähnlichkeit, 3072 Dimensionen)
4. **Gemini Fallback** — Bei Konfidenz < 75%: LLM extrahiert Fachbegriffe, erneute Suche

Drei parallele KI-Endpunkte generieren unabhängig voneinander Erklärungen:
- `/api/chat/explain` — "Was ist das?"
- `/api/chat/specialist` — "Wer behandelt das?"
- `/api/chat/guidance` — "Wie wird behandelt?"

Detaillierte Architektur-Dokumentation:
- [Architektur & Funktionsweise](docs/architektur_und_funktion.md)
- [Frontend Design-Dokumentation](docs/design/frontend_design.md)

---

## API-Endpunkte

| Methode | Endpoint | Beschreibung |
|---------|---------|-------------|
| GET | `/api/search?q=...&limit=5` | Hybridsuche (Meili + pgvector) |
| GET | `/api/search/refined?q=...&limit=5` | KI-verfeinerte Suche (Gemini) |
| GET | `/api/subcodes?code=...` | ICD-10 Unterkategorien |
| GET | `/api/cached-conditions` | Vorgeseedete Diagnosen für A-Z Index |
| POST | `/api/chat/explain` | KI-Erklärung der Diagnose |
| POST | `/api/chat/specialist` | Facharzt-Empfehlung |
| POST | `/api/chat/guidance` | Behandlungshinweise |
| POST | `/api/chat/contextual` | Kontextuelle Folgefragen |
| GET | `/api/sitemap.xml` | SEO-Sitemap |

---

## Dokumentation
//TODO Backend kommt hier noch rein
| Dokument | Beschreibung |
|---------|-------------|
| [Frontend Design-Dokumentation](docs/design/frontend_design.md) | Komponentendiagramm, Sequenzdiagramme, State-Management, Design Patterns |
| [Backend Design-Dokumentation]() | - |
| [Benutzerhandbuch](docs/benutzerhandbuch.md) | Bedienungsanleitung + Installationsanleitung |
| [Architektur & Funktionsweise](docs/architektur_und_funktion.md) | RAG-Pipeline, Docker-Infrastruktur, Datenfluss |
| [Protokolle](docs/protocols/) | Sitzungsprotokolle (Kunden- und Team-Meetings) |
| [Deliverables](docs/deliverables/) | Statusberichte und Risikoanalysen |

---

## Docker Services

| Service | Image | Port | Beschreibung | Profil |
|---------|-------|------|-------------|--------|
| `db` | pgvector/pgvector:pg16 | 5432 | PostgreSQL + Vektordatenbank | default |
| `backend` | Custom (Python 3.11) | 8000 | FastAPI Server | default |
| `frontend` | Custom (Node 20) | 5173 | React/Vite Dev-Server | default |
| `meilisearch` | getmeili/meilisearch:v1.7 | 7700 | Volltextsuche | default |
| `importer` | Custom (Python 3.11) | — | ICD-10 XML Import + Embedding-Generierung | import |
| `meili-importer` | Custom (Python 3.11) | — | Meilisearch-Indexierung | import |

---

## Team

| Name | Rolle |
|------|-------|
| Felix Buchmüller | Key Account Manager |
| Alexander Bot | Master Tracker |
| Stefan Linder | Chief Deliverable Officer |
| Christian Gafner | Quality Evangelist |
| Dennis Roduner | Sitzungsleitung & Protokollführung |
| Julien Chopin | Sitzungsleitung & Protokollführung |

### Arbeitsplan

[Trello Board](https://trello.com/invite/b/699c50bc8934bc6d26e464a5/ATTI1d9d3acc8e273c0cf821f590b0f7a0626D898DDD/pse)

### Kunde

- **Stefan Vogt** — Geschäftsführer, Medcode GmbH
- **Simon Hölzer** — Arzt, Medcode GmbH
