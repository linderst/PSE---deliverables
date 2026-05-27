[//]: # (this is a .md comment)

# Protokoll – [interes Meeting, 2. Iteration]

**Datum:** [23. März 2026]  
**Zeit:** [18:00 – 19:00 Uhr]  
**Ort:** [online - Discord]  
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

[//]: # (für interne Meetings, Kundenseite als comment lassen)
[//]: # (
    **Kundenseite:**
    | Name | Rolle | anwesend |
    |---|---|---|
    | Stefan Vogt   | Geschäftsführer, Medcode GmbH |-|
    | Simon Hölzer  | Arzt, Medcode GmbH            |-|
    )

"x" - **anwesend**  
"-" - **entschuldigt abwesend**  
## Traktanden

| Nr. | Dauer | Traktandum | Zeitmanagement |
|---|---|---|---|
| 1 | 20min | Project bei allen             | Felix |
| 2 | 10min | Meilisearch in depth Erklärung | Stefan |
| 3 | 10min | Meilisearch vs pgvector       | Christian |
| 4 | 10min | Static Problem - extra DB?    | Dennis |
| 5 | 10min | Aufgaben & next Meeting       | Alex |

### 1 - [Project bei allen]

* soll bei allen auf den gleichen Stand funktionieren

Problem macht die Vektordatenbank. Stefan hat jetzt aus dem `.gitignore` die Datenbank-XML genommen und jeder muss auf seinem PC das Vektorembedding machen.

### 2 – [Meilisearch in depth Erklärung]

* Erklärung was ist Meilisearch
* Wie funktioniert es
* Pro - Kontra allgemein

Stefan hat den aktuellen Suchalgorithmus vorgestellt. Der Ablauf ist wie folgt:
 
1. Eingabe wird per Regex auf einen direkten ICD-10-Code geprüft (z. B. „I10"). Falls Treffer, wird direkt das Ergebnis zurückgegeben.
2. Falls kein direkter Code-Treffer: Suche über Meilisearch.
3. Falls Meilisearch 0 Treffer liefert, wird eine Vektorsuche (pgvector) ausgelöst. Diskutiert wurde, ob der Fallback bereits bei niedriger Meilisearch-Konfidenz (z. B. unter 45 %) greifen sollte, nicht erst bei 0 Treffern.
4. Falls die Konfidenz weiterhin unter 75 % liegt, wird die Gemini-API aufgerufen, um den Eingabetext in medizinische Fachbegriffe umzuwandeln. Anschliessend wird Schritt 2 mit den neuen Begriffen wiederholt.

### 3 – [Meilisearch vs pgvector]

* Pro - Kontra für unser Projekt  
Meilisearch - PgVector
* Diskussion, welche Option auswählen
    * rein Meilisearch
    * rein PgVector
    * Hybrid
* Beschluss

Diskussion über die Rolle von pgvector im Projekt:
 
- Das Tool deckt ausschliesslich ICD-10-Codes und medizinische Fachbegriffe ab – kein Nonsense.
- Ein Fallback auf pgvector ist nötig: Beispiel „Ich habe Hodenschmerzen" liefert bei Meilisearch fälschlicherweise Treffer für „Schilddrüsen".
- **Idee:** Die verschiedenen Such-Engines nicht nur sequenziell, sondern parallel laufen lassen und prüfen, ob die Ergebnisse besser werden.
- **Offene Frage:** Ist pgvector für den Kunden zwingend oder optional? Soll beim nächsten Kundenmeeting geklärt werden.

### 4 - [Static Problem - extra DB?]

* klaren Beschluss - was soll angezeigt/gespeichert werden
* technische Umsetzungsansätze
* Beschluss

- Alte Suchanfragen werden bereits heute in einer separaten Tabelle gespeichert.
- **Neues Feature-Idee: „Feedback Button"** – Falls ein schlechtes Ergebnis angezeigt wird, kann der Nutzer dies melden. Es erfolgt dann ein Reprompt über die KI mit angepasster Anfrage.


### 5 - [Aufgaben & next Meeting ]

* Klare Strukturierung
    * Wer hat welche Aufgabe
    * Deadlines
* nächstes Meeting
    * mit Kunden:  
     25.3. 11:00Uhr
    * interes Meeting?

* Aufgaben:
- [ ] Thresholds definieren (Stefan, Christian) (bis Mittwoch 25.03)
- [ ] UI anpassen (es benötigt keinen Verlauf in linker Seitenleiste) (Alex)
- [ ] Doku schreiben (Felix, Dennis)
- [ ] Parallelisierung überprüfen (Julien
- [ ] Anleitungen anpassen (Docker) (Felix, Dennis)
- [ ] Tests schreiben (wegen Fallbacks, ob pgvector nötig) (Stefa, Christian, Julien)
- [ ] Jeder sollte es zum Laufen bringen (Alle)

## Beschlussprotokoll

- [Beschluss] – *[Verantwortlich]*

