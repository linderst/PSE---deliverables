# Architektur & Funktionsweise: ICD-10 AI Prompt Engineer

Dieses Dokument erklärt detailliert und technisch, wie die gesamte Applikation vom Starten bis zur endgültigen KI-Diagnose funktioniert.

## 1. Das Big Picture: Retrieval-Augmented Generation (RAG)

Traditionelle Large Language Models (LLMs) wie ChatGPT oder Gemini "halluzinieren" (erfinden Fakten) oft, wenn es um sehr spezifisches Fachwissen geht. In der Medizin ist das gefährlich. 

Um dieses Problem zu lösen, implementiert dieses Projekt eine moderne KI-Architektur namens **RAG (Retrieval-Augmented Generation)**.
Anstatt das Modell einfach blind raten zu lassen, funktioniert RAG wie eine Open-Book-Klausur für die KI: 
1. **Retrieval (Suchen):** Wenn du ein Symptom (z.B. "Kopfschmerzen") eintippst, sucht das System zuerst *selbstständig* in einem offiziellen medizinischen Katalog nach den besten Treffern.
2. **Augmented Generation (Erweitertes Generieren):** Das System gibt der KI nicht nur deine Frage, sondern *auch* das Suchergebnis aus Schritt 1 als verlässliche Faktenbasis (den "Ground Truth") mit auf den Weg.
3. Die KI liest die echten Fakten durch und formuliert basierend darauf eine präzise Antwort.

---

## 2. Die Infrastruktur: Docker Compose

Damit all das ohne komplizierte Installationen auf jedem Computer läuft, ist das Projekt in 3 sogenannte **Docker Container** unterteilt, die komplett isoliert voneinander laufen, aber intern über ein virtuelles Netzwerk kommunizieren. Diese werden über die `docker-compose.yml` orchestriert.

### A. Datenbank Container (`db`)
- Läuft auf: **PostgreSQL 16** (dem Standard für relationale Datenbanken).
- Modifikation: Es ist die spezielle Erweiterung **`pgvector`** installiert. Normale Datenbanken können nur exakt nach dem Wort "Kopfschmerz" suchen. Vektordatenbanken können auch nach Inhalten suchen, die "Migräne" ähnlich sind, indem sie Text als geometrischen Punkt in einem extrem hochdimensionalen Raum (meist 384 Dimensionen) speichern.
- Speichert seine Daten dauerhaft im Volume `db_data` auf deiner Festplatte.

### B. Backend Container (`backend`)
- Das Gehirn der Applikation, geschrieben in **Python**.
- Nutzt das moderne und rasante **FastAPI** Framework.
- Ist über Port `8000` erreichbar.
- Hier läuft sowohl die Logik für Vektorsuchen, als auch die Kommunikation mit Google Gemini ab.

### C. Frontend Container (`frontend`)
- Die Benutzeroberfläche, geschrieben in **React** & **TypeScript**, gebaut mit dem Tooling **Vite**.
- Läuft auf Port `5173`.
- Nimmt nur deine Eingaben auf und stellt sie schön dar, die eigentliche Arbeit macht das Backend.

---

## 3. Schritt 1: Der Daten-Import (`import_icd.py`)

Bevor überhaupt Fragen gestellt werden können, muss die Datenbank mit medizinischem Wissen gefüllt werden (dies geschieht über den Importer-Container, den du beim ersten Mal ausgeführt hast).

1. Der Code (`import_icd.py`) liest tausende von Einträgen aus offiziellen deutschen **ICD-10 XML-Dateien** (herausgegeben vom BfArM). ICD-10 ist das internationale Klassifikationssystem für Krankheiten.
2. Das Skript lädt ein lokales KI-Modell (`paraphrase-multilingual-MiniLM-L12-v2`) von HuggingFace herunter. Dies ist ein sogenanntes **Embedding-Modell**.
3. Jeder einzelne Krankheitsname aus dem XML wird durch dieses kompakte Modell geschoben. Das Modell wandelt den Text-Satz (z.B. *G43.0: Migräne ohne Aura*) in eine Liste hunderter Kommazahlen (den Vektor) um.
4. Diese Zahlen-Listen (Embeddings) werden zusammen mit den Klartexten in die PostgreSQL Datenbank (`db`) gespeichert.

