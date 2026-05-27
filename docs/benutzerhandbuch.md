# Benutzerhandbuch — Medcode Diagnosensuche (Stand 30.03.2026)

## 1. Einführung

**Medcode** ist eine webbasierte Plattform zur Suche und verständlichen Erklärung medizinischer Diagnosen. Die Anwendung richtet sich an Patientinnen und Patienten, die auf ihren Arztrechnungen oder Arztbriefen ICD-10-Codes finden und wissen möchten, was diese bedeuten.

**Zielgruppe:** Laien ohne medizinisches Fachwissen, die ihre Diagnosen verstehen möchten.

**Was ist ein ICD-10-Code?** ICD-10 ist das internationale Klassifikationssystem für Krankheiten. Jede Diagnose hat einen eindeutigen Code (z.B. J18.9 für Pneumonie). Diese Codes werden in der Schweiz auf Arztrechnungen und in medizinischen Dokumenten verwendet.

---

Für die Nutzung der Medcode-Plattform gelten folgende Voraussetzungen:

### Für Endnutzer (Client)
* **Webbrowser:** Ein moderner, standardkonformer Webbrowser (z. B. Google Chrome, Mozilla Firefox, Apple Safari oder Microsoft Edge) mit aktiviertem JavaScript.
* **Bildschirmauflösung:** Die Anwendung ist voll-responsiv gestaltet und für mobile Geräte (Smartphones, Tablets) sowie Desktop-Bildschirme optimiert.

### Für den Serverbetrieb (Infrastruktur)
Die genauen Anforderungen für den Serverbetrieb und die Installation mittels Docker findest du am Ende dieses Dokuments im **Anhang A: Installation und Betrieb**.

---

## 3. Startseite

Beim Aufrufen der Anwendung erscheint die Startseite mit zwei Hauptelementen:

<!-- Screenshot: Startseite -->
![Screenshot](/docs/screenshots/startseite.png)

### 3.1 Suchfeld

Das zentrale Suchfeld akzeptiert zwei Arten von Eingaben:
- **ICD-10-Code** (z.B. `J18.9`, `E11`, `I10`): liefert sofortige, exakte Ergebnisse
- **Freitext-Symptome** (z.B. "pulsierende Kopfschmerzen mit Übelkeit") die KI sucht den passenden Code


### 3.2 Krankheits-Index (A-Z)

Unterhalb des Suchfelds befindet sich ein alphabetischer Index mit vorbereiteten Diagnosen. Klicken Sie auf einen Buchstaben, um Diagnosen zu filtern, und wählen Sie eine Diagnose direkt aus.

<!-- Screenshot: Krankheits-Index (A-Z) -->
![Screenshot](/docs/screenshots/krankheitsindex.png)

---

## 4. Suche durchführen

### 4.1 Suche nach ICD-10-Code

Wenn Sie einen bekannten Code eingeben (z.B. `J18.9`):
1. Das System erkennt das Code-Muster automatisch
2. Der exakte Treffer wird sofort angezeigt (Treffsicherheit: 100%)
3. Die KI-Erklärungen werden parallel geladen

### 4.2 Suche nach Symptomen oder Krankheitsnamen

Bei Freitext-Eingaben (z.B. "starke Rückenschmerzen"):
1. Das System durchsucht den medizinischen Katalog
2. Bei hoher Treffsicherheit (>= 75%) wird das Ergebnis sofort angezeigt
3. Bei geringerer Sicherheit startet ein KI-gestützter Prompt:
   - Die Anzeige wechselt zu "KI-Diagnose läuft..."
   - Nach ca. 2-3 Sekunden erscheint: "Detaillierte Analyse deines komplexeren Symptoms..."
   - Das verfeinerte Ergebnis trägt den Badge "KI-verfeinert"
