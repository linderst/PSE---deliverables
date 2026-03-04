# Protokoll – Teamsitzung; Weiteres Vorgehen

**Datum:** 4. März 2026  
**Zeit:** 15:00 - 16:30  
**Ort:** ExWi PC-Pool 
**Sitzungsleitung:** -  
**Protokoll:** Dennis

## Anwesende

Felix, Alex, Julien, Christian, entschuldigt: Dennis

## Protokoll

### 1 – ICD-10-Code Klassifizierung
* Alex zeigt ICD-10-Code Klassifizierung und Idee, welche verwandte Codes gezeigt werden sollen.
* Er möchte auf pgvector verzichten und einen direkteren Weg mit LLM einschlagen.
* Diskussion über wie wenig die ICD-10 XML-Datei an Daten enthält, die weiterverarbeitet werden koennen.
* Stellt sich die Frage, wie sinnvoll es ist diese zu verwenden.

### 2 – Priorisierung
Juliens Ansicht, welche Prios wir haben in welcher Reihenfolge:
1. Funktioniert (Sinnvoll)
2. Schnelligkeit
3. Genauigkeit

### 3 – User Stories
* Es wurden nochmals die User Stories angeschaut, da Anforderungen wer die Webseite benutzt nicht klar war.
* Wir gehen davon aus, dass ein Patient einen Bericht/Diagnose hat, worauf er dann unsere Webseite besuchen wuerde.

### 5 – Idee pgvector Datenbank als Constraint
* Idee die Klassifizierung zu benutzen, um der Webseite Struktur zu verleihen (schnelles Springen zwischen Hierarchien).
* pgvector nur als Basis für Constraint, bevor API Call an Gemini geschickt wird (kosteneffizienter und schneller).

## Beschlüsse
* Alex macht die Deliverables noch heute.
* Wir arbeiten an Iteration weiter mit pgvector.

## Aufgabenverteilung
| Aufgabenbereich | Personen |
|---|---|
| Backend: Datenbank | Felix und Christian |
| Frontend: Website | Alex |
| Frontend–Backend Schnittstelle (Pointer Comparison) Vektoren | Julien |
| API-Schnittstelle | Dennis (neu) |
| Promptengineering | (Stefan) – muessen ihn noch fragen (neu) |

## Offene Punkte
* Stefan wegen Promptengineering fragen
* Klären ob nächster Termin besser online durchgeführt wird

## Naechster Termin
* 11. März 2026 - 18:00 Uhr in Bern
