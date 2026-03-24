[//]: # (this is a .md comment)

# Protokoll – [Demo 2. It. & Planning Game 3.]

**Datum:** [25. März 2026]  
**Zeit:** [11:00 – 12:00 Uhr]  
**Ort:** [Länggassstrasse 31]  
**Sitzungsleitung:** [Julien]  
**Protokoll:** [Julien]

## Teilnehmer

**Entwicklungsteam:**

| Name | Rolle | anwesend |
|---|---|---|
| Felix Buchmüller  | Key Account Manager       |x|
| Alexander Bot     | Master Tracker            |x|
| Stefan Linder     | Chief Deliverable Officer |x|
| Christian Gafner  | Quality Evangelist        |x|
| Dennis Roduner    | Leitung / Protokoll       |x|
| Julien Chopin     | Leitung / Protokoll       |x|


**Kundenseite:**
| Name | Rolle | anwesend |
|---|---|---|
| Stefan Vogt   | Geschäftsführer, Medcode GmbH |-|
| Simon Hölzer  | Arzt, Medcode GmbH            |x|


"x" - **anwesend**  
"-" - **entschuldigt abwesend**  
## Traktanden

| Nr. | Dauer | Traktandum | Zeitmanagement |
|---|---|---|---|
| 1 | 5min | Begrüssung | Stefan |
| 2 | 10min | Demo | Christian |
| 3 | 10min | Besprechung Demo | Dennis |
| 4 | 10min | Parallelität | Alex |
| 5 | 20min | Planning Game 3. | Felix |
| 6 | 5min | Abschluss | - |

### 1 – [Begrüssung]

Kurze Begrüssung

### 2 – [Demo]

Stefan und/oder Felix stellen die zweite Iteration vor.  
Dabei soll besonders auf die Funktionalitäten, weniger auf den technischen Aspekt eingegangen werden.

Klare Vorführung.

### 3 - [Besprechung Demo]

Kunde gibt seine Meinung über die Iteration und Vorschläge, welche Aspekte fehlen / zu verbessern sind.  

Anhaltspunkte für die 3. Iteration.

### 4 - [Parallelität]

Momentan haben wir serielle Hybride Architektur, jedoch die Frage ob parallel besser wäre.

##### Hybrid (seriell – aktueller Ansatz)

* User Query
* → Meilisearch (Keyword Search)
* → sonst pgvector (Semantic Search)
* → sonst Query Rewrite (LLM)
* kompletter Prozess startet erneut

* Vorteile
  * einfach implementieren
  * potenziell weniger Compute (nicht immer beide Systeme)
  * klarer Ablauf

* Nachteile
  * verpasst Kombination Keyword + Semantik
  * stark abhängig Thresholds
    * fragile Threshold-Definition
  * Query Rewrite
  * inkonsistente Qualität
  * höhere Worst-Case Latenz (mehrere Durchläufe)

##### Hybrid (parallel)

* User Query
* → Embedding erzeugen → parallel:
    * Meilisearch (Keyword Top-K)
    * pgvector (Semantic Top-K)
* → Merge (IDs zusammenführen) → Score Kombination (Hybrid Score) - Important Note: logging für tuning
* → Ranking
* → Top-K Auswahl
* → optional: Re-Ranking (LLM)

* Vorteile
  * bessere Suchqualität (Keyword + Semantik kombiniert)
  * stabilere Ergebnisse
  * weniger Bedarf für Query Rewrite - weniger LLM API calls (billiger)
  * geringere Latenz im Durchschnitt
  * besser skalierbar

* Nachteile
  * höhere Implementationskomplexität
  * Merge- und Ranking-Logik notwendig
  * beide Systeme werden immer abgefragt (mehr Compute)

### 5 - [Planning Game 3.]

#### Vorschläge des Teams für die 3. Iteration:
* Parallelität
* Reprompts
    * Feedback system
    * Button - Limit
    * im Cache statt DB
* Logging für debugging
    * Query
    * keyword_score
    * semantic_score
    * hybrid_score
    * final Top-K
* Performance Monitoring
    * Meilisearch
    * pgvector
    * LLM
    * Gesamt-Response-Time tracken
    * Alerts (optional)
* Server implementierung

#### Vorschläge Kunde



## Beschlussprotokoll

- [Beschluss] – *[Verantwortlich]*

## Offene Punkte

- [ ] [Aufgabe] – *[Verantwortlich]*

## Nächster Termin

**[Datum]** – [Ort]
