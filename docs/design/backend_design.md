# Medcode — Backend-Architekturdokumentation

**Projekt:** Medcode — ICD-10 Diagnosensuche  
**Backend-Framework:** Python 3.11 + FastAPI  
**Datenbank:** PostgreSQL 16 + pgvector  
**Suchmaschine:** Meilisearch 1.7  
**KI-Modell:** Google Gemini 2.5 Flash  
**Containerisierung:** Docker Compose  
**Datenquelle:** BfArM ICD-10-GM 2026 (XML)  

---

## Inhaltsverzeichnis

1. [Systemübersicht](#1-systemübersicht)
2. [Backend-Architektur](#2-backend-architektur)
3. [Datenmodelle](#3-datenmodelle-pydantic)
4. [Service-Schicht](#4-service-schicht)
5. [API-Endpunkte](#5-api-endpunkte)
6. [Datenbankschema](#6-datenbankschema)
7. [Konfiguration und Umgebungsvariablen](#7-konfiguration-und-umgebungsvariablen)
8. [Import- und Wartungsskripte](#8-import--und-wartungsskripte)
9. [Schnellreferenz](#9-schnellreferenz)

---

## 1. Systemübersicht

Medcode ist eine moderne, KI-gestützte Plattform zur Suche und Erklärung medizinischer Diagnosen in verständlicher Sprache. Patienten können ICD-10-Codes oder umgangssprachliche Symptome eingeben und erhalten schnelle, laienverständliche Erklärungen, Facharztempfehlungen sowie allgemeine Behandlungshinweise.

Das System basiert auf einer fortschrittlichen Retrieval-Augmented-Generation-Architektur (RAG), die KI-Halluzinationen im medizinischen Bereich zuverlässig verhindert.

### 1.1 Technologie-Stack

| Komponente | Technologie | Version |
|---|---|---|
| Backend-API | Python + FastAPI | 3.11 |
| Datenbank / Cache | PostgreSQL + pgvector | 16 |
| Volltextsuche | Meilisearch | 1.7 |
| KI-Modell (LLM) | Google Gemini 2.5 Flash | — |
| Embedding-Modell | gemini-embedding-001 | 3072 Dim. |
| Containerisierung | Docker Compose | 2.0+ |
| Datenquelle | BfArM ICD-10-GM 2026 (XML) | — |

### 1.2 Kernfunktionen

- **Zweiphasige Hybridsuche:** Kombiniert schnelle, tippfehlertolerante Volltextsuche (Meilisearch) mit semantischer Vektorsuche (pgvector) und Gemini-basierter Anfrageverfeinerung für komplexe Symptombeschreibungen.
- **Umgangssprachen-Mapping:** Übersetzt automatisch Alltagsbegriffe (z.B. «Herzrasen») in korrekte medizinische Fachbegriffe vor der Suche.
- **KI-Caching-System:** Erklärungen für die häufigsten Krankheiten sind in einer dedizierten Cache-Tabelle vorgespeichert — dadurch entfällt die LLM-Latenz (0 ms statt 3–5 s) und API-Kosten werden minimiert.
- **Kontextueller Chat:** Pro Diagnose steht ein dedizierter Chatbot für Rückfragen bereit, der stets im Kontext der jeweiligen Erkrankung antwortet.
- **SEO und Sichtbarkeit:** Vollständige SEO-Struktur mit dynamischer `sitemap.xml`, statischen A-Z-Indizes und suchmaschinenoptimierten URLs (z.B. `/diabetes-mellitus-typ-2/E11`).

### 1.3 Dreischichtige Architektur

1. **Frontend → Backend:** Die React-SPA ruft FastAPI-Endpunkte via `fetch()` auf. Die API-Basis-URL wird über `VITE_API_BASE_URL` konfiguriert.
2. **Backend → PostgreSQL:** Der `DatabaseService` verwaltet einen Verbindungspool (`psycopg2.pool.SimpleConnectionPool`, 1–20 Verbindungen).
3. **Backend → Meilisearch:** Der `SearchService` nutzt den Meilisearch-Python-Client für schnelle, tippfehlertolerante Suchen.
4. **Backend → Gemini-API:** `ChatService` (LLM-Antworten) und `SearchService` (Embeddings) kommunizieren über den Google-`genai`-Client.

> **Designprinzip:** Keine Geschäftslogik in den FastAPI-Routern. Alles ist sauber in Singleton-Services gekapselt.

---

## 2. Backend-Architektur

### 2.1 Projektstruktur

| Pfad | Beschreibung |
|---|---|
| `src/backend/main.py` | FastAPI-Einstiegspunkt, Lifespan, CORS, Root-Route |
| `src/backend/config.py` | Zentrale Konfiguration — lädt `.env`, initialisiert Gemini und Meilisearch |
| `src/backend/dependencies.py` | Singleton-Verdrahtung — erstellt und stellt die drei Service-Instanzen bereit |
| `src/backend/models/` | Pydantic-Request/Response-Modelle (`SearchResult`, `ChatRequest`, etc.) |
| `src/backend/services/db_service.py` | `DatabaseService` — alle PostgreSQL-Zugriffe über Verbindungspool |
| `src/backend/services/chat_service.py` | `ChatService` — Gemini-LLM-Aufrufe und Caching-Logik |
| `src/backend/services/search_service.py` | `SearchService` — 4-stufige Hybrid-Such-Pipeline |
| `src/backend/routers/search.py` | `GET /api/search` und `/api/search/refined` |
| `src/backend/routers/chat.py` | `POST /api/chat/*` (explain, specialist, guidance, contextual) |
| `src/backend/routers/subcodes.py` | `GET /api/subcodes` |
| `src/backend/routers/seo_cache.py` | `GET /api/cached-conditions` und `/sitemap.xml` |
| `src/backend/medical_synonyms.py` | `COLLOQUIAL_EXPANSION`-Dict und `expand_query()`-Hilfsfunktion |
| `src/backend/import_icd.py` | Einmaliger ICD-10-Import, Embedding-Generierung, DB-Schema-Erstellung |
| `src/backend/import_meili.py` | Einmaliger Meilisearch-Index-Aufbau |
| `src/backend/seed_cache.py` | KI-Cache-Vorwärmer für die Top-100-ICD-Codes |

### 2.2 Dependency-Injection-Graph

Services werden einmalig beim Anwendungsstart erstellt (Singleton-Muster) und via FastAPIs `Depends()` injiziert:

```
Config (genai_client, meili_index)
    │
    ▼
DatabaseService()
    │
    ▼
ChatService(db_service, genai_client)
    │
    ▼
SearchService(db_service, chat_service, genai_client, meili_index)
```

### 2.3 Docker-Services

| Service | Basis-Image | Port | Beschreibung | Profil |
|---|---|---|---|---|
| `db` | `pgvector/pgvector:pg16` | 5432 | PostgreSQL + Vektoren-Erweiterung | standard |
| `meilisearch` | `getmeili/meilisearch:v1.7` | 7700 | Volltextsuchmaschine mit Tippfehlerkorrektur | standard |
| `backend` | `python:3.11-slim` | 8000 | FastAPI Python-Server | standard |
| `frontend` | `node:20` | 5173 | React/Vite-Anwendung | standard |
| `importer` | `python:3.11-slim` | — | Einmaliger ICD-10-Parser und Gemini-Embedding | import |
| `meili-importer` | `python:3.11-slim` | — | Einmaliger Meilisearch-Index-Aufbau | import |

---

## 3. Datenmodelle (Pydantic)

Pydantic-Modelle definieren das Schema für alle API-Anfragen und -Antworten. FastAPI nutzt sie automatisch für Validierung, Serialisierung und OpenAPI-Dokumentation.

### 3.1 Modellübersicht

| Modell | Richtung | Felder | Verwendet von |
|---|---|---|---|
| `SearchResult` | Antwort | `code`, `title`, `score` (float, Standard 0.0), `version` (Standard `'2024'`) | SearchRouter |
| `SearchResponse` | Antwort | `results: List[SearchResult]` | SearchRouter |
| `ChatRequest` | Anfrage | `question: str` | ChatRouter — explain, specialist, guidance |
| `ContextualChatRequest` | Anfrage | `question`, `condition_code`, `condition_title` | ChatRouter — contextual |
| `ChatResponse` | Antwort | `answer: str`, `disclaimer: bool` (Standard `False`) | ChatRouter |
| `SubcodeResult` | Antwort | `code`, `title`, `synonym_count` (int), `is_leaf` (Optional[bool]) | SubcodesRouter |
| `SubcodeResponse` | Antwort | `parent_code`, `parent_title`, `subcodes: List[SubcodeResult]` | SubcodesRouter |

> **Hinweis:** `ContextualChatRequest` erweitert `ChatRequest` logisch (fügt `condition_code` und `condition_title` hinzu), ist aber eine eigenständige Klasse ohne Python-Vererbung.

---

## 4. Service-Schicht

Die Service-Schicht enthält die gesamte Geschäftslogik. Kein FastAPI-Routing-Code befindet sich hier — diese Trennung ist bewusst und gewährleistet Testbarkeit und Wartbarkeit.

### 4.1 DatabaseService (`db_service.py`)

Verwaltet alle PostgreSQL-Interaktionen über einen Verbindungspool.

**Wichtige Design-Entscheidungen:**
- **Lazy Pool-Initialisierung:** Der Verbindungspool wird beim ersten Datenbankzugriff erstellt (`_ensure_pool()`). Damit werden Docker-Startprobleme vermieden, wenn der Backend-Container vor der Datenbank startet.
- **Context-Manager-Muster:** `get_connection()` ist ein `@contextmanager`, der automatisch Verbindungen aus dem Pool holt und nach Verwendung zurückgibt.

**Öffentliche Methoden:**

| Methode | Parameter | Rückgabe | Beschreibung |
|---|---|---|---|
| `get_connection()` | — | `ContextManager[Connection]` | Thread-sichere Verbindung aus dem Pool |
| `get_icd_code_direct(code)` | `code: str` | `tuple \| None` | Exakte Suche eines 3-stelligen ICD-Codes (<1ms) |
| `run_vector_search_query(embedding, limit)` | `embedding: list[float]`, `limit: int` | `list` | pgvector Kosinus-Ähnlichkeitssuche (0.6×MAX + 0.4×AVG) |
| `get_subcodes_from_db(code)` | `code: str` | `tuple` | Elterntitel und alle 4+-stelligen Subcodes |
| `get_cached_chat(code, prompt_type)` | `code: str`, `prompt_type: str` | `str \| None` | Gibt gecachte Gemini-Antwort zurück oder `None` |
| `save_cached_chat(code, prompt_type, ans)` | `code`, `prompt_type`, `ans: str` | `void` | Speichert Gemini-Antwort; überspringt Fehler-Strings |
| `get_cached_conditions_from_db()` | — | `list` | Alle ICD-Codes mit gecachten KI-Antworten |
| `get_sitemap_codes()` | — | `list` | Alle gecachten Codes für Sitemap-Generierung |
| `close()` | — | `void` | Schliesst den Verbindungspool beim Herunterfahren |

### 4.2 ChatService (`chat_service.py`)

Verwaltet alle Interaktionen mit dem Google Gemini LLM und das zweistufige Antwort-Cache-System.

| Methode | Parameter | Rückgabe | Beschreibung |
|---|---|---|---|
| `ask_gemini(prompt)` | `prompt: str` | `str` | Sendet Prompt an `gemini-2.5-flash`; gibt Text oder Fehler-String zurück |
| `handle_cached_chat(req, prompt_type, template, disclaimer)` | `req`, `prompt_type`, `template`, `disclaimer` | `ChatResponse` | Cache-first: prüft DB, bei Treffer sofortige Antwort; bei Fehlen Gemini aufrufen, speichern, zurückgeben |

**Cache-Ablauf:**
1. ICD-Code aus der Frage extrahieren (z.B. `'I10: Essentielle Hypertonie'` → `'I10'`)
2. `icd_ai_cache`-Tabelle auf `(code, prompt_type)` prüfen
3. **Cache-Treffer:** Gespeicherte Antwort sofort zurückgeben — null API-Kosten, null Latenz
4. **Cache-Fehltreffer:** Gemini aufrufen, Ergebnis in DB speichern, zurückgeben

> **Hinweis zu Rate-Limits:** Das Gemini Free-Tier erlaubt 15 Anfragen/Minute. Der Cache macht Folgeanfragen zur gleichen Diagnose sofort und kostenlos.

### 4.3 SearchService (`search_service.py`)

Orchestriert die vierstufige Hybrid-Such-Pipeline, kombiniert mehrere Suchstrategien für maximale Genauigkeit bei minimaler Latenz.

**4-stufige Such-Kaskade (`perform_search`):**

| Stufe | Methode | Schwellenwert | Latenz | Beschreibung |
|---|---|---|---|---|
| 1. Direkter Code-Treffer | Regex + DB-Abfrage | Exakter Treffer | <1ms | Erkennt ICD-Code-Muster (z.B. `'I10'`); umgeht alle Suchmaschinen |
| 2. Meilisearch | Volltextsuche | Score ≥ 0.75 | 5–20ms | Tippfehlertolerant, synonymbewusst. Subcodes 15% abgewertet |
| 3. pgvector-Fallback | Kosinus-Ähnlichkeit | raw_sim ≥ 0.73 | 50–150ms | Semantische Suche via Gemini-Embeddings, Query per MedicalSynonyms erweitert |
| 4. Gemini-Verfeinerung | LLM + Meilisearch/pgvector | Score < 0.75 | 1–3s | Gemini extrahiert 5 medizinische Begriffe aus natürlicher Sprache |

**Meilisearch-Deduplizierungslogik:**

Da Meilisearch sowohl 3-stellige Eltern-Codes als auch 4+-stellige Subcodes indexiert:
- Alle Ergebnisse werden nach den ersten 3 Zeichen gruppiert
- Subcodes erhalten eine 15%-Score-Strafe (`score × 0.85`)
- Pro 3-stelliger Gruppe wird nur der höchste Eintrag behalten

> **Beispiel:** Ohne Strafe könnte `O24.1 Diabetes in der Schwangerschaft` (Subcode) fälschlicherweise über `E11 Diabetes mellitus Typ 2` (Elterncode) ranken.

---

## 5. API-Endpunkte

Das Backend stellt eine RESTful-API auf Port 8000 bereit. Alle Router delegieren sofort an die Service-Schicht — Router enthalten keine Geschäftslogik.

### 5.1 Vollständige Endpunkt-Referenz

| Methode | Endpunkt | Anfrage | Antwort | Beschreibung |
|---|---|---|---|---|
| `GET` | `/` | — | `{status: ok}` | Gesundheitsprüfung |
| `GET` | `/api/search` | `q` (str), `limit` (int, Standard 5) | `SearchResponse` | 3-stufige Hybridsuche: Code → Meilisearch → pgvector |
| `GET` | `/api/search/refined` | `q` (str), `limit` (int, Standard 5) | `SearchResponse` | Gemini-erweiterte Suche für komplexe Symptombeschreibungen |
| `POST` | `/api/chat/explain` | `ChatRequest` | `ChatResponse` | Laienverständliche Diagnoseerklärung |
| `POST` | `/api/chat/specialist` | `ChatRequest` | `ChatResponse` | Welcher Facharzt ist zuständig? |
| `POST` | `/api/chat/guidance` | `ChatRequest` | `ChatResponse` | Gängige Behandlungsansätze |
| `POST` | `/api/chat/contextual` | `ContextualChatRequest` | `ChatResponse` | Rückfrage im Kontext einer bestimmten Diagnose |
| `GET` | `/api/subcodes` | `code` (str) | `SubcodeResponse` | Alle 4-stelligen Subcodes für einen 3-stelligen ICD-Code |
| `GET` | `/api/cached-conditions` | — | `{conditions: [...]}` | Alle Codes mit gecachten KI-Antworten (A-Z-Index) |
| `GET` | `/sitemap.xml` | — | XML | Dynamisch generierte Sitemap aller gecachten Krankheitsseiten |

### 5.2 Chat-Endpunkte im Detail

| Endpunkt | Gecacht? | Modell | Verhalten |
|---|---|---|---|
| `/api/chat/explain` | JA | `ChatRequest` | Erklärt Diagnose in einfachem Deutsch für Patienten |
| `/api/chat/specialist` | JA | `ChatRequest` | Gibt zuständigen Facharzttyp zurück |
| `/api/chat/guidance` | JA | `ChatRequest` | Listet gängige Behandlungsschritte auf |
| `/api/chat/contextual` | NEIN | `ContextualChatRequest` | Beantwortet freie Folgefragen im Diagnosekontext |

---

## 6. Datenbankschema

Die PostgreSQL-Datenbank (mit pgvector-Erweiterung) speichert die offizielle ICD-10-GM-Klassifikation, Synonyme, semantische Embeddings und gecachte KI-Antworten.

### 6.1 Tabellenübersicht

| Tabelle | Zweck | Ca. Zeilen |
|---|---|---|
| `icd_class` | Offizielle ICD-10-GM-Klassifikation mit allen Metadaten | ~15.000 |
| `icd_synonym` | Alphabetisches Verzeichnis — alternative Namen je Code | ~80.000 |
| `icd_embedding` | 3072-dimensionale Vektoren für semantische Suche (pgvector) | ~95.000 |
| `icd_ai_cache` | Gecachte Gemini-Antworten (explain, specialist, guidance) je ICD-Code | ~300 (Top-100 × 3) |

### 6.2 Tabellendefinitionen

#### `icd_class`

| Spalte | Typ | Einschränkung | Beschreibung |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-inkrementierender Zeilenschlüssel |
| `code` | `VARCHAR(10)` | `UNIQUE, NOT NULL` | ICD-10-Code (z.B. `'I10'`, `'E11.9'`) |
| `kind` | `VARCHAR(50)` | — | Klassifikationstyp (Kategorie, Block, etc.) |
| `title` | `TEXT` | `NOT NULL` | Lesbare Diagnosebezeichnung |
| `definition` | `TEXT` | — | Erweiterte klinische Beschreibung |
| `parent_code` | `VARCHAR(10)` | — | 3-stelliger Elterncode für Subcodes |
| `is_leaf` | `BOOLEAN` | — | `True` wenn keine Subcodes vorhanden |
| `sex_code` | `CHAR(1)` | — | Geschlechtsspezifischer Kodierungsindikator |
| `age_low`, `age_high` | `VARCHAR(10)` | — | Altersbereichsanwendbarkeit |
| `infectious` | `BOOLEAN` | — | Kennzeichen für Infektionskrankheit |

#### `icd_synonym`

| Spalte | Typ | Einschränkung | Beschreibung |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-inkrementierender Zeilenschlüssel |
| `icd_code` | `VARCHAR(10)` | `FK → icd_class.code` | Zugehöriger ICD-Code |
| `term` | `TEXT` | `NOT NULL` | Alternativer Name oder Synonym |
| `coding_type` | `INT` | — | Quelltyp aus BfArM-XML |
| `is_printed` | `BOOLEAN` | — | Ob Begriff im gedruckten Katalog erscheint |

#### `icd_embedding`

| Spalte | Typ | Einschränkung | Beschreibung |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-inkrementierender Zeilenschlüssel |
| `icd_code` | `VARCHAR(10)` | `FK → icd_class.code` | Zugehöriger ICD-Code |
| `source_type` | `VARCHAR(20)` | — | Ursprung: `'title'` oder `'synonym'` |
| `source_id` | `INT` | — | ID des Quelldatensatzes |
| `embedding` | `VECTOR(3072)` | — | Gemini-Embedding-Vektor (Kosinus-Ähnlichkeit) |

#### `icd_ai_cache`

| Spalte | Typ | Einschränkung | Beschreibung |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-inkrementierender Zeilenschlüssel |
| `icd_code` | `VARCHAR(10)` | `FK → icd_class.code, NOT NULL` | Gecachter Diagnosecode |
| `prompt_type` | `VARCHAR(20)` | `NOT NULL` | Eines von: `'explain'`, `'specialist'`, `'guidance'` |
| `response_text` | `TEXT` | `NOT NULL` | Vollständige Gemini-LLM-Antwort |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()` | Erstellungszeitpunkt des Cache-Eintrags |
| — | `UNIQUE` | `(icd_code, prompt_type)` | Maximal 1 Antwort pro Code + Prompt-Typ |

### 6.3 Vektor-Suchabfrage

Die pgvector-Suche verwendet eine zweistufige Aggregation, um Elternkategorien statt einzelner Subcodes zu bevorzugen:

```sql
SELECT icd_code[:3] AS parent_code,
       0.6 * MAX(1 - embedding <=> query_vector)
     + 0.4 * AVG(1 - embedding <=> query_vector) AS combined_score
FROM icd_embedding
GROUP BY parent_code
HAVING MAX(1 - embedding <=> query_vector) >= 0.73
ORDER BY combined_score DESC
LIMIT :limit
```

Diese Formel stellt sicher, dass Kategorien deren Subcodes alle zum Suchbegriff passen (hoher AVG) höher ranken als Kategorien mit einem sehr ähnlichen Subcode aber vielen irrelevanten (hoher MAX, niedriger AVG).

---

## 7. Konfiguration und Umgebungsvariablen

Alle Konfigurationen sind in `config.py` zentralisiert. Kein anderes Produktionsmodul ruft `os.getenv()` direkt auf.

### 7.1 Umgebungsvariablen

| Variable | Pflicht | Standard | Beschreibung |
|---|---|---|---|
| `GEMINI_API_KEY` | JA | — | Google AI Studio API-Schlüssel für Gemini LLM und Embeddings |
| `DB_HOST` | JA | `db` | PostgreSQL-Hostname (Docker-Service-Name) |
| `DB_NAME` | JA | `medcode` | PostgreSQL-Datenbankname |
| `DB_USER` | JA | `medcode` | PostgreSQL-Benutzer |
| `DB_PASSWORD` | JA | `medcode` | PostgreSQL-Passwort |
| `MEILI_URL` | NEIN | `http://meilisearch:7700` | Meilisearch-Server-URL |
| `MEILI_KEY` | NEIN | — | Meilisearch-Master-Schlüssel (optional für lokale Entwicklung) |
| `VITE_API_BASE_URL` | Frontend | `http://localhost:8000` | Backend-URL für die React-Frontend-Anwendung |

### 7.2 Startsequenz

1. Docker Compose startet `db`, `meilisearch`, `backend` und `frontend`.
2. Backend-Container startet `uvicorn main:app`. FastAPIs Lifespan-Kontext wird ausgeführt.
3. `config.py` liest `.env`, initialisiert `genai.Client` (Gemini) und `meilisearch.Index`.
4. `dependencies.py` erstellt die drei Service-Singletons in Abhängigkeitsreihenfolge: `DatabaseService` → `ChatService` → `SearchService`.
5. Der Pool im `DatabaseService` wird **nicht** sofort erstellt — er wird beim ersten Request lazy initialisiert (`_ensure_pool()`).
6. Alle vier Router werden bei FastAPI registriert. Anwendung ist betriebsbereit.

### 7.3 Medical-Synonyms-Modul

Das Modul `medical_synonyms.py` erweitert Suchanfragen mit medizinischen Fachbegriffen:

```python
# Beispiel-Erweiterungen
'Bluthochdruck' → 'Bluthochdruck Hypertonie arterielle Hypertonie Hochdruck'
'Herzrasen'     → 'Herzrasen Tachykardie Palpitationen'
```

Das Modul enthält ca. 70 deutsche Umgangsbegriffe die medizinischen Entsprechungen zugeordnet sind. Die Funktion `expand_query(q)` wird ausschliesslich für die pgvector-Embedding-Suche verwendet.

---

## 8. Import- und Wartungsskripte

### 8.1 `import_icd.py` — Erstmaliger Datenimport

Wird einmalig beim initialen Setup oder nach ICD-Katalog-Aktualisierungen ausgeführt.

1. Erstellt Datenbanktabellen und aktiviert die pgvector-Erweiterung.
2. Parst die offizielle BfArM ICD-10-GM ClaML-XML-Datei (~15.000 Klassifikationseinträge).
3. Generiert Titel-Embeddings in 500er-Batches mit dem Gemini `gemini-embedding-001` Modell.
4. Parst das alphabetische Synonymverzeichnis (~80.000 Einträge) und generiert Synonym-Embeddings.

> **Zeithinweis:** Die erstmalige Embedding-Generierung dauert ca. 20–30 Minuten aufgrund von Gemini-API-Rate-Limits. Einmalig ausführen und nicht wiederholen ausser bei Katalog-Updates.

### 8.2 `import_meili.py` — Meilisearch-Index-Aufbau

1. Holt alle 3-stelligen ICD-Codes aus PostgreSQL.
2. Baut ein Meilisearch-Dokument pro Code mit einem `search_text`-Feld (Code + Titel + Synonyme).
3. Konfiguriert Tippfehlertoleranz: `oneTypo: 4`, `twoTypos: 6` (besser als Standardwerte 5/8).
4. Lädt deutsche umgangssprachliche Synonym-Mappings in Meilisearch.

### 8.3 `seed_cache.py` — KI-Cache-Vorwärmer

1. Fragt die Top-100 häufigsten ICD-Codes ab (nach Synonymanzahl sortiert).
2. Ruft alle drei Chat-Endpunkte für jeden Code auf (`/chat/explain`, `/chat/specialist`, `/chat/guidance`).
3. Wartet 4,2 Sekunden zwischen Anfragen (Gemini Free-Tier-Rate-Limit: 15 Anfragen/Minute).
4. Erstellt ca. 300 Cache-Einträge (100 Codes × 3 Prompt-Typen).

---