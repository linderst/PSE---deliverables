# Docker-Anleitung – Medcode Entwicklungsumgebung

## Was ist Docker?

Docker löst das Problem "bei mir läuft es": Jeder im Team hat eine andere Python-Version, ein anderes OS, andere Libraries installiert und kriegt andere Fehler. Docker packt die gesamte Anwendung mit allem was sie braucht in isolierte **Container**, die auf jedem Computer identisch laufen.

In unserem Projekt starten wir mit einem einzigen Befehl drei Container gleichzeitig:

```
┌──────────────────────────────────────────────────┐
│  Dein Computer                                   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │ frontend │  │ backend  │  │      db       │   │
│  │  (React) │  │ (FastAPI)│  │  (PostgreSQL) │   │
│  │  :5173   │  │  :8000   │  │     :5432     │   │
│  └──────────┘  └──────────┘  └───────────────┘   │
└──────────────────────────────────────────────────┘
```

Code-Änderungen in `src/` werden sofort in den Containern sichtbar – kein Neustart nötig.
Die `.env`-Datei liefert Passworter und API-Keys an die Container, ohne dass diese im Code stehen.

---

## 1. Voraussetzungen

### Docker Desktop installieren

- **Mac:** https://docs.docker.com/desktop/install/mac-install/
- **Windows:** https://docs.docker.com/desktop/install/windows-install/

Nach der Installation Docker Desktop starten und warten, bis das Symbol in der Menuleiste grün ist.

> **Windows-Nutzer:** Docker Desktop benötigt WSL 2 (Windows Subsystem for Linux).
> Falls WSL 2 nicht installiert ist, erscheint ein Hinweis beim ersten Start.

---

## 2. Repository klonen

```bash
git clone <repo-url>
cd PSE---deliverables
```

---

## 3. Umgebungsvariablen einrichten

Im Projektstamm liegt eine Vorlage `.env.example`. Diese kopieren und bearbeiten:

**Mac / Linux:**
```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

Die `.env`-Datei mit einem Texteditor öffnen (alle Variabeln können für DB beliebig geändert werden) und den Gemini API Key eintragen:

```
DB_NAME=medcode
DB_USER=medcode
DB_PASSWORD=changeme

GEMINI_API_KEY=hier_den_echten_key_eintragen
```

> Die `.env`-Datei wird nicht ins Git-Repository committet. Jedes Teammitglied pflegt sie lokal.

---

## 4. Entwicklungsumgebung starten

Zurück im Projektstamm:

```bash
docker compose up -d
```

Beim ersten Aufruf werden die Docker-Images gebaut. Das dauert **5–10 Minuten**,
weil unter anderem PyTorch und sentence-transformers heruntergeladen werden.
Danach wird der Aufbau gecacht und der Start dauert nur noch wenige Sekunden.

Wenn alles lauft, sind folgende Adressen erreichbar:

| Service    | Adresse                  |
|------------|--------------------------|
| Frontend   | http://localhost:5173    |
| Backend API| http://localhost:8000    |
| Datenbank  | localhost:5432           |

---

## 5. ICD-Daten importieren 

Dieser Schritt ist notwendig, um die Datenbank mit ICD-10-Daten zu befüllen.

**Schritt 1:** Die beiden Dateien von BfArM in den `data/`-Ordner legen:
- `icd10gm2026syst_claml_20250912.xml`
- `icd10gm2026alpha_edvtxt_20250926.txt`

**Schritt 2:** Importer ausführen:

```bash
docker compose --profile import run --rm importer
```

Der Importer läuft durch und beendet sich von selbst. Beim ersten Aufruf wird
ausserdem das Embedding-Modell heruntergeladen (~500 MB) – das geschieht nur einmal
und wird danach gecacht.

> Der Import kann je nach Hardware **30–60 Minuten** dauern, da für jeden ICD-Eintrag
> ein Embedding berechnet wird.

---

## 6. Täglicher Arbeitsablauf

```bash
# Umgebung starten
docker compose up -d

# Umgebung stoppen (Daten bleiben erhalten)
docker compose down
```

Code-Änderungen im `src/backend/` und `src/frontend/` werden dank Volume-Mounts
und Hot-Reload **sofort** übernommen, ohne Neustart.

---

## 7. Häufige Befehle

```bash
# Status aller Services anzeigen
docker compose ps

# Logs eines Services live verfolgen
docker compose logs -f backend
docker compose logs -f frontend

# Einzelnen Service neu bauen (z.B. nach requirements.txt Anderung)
docker compose build backend

# Alles stoppen und Volumes loschen (Datenbank wird zurückgesetzt)
docker compose down -v
```

---

## 8. Häufige Probleme

### "Port already in use"
Ein anderes Programm belegt Port 5173, 8000 oder 5432. Docker Desktop beenden,
das andere Programm stoppen, dann erneut starten.

### Backend startet nicht (Datenbankfehler)
Die Datenbank braucht beim ersten Start ein paar Sekunden. Kurz warten und dann:
```bash
docker compose restart backend
```

### Image neu bauen erzwingen
```bash
docker compose build --no-cache
docker compose up -d
```