### 4.3 Alternative Vorschläge
Das System beschränkt sich nicht nur auf das beste Ergebnis, sondern präsentiert darunter alternative Übereinstimmungen als auswählbare Chips (siehe Abschnitt 5.2). So können Benutzer auch bei unscharfen Beschreibungen die am besten passende Diagnose finden.
---

## 5. Ergebnis-Ansicht

Nach einer erfolgreichen Suche wird die Ergebnis-Ansicht angezeigt:

<!-- Screenshot: Vollständige Ergebnisseite -->
![Screenshot](/docs/screenshots/ergebnisansicht.png)

### 5.1 Diagnose-Karte

Die prominente Hauptkarte zeigt:
- **ICD-10-Code** (z.B. J18) als blaues Badge
- **Diagnose-Titel** (z.B. "Pneumonie, Erreger nicht näher bezeichnet")
- **Katalogversion** (ICD-10)
- **Treffsicherheit** als kreisförmiger Tachometer (0-100%)

<!-- Screenshot: Diagnose-Karte mit Tachometer -->
![Screenshot](/docs/screenshots/tachometerdetail.png)

Falls die KI das Ergebnis verbessert hat, erscheint zusätzlich ein violettes Badge mit dem Text **"KI-verfeinert"**.

### 5.2 Weitere Treffer

Unterhalb der Hauptkarte werden alternative Diagnosen als kleine Chips angezeigt. Jeder Chip zeigt den ICD-10-Code. Bewegen Sie die Maus über einen Chip, um den vollständigen Diagnosenamen und die Treffsicherheit zu sehen.

- Chips mit **grüner Hervorhebung** und Häkchen haben eine besonders hohe Treffsicherheit (>= 95%)
- **Klick** auf einen Chip wechselt zu dieser Diagnose

### 5.3 Informationsblöcke

Drei KI-generierte Informationskarten laden parallel und unabhängig voneinander:

| Block | Inhalt |
|-------|--------|
| **Was ist das?** | Laienverständliche Erklärung der Diagnose |
| **Wer behandelt das?** | Empfohlener Facharzt + Link zu extradoc.ch |
| **Wie wird behandelt?** | Übliche Behandlungsmethoden und erste Schritte |

Jeder Block zeigt während des Ladens einen Spinner ("Wird geladen...") und kann unabhängig Fehler anzeigen.

### 5.4 Spezifische Diagnosen (Unterkategorien)

Ein aufklappbares Panel listet die spezifischeren Unterkategorien der aktuellen Diagnose auf. Zum Beispiel zeigt die Kategorie I10 (Hypertonie) alle Varianten wie I10.0, I10.1 etc.

- **Klick auf den Toggle** öffnet/schliesst das Panel
- Jede Zeile zeigt Code, Titel und einen Relevanzbalken
- **Klick auf eine Zeile** navigiert zur spezifischen Diagnose

<!-- Screenshot: Unterkategorien einer Diagnose -->
![Screenshot](/docs/screenshots/unterkategorien.png)

### 5.5 Folgefragen stellen (Dialog)

Am unteren Rand befindet sich ein Eingabefeld für Folgefragen. Die Fragen beziehen sich automatisch auf die aktuelle Diagnose.

**Beispiel: Bei der Diagnose "Asthma bronchiale" können Sie fragen: "Ist das ansteckend?" oder "Wie lange dauert die Genesung?"

- Geben Sie Ihre Frage ein und drücken Sie `Enter` oder klicken Sie auf "Senden"
- Die Antwort erscheint im Gesprächsverlauf
- Der Verlauf ist auf-/zuklappbar über den Header "Gesprächsverlauf (X Nachrichten)"

<!-- Screenshot: Dialog mit Folgefrage und Antwort -->
![Screenshot](/docs/screenshots/dialogpanel.png)


---

## 6. Navigation

| Aktion | Beschreibung |
|--------|-------------|
| Neue Suche | Suchfeld in der oberen Leiste, Enter drücken |
| Zurück zur Startseite | Klick auf "medcode.ch"-Logo oben links |
| Browser Zurück/Vor | Wird vollständig unterstützt |
| Direkt-URL | Jede Diagnose hat eine eindeutige URL (z.B. `/pneumonie/J18.9`), die geteilt oder als Lesezeichen gespeichert werden kann |

