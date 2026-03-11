# Protokoll – Zweites Kundengespräch Medcode

**Datum:** Mittwoch, 11. März 2026  
**Zeit:** 18:00 – ca. 19:00 Uhr  
**Ort:** Bern, Länggassstrasse 18
**Sitzungsleitung:** Dennis Roduner  
**Protokoll:** Dennis Roduner  
**Betreuer:** Raphael Keller (TA)

---

## Teilnehmende

**Entwicklungsteam:**

| Name | Rolle |
|---|---|
| Felix Buchmüller | Key Account Manager |
| Alexander Bot | Master Tracker |
| Stefan Linder | Chief Deliverable Officer |
| Christian Gafner | Quality Evangelist |
| Dennis Roduner | Sitzungsleitung / Protokoll (online zugeschaltet) |
| Julien Chopin | Sitzungsleitung / Protokoll ***entschuldigt abwesend***|

**Kundenseite:**

| Name | Rolle |
|---|---|
| Simon Hölzer | Arzt, Medcode GmbH |

---

**Hier noch einfügen wer wirklich von Kundenseite teilnimmt**

## Traktanden

| Nr. | Zeit | Traktandum | Verantwortlich |
|---|---|---|---|
| 1 | 18:00 | Begrüssung | Felix |
| 2 | 18:05 | Demo des aktuellen Prototyps | Christian |
| 3 | 18:20 | Fragen an den Kunden | Dennis |
| 4 | 18:35 | Planning Game – Iteration 2 (Finetuning & mögliche Erweiterungen) | Team / Medcode |
| 5 | 18:55 | Zusammenfassung und nächste Schritte | Alex |

---

### Traktandum 1 – Begrüssung

- Begrüssung der Teilnehmenden  
- Kurzer Überblick über den Ablauf des Treffens  

---

### Traktandum 2 – Demo des aktuellen Prototyps

- Vorstellung des aktuellen Entwicklungsstands  
- Demonstration der zentralen Funktionen (z.B. Suchanfrage, generierte Antwort, Datenbank/Embedding-Prototyp)  
- Kurze Erläuterung der technischen Architektur  

---

### Traktandum 3 – Fragen an den Kunden

**User Stories**

- Validierung der bisherigen User Stories  
- Klärung, ob weitere Anwendungsfälle ergänzt werden sollen  
- Priorisierung der wichtigsten Funktionen aus Kundensicht  

**Data Privacy**

- Umgang mit Nutzerdaten  
- Sollten User-Anfragen anonymisiert gespeichert werden?  
- Welche Anforderungen bestehen bezüglich Datenschutz und Logging?  

---

### Traktandum 4 – Planning Game: Iteration 2

- Rückblick auf Iteration 1  
- Definition der Ziele für Iteration 2  
- Fokus auf:
  - Finetuning der bestehenden Funktionen  
  - Verbesserung der Suchlogik / Embeddings  
  - mögliche zukünftige Erweiterungen  

- Gemeinsame Priorisierung der nächsten Schritte  

---

### Traktandum 5 – Zusammenfassung und nächste Schritte

- Kurze Zusammenfassung der wichtigsten Punkte und Beschlüsse  
- Festhalten offener Fragen  

- Planung der nächsten Iteration und weiterer Meetings  

## Protokoll vom 11. März 2026 um 18:06 Uhr
Felix stellt die Frage, wie mit den ICD-10-Codes umzugehen ist. Simon Hölzer erläutert daraufhin das
grundlegende Konzept: Zuerst wird über die Datenbank der passende ICD-Code ermittelt, anschliessend
wird dieser Code als Kontext an die KI übergeben, die darauf aufbauend die Antwort generiert.
Beispiel: Sucht ein Nutzer nach "Ziegenpeter", soll im Hintergrund "Mumps" (B26) identifiziert und
als Kontext verwendet werden.

Die XML-Datei der ICD-10-Daten enthält weniger Information als erhofft. Die Priorität liegt daher
zunächst auf dem Aufbau der Datenbank, die KI-Antworten sind nachgelagert.
Es stellt sich die Frage, wie relevant eine Vektordatenbank wirklich ist.

Simon Hölzer präsentiert anschliessend einen eigenen Prototyp, den er mit Claude Code erstellt hat.
Der Prototyp demonstriert die Kernfunktionalität: semantische Suche sowie Verhaltensempfehlungen (US3).

Stefan Linder stösst zum Meeting dazu und präsentiert eine UI-Demo der bestehenden Plattform.

### Zusätzliche Anforderungen

- Bei einer Suche sollen fünf verwandte Vorschläge angezeigt werden
- Vergangene Suchanfragen werden in der Datenbank persistiert
- Erfahrungswert des Kunden: 200 Codes decken rund 90 % der realen Suchanfragen ab

## Beschlüsse

| Nr. | Beschluss | Verantwortlich |
|---|---|---|
| B1 | Datenbankaufbau hat Priorität gegenüber KI-Antworten in Iteration 2 | Team |
| B2 | Suche (DB) und KI-Dialog werden als getrennte Komponenten implementiert | Team |
| B3 | Bei einer Suchanfrage werden 5 verwandte Vorschläge angezeigt | Team |
| B4 | Vergangene Suchanfragen werden in der Datenbank persistiert (SEO-Seiten) | Team |
| B5 | Relevanz der Vektordatenbank wird im Rahmen von Iteration 2 evaluiert | Team |

## Nächster Termin

**[Datum]** – [Ort]

