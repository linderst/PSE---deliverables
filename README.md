# Medcode — ICD-10 Diagnosensuche & AI Prompt Engineer

![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-pgvector-4169E1?style=flat&logo=postgresql&logoColor=white)
![Meilisearch](https://img.shields.io/badge/Meilisearch-1.7-FF5757?style=flat&logo=meilisearch&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?style=flat&logo=googlegemini&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)

> **Stand:** April 2026

Medcode ist eine moderne, KI-gestützte Plattform zur Suche und verständlichen Erklärung medizinischer Diagnosen. Patientinnen und Patienten können ICD-10-Codes oder umgangssprachliche Symptome eingeben und erhalten extrem schnell präzise, laienverständliche Erklärungen, Facharzt-Empfehlungen und generelle Behandlungshinweise. 

Das System basiert auf einer fortschrittlichen **Retrieval-Augmented Generation (RAG)** Architektur, um sogenannte "KI-Halluzinationen" im medizinischen Bereich strikt zu vermeiden.

---

## ✨ Kern-Features

- **Zweiphasige Hybridsuche:** Kombiniert blitzschnelle, typotolerante Volltextsuche (Meilisearch) mit semantischer Vektorsuche (pgvector) und einer Gemini-basierten Query-Verfeinerung für hochkomplexe Symptombeschreibungen.
- **Umgangssprachen-Mapping:** Übersetzt Alltagsbegriffe (z.B. "Herzrasen" oder "Bluthochdruck") automatisch in den korrekten medizinischen Fachjargon, noch bevor gesucht wird.
- **AI-Caching System:** Die Erklärungen für die häufigsten Krankheiten werden in einer eigenen Cache-Tabelle vorgehalten — das eliminiert LLM-Latenzen (0 ms statt 3-5s) und minimiert API-Kosten auf null für Standard-Diagnosen.
- **Kontextueller Chat:** Das System bietet pro Diagnose einen dedizierten Chatbot für Folgefragen an (`"Ist das ansteckend?"`, `"Darf ich Sport machen?"`), der stets im Kontext der jeweiligen Krankheit antwortet.
- **SEO & Sichtbarkeit:** Vollständige SEO-Struktur mit dynamischer `sitemap.xml`, statischen A-Z-Indizes auf der Startseite und suchmaschinenoptimierten, sprechenden URLs (z.B. `/diabetes-mellitus-typ-2/E11`).

---

## 🛠️ Technologie-Stack

| Komponente | Technologie | Version |
|-----------|------------|---------|
| **Frontend** | React + Vite | 19.2 / 7.3.1 |
| **Backend API** | Python + FastAPI | 3.11 |
| **Datenbank / Cache** | PostgreSQL + pgvector | 16 |
| **Volltextsuche** | Meilisearch | 1.7 |
| **KI-Modell (LLM)** | Google Gemini 2.5 Flash | — |
| **Embedding-Modell** | gemini-embedding-001 (3072 Dim.) | — |
| **Containerisierung** | Docker Compose | — |
| **Datenquelle** | BfArM ICD-10-GM 2026 (XML) | — |

---

## 🚀 Schnellstart

### Voraussetzungen
- **Docker + Docker Compose** (Version 2.0+)
- **Google Gemini API-Key** (kostenlos unter Google AI Studio erhältlich)

### 1. Konfiguration einrichten
Kopiere die Beispiel-Konfiguration:
```bash
cp .env.example .env
```
Öffne die `.env`-Datei und trage deinen gültigen Gemini API-Key ein:
```env
GEMINI_API_KEY=dein_api_key_hier
```

### 2. Daten importieren (Einmalig)
Der Import lädt den ICD-Katalog herunter, generiert Vektor-Embeddings und indiziert Meilisearch. *Dieser Vorgang dauert aufgrund der Embedding-Generierung initial ca. 20-30 Minuten.*
```bash
# Importer-Images bauen
docker compose --profile import build

# ICD-10 Daten (PostgreSQL) + Gemini-Embeddings generieren
docker compose --profile import run --rm importer

# Meilisearch-Index aufbauen
docker compose --profile import run --rm meili-importer
```

### 3. Applikation starten
Nach erfolgreichem Import kann das Gesamtsystem hochgefahren werden:
```bash
docker compose up -d --build
```

**Verfügbare Dienste:**
- 🌐 **Frontend (Benutzeroberfläche):** http://localhost:5173
- ⚙️ **Backend (API):** http://localhost:8000
- 🔍 **Meilisearch Dashboard:** http://localhost:7700

Zum Stoppen der Container: `docker compose down`

---

## 🧠 Architektur & Routing

Das System verarbeitet Benutzeranfragen in einer performanten, mehrstufigen Pipeline. Keine Geschäftslogik befindet sich in den FastAPI-Routern — alles ist sauber in Singleton-Services gekapselt.

1. **Direct Match** (`DatabaseService`) — Ein regulärer Ausdruck erkennt ICD-10-Code-Muster (z.B. "I10"). Sofort-Treffer in < 1ms.
2. **Meilisearch** (`SearchService`) — Fehlertolerante Volltextsuche, gekoppelt mit einem Subcode-Penalty, um Parent-Kategorien korrekt zu priorisieren.
3. **pgvector Fallback** (`DatabaseService`) — Semantische Vektorsuche für abweichende Formulierungen mittels Cosinus-Ähnlichkeit.
4. **Gemini Fallback / Refinement** (`SearchService`/`ChatService`) — Liefert die erste schnelle Suche keine starke Übereinstimmung (Konfidenz < 75%), extrahiert ein LLM asynchron Fachbegriffe aus dem Symptom und sucht erneut.

Informationen werden primär aus dem AI-Cache bedient und mit SEO-freundlichen URLs (`/:slug/:code`) im Frontend präsentiert.

---

## 📑 Dokumentation

| Dokument | Beschreibung |
|---------|-------------|
| 📐 **[Klassendiagramm & Funktionsweise](docs/klassendiagramm_und_funktionsweise.md)** | **Hauptrereferenz:** Umfassendes Systemdesign, Mermaid-Klassendiagramme, Flowcharts, API-Abläufe und Modul-Erklärungen. | 
| 🎨 **[Frontend Design](docs/design/frontend_design.md)** | UI-Komponentendiagramm, Design Patterns und React State-Management. |
| 📖 **[Benutzerhandbuch](docs/benutzerhandbuch.md)** | Bedienungs- und technische Installationsanleitung der Applikation. |
| 🕰️ **[Ältere Architektur](docs/architektur_und_funktion.md)** | Ursprünglicher Entwurf der RAG-Pipeline und Docker-Infrastruktur. |
| 📝 **[Protokolle](docs/protocols/)** | Sitzungsprotokolle (Kunden- und Team-Meetings). |
| 📊 **[Deliverables](docs/deliverables/)** | Risikoanalysen, Testkonzepte und Statusberichte. |

---

## 🔌 API-Endpunkte

| Methode | Endpoint | Beschreibung |
|---------|---------|-------------|
| `GET` | `/api/search?q=...&limit=5` | Initiale Hybridsuche (Direct + Meili + pgvector) |
| `GET` | `/api/search/refined?q=...` | KI-verfeinerte Symptomsuche (Gemini Extrahierung) |
| `GET` | `/api/subcodes?code=...` | Lädt hierarchisch alle ICD-10 Unterkategorien |
| `GET` | `/api/cached-conditions` | Holt vorgeseedete Krankheiten für den SEO A-Z Index |
| `POST` | `/api/chat/explain` | KI-Erklärung der Diagnose (Laienverständlich) |
| `POST` | `/api/chat/specialist` | Welcher Facharzt ist hierfür zuständig? |
| `POST` | `/api/chat/guidance` | Gängige Behandlungshinweise |
| `POST` | `/api/chat/contextual` | Individueller Kontext-Chat (Folgefragen-Dialog) |
| `GET` | `/sitemap.xml` | Dynamisch generierte SEO-Sitemap |

---

## 🐳 Docker Services

| Service | Basis-Image | Container-Port | Beschreibung | Profil |
|---------|-------|------|-------------|--------|
| `db` | `pgvector/pgvector:pg16` | 5432 | Relationale PostgreSQL inkl. Vektordatenbank | default |
| `meilisearch` | `getmeili/meilisearch:v1.7` | 7700 | In-Memory Volltext-Engine mit Typokorrektur | default |
| `backend` | `python:3.11-slim` | 8000 | FastAPI Python Server | default |
| `frontend` | `node:20` | 5173 | React/Vite Application | default |
| `importer` | `python:3.11-slim` | — | Einmaliges ICD-10 Parsing & Gemini-Embedding | import |
| `meili-importer` | `python:3.11-slim` | — | Einmaliges Meilisearch-Indexing der DB-Synonyme | import |

---

## 👥 Projekt-Team & Stakeholder

**Projektteam:**
| Name | Rolle |
|------|-------|
| Felix Buchmüller | Key Account Manager |
| Alexander Bot | Master Tracker |
| Stefan Linder | Chief Deliverable Officer |
| Christian Gafner | Quality Evangelist |
| Dennis Roduner | Sitzungsleitung & Protokollführung |
| Julien Chopin | Sitzungsleitung & Protokollführung |

**Kunde (Medcode GmbH):**
- **Stefan Vogt** — Geschäftsführer
- **Simon Hölzer** — Leitender Arzt

🔗 [Projekt Trello Board (Intern)](https://trello.com/invite/b/699c50bc8934bc6d26e464a5/ATTI1d9d3acc8e273c0cf821f590b0f7a0626D898DDD/pse)