---

## 7. Hinweis zur medizinischen Beratung

Die auf Medcode bereitgestellten Informationen dienen ausschliesslich der allgemeinen Orientierung und ersetzen keine ärztliche Beratung, Diagnose oder Behandlung. Bei gesundheitlichen Beschwerden wenden Sie sich bitte an Ihren Arzt oder Ihre Ärztin.

Für ärztliche Zeugnisse, Rezepte oder eine medizinische Beratung besuchen Sie [extradoc.ch](https://extradoc.ch).

---

## Anhang A: Installation und Betrieb (für Systemadministratoren)

### A.1 Voraussetzungen

| Anforderung | Minimum |
|------------|---------|
| Docker + Docker Compose | Version 2.0+ |
| RAM | 4 GB |
| Festplatte | 10 GB (inkl. Datenbank, Modelle, Suchindex) |
| Google Gemini API-Key | Erforderlich für KI-Funktionen |
| Netzwerk | Ausgehende HTTPS-Verbindungen zu Google APIs |

### A.2 Erstinstallation

1. **Repository klonen:**
```bash
git clone <repository-url>
cd <repository-name>
```

2. **Umgebungsvariablen einrichten:**
```bash
cp .env.example .env
```
Öffnen Sie `.env` und tragen Sie Ihren Gemini API-Key ein:
```
GEMINI_API_KEY=ihr_api_key_hier
```

3. **Daten importieren (einmalig, ca. 30 Minuten):**
```bash
# Importer-Images bauen
docker compose --profile import build

# ICD-10 Daten + Vektoren generieren
docker compose --profile import run --rm importer

# Meilisearch-Index befuellen
docker compose --profile import run --rm meili-importer
```

4. **Anwendung starten:**
```bash
docker compose up -d --build
```

Die Anwendung ist nun erreichbar unter:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Meilisearch:** http://localhost:7700

### A.3 Betrieb

**Container starten:**
```bash
docker compose up -d
```

**Container stoppen:**
```bash
docker compose down
```

**Logs einsehen:**
```bash
# Alle Services
docker compose logs -f

# Nur Backend
docker compose logs -f backend
```

**Datenbank-Backup:**
```bash
docker compose exec db pg_dump -U medcode medcode > backup.sql
```

### A.4 Service-Übersicht

| Service | Port | Beschreibung |
|---------|------|-------------|
| `frontend` | 5173 | React/Vite Entwicklungsserver |
| `backend` | 8000 | FastAPI Server (Python) |
| `db` | 5432 | PostgreSQL 16 + pgvector |
| `meilisearch` | 7700 | Volltextsuche |

### A.5 Häufige Probleme

| Problem | Lösung |
|---------|---------|
| Container startet nicht | `docker compose logs <service>` prüfen |
| "Connection refused" beim Backend | Warten bis Health-Check der Datenbank abgeschlossen ist |
| Suche liefert keine Ergebnisse | Daten-Import (Schritt 3) wiederholen |
| Gemini-Antworten fehlen | GEMINI_API_KEY in `.env` prüfen |
| Port bereits belegt | Anderen Port in `docker-compose.yml` konfigurieren |

### A.6 Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|-------------|---------|
| `DB_NAME` | Datenbankname | medcode |
| `DB_USER` | Datenbankbenutzer | medcode |
| `DB_PASSWORD` | Datenbankpasswort | changeme |
| `GEMINI_API_KEY` | Google Gemini API-Schlüssel | (erforderlich) |
| `MEILI_URL` | Meilisearch URL | http://meilisearch:7700 |
| `MEILI_KEY` | Meilisearch Master-Key | masterKey |
| `VITE_API_BASE_URL` | Backend-URL für Frontend | http://localhost:8000/api |