*Dieser Schritt dauert sehr lange, da hunderttausende solcher Vektoren lokal auf der CPU deines Laptops berechnet werden müssen.*

---

## 4. Schritt 2: Der Ablauf bei einer Benutzer-Anfrage

Wenn du im Frontend auf "Generate Diagnosis" klickst, wird das Backend aufgerufen (die Schnittstelle `/api/diagnose` in `main.py`). Dann passiert Folgendes in Bruchteilen einer Sekunde:

### Phase A: Vektorisierung deiner Eingabe
Das Backend nimmt genau deine Formulierung von der Tastatur entgegen und schickt sie ebenfalls durch das kleine, lokale Embedding-Modell (SentenceTransformer). Deine Eingabe (z.B. *"Mir pocht der Schädel und mir wird schlecht"*) wird in genau denselben 384-dimensionalen Vektor-Raum übersetzt wie die ICD-Katalog-Daten beim Import.

### Phase B: Die Vektorsuche (`K-Nearest Neighbors / Cosine Similarity`)
Das Backend öffnet eine Verbindung zur PostgreSQL Datenbank und sagt: *"Hier ist ein Vektor. Vergleiche ihn mit allen 100.000 Vektoren im Katalog und gib mir die 5 Ergebnisse zurück, die mathematisch am dichtesten an diesem Punkt liegen".*

Die Datenbank berechnet die `Cosine Similarity` (die Winkel-Differenz zwischen den Linien der Vektoren im 384D Raum) und liefert blitzschnell die 5 Katalogeinträge zurück, die inhaltlich absolut am besten zu deiner Beschreibung passen.

### Phase C: Prompt Engineering (Der wichtigste Schritt)
Jetzt wird der fertige Text (der "Prompt") für das eigentliche, riesige Google Gemini LLM zusammengebaut.

Das Backend schnürt das dynamische Paket aus drei Dingen zusammen:
1. **Die System-Instruktion:** ("Du bist ein hilfreicher medizinischer Kodier-Assistent...")
2. **Deine ursprüngliche Eingabe:** ("Symptome: Mir pocht der Schädel...")
3. **Der Ground Truth / Kontext:** ("Die Vektordatenbank hat folgende relevanten ICD-10 Codes als treffend gefunden: G43.0 Migräne, G44.1 Spannungskopfschmerz...")

*Dieser Bereich in der `main.py` (Zeile ~138) ist der Ort, an dem du als "Prompt Engineer" das System feinjustieren kannst, um bessere oder detailreichere Ergebnisse zu erzwingen.*

### Phase D: Der API-Call
Über das Internet wird dieser fertige Prompt blockweise inklusive deinem in der `.env` hinterlegten `GEMINI_API_KEY` an die Google-Server in den USA/Europa geschickt. Das gigantische `gemini-2.5-flash` Modell verarbeitet den Text, schreibt seine medizinisch fundierte Herleitung basierend auf unseren mitgelieferten Vektoren, und schickt die Antwort zurück an das Backend.

Das Backend packt die KI-Antwort und die Liste der verwendeten 5 Top-Suchtreffer ein und meldet sich beim Frontend.

### Phase E: Darstellung
Dein Frontend-Code erhält die Antwort, schließt den rotierenden Ladebalken ("Loading...") und platziert den Markdown-formatierten Text von Gemini in das Textfeld. Gleichzeitig listet es darunter transparent für den User die 5 Datenbanktreffer auf, die verwendet wurden, um die Antwort zusammenzubauen (als Quellenangabe & Verifizierbarkeit im medizinischen Kontext immens wichtig!).
