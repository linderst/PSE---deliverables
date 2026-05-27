
# Protokoll – Kundenmeeting 

**Datum:** [15. April 2026]  
**Zeit:** [11:00 – 12:00 Uhr]  
**Ort:** [Länggassstrasse 31]  
**Sitzungsleitung:** [Julien / Dennis]  
**Protokoll:** [Julien / Dennis]

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
| Sergej Weinstein | Informatiker, Medcode GmbH  |x|


"x" - **anwesend**  
"-" - **entschuldigt abwesend**  
## Traktanden

| Nr. | Traktandum | Wer
|---|---|---| 
| 1 | Begrüssung | Alle |
| 2 | Demo Iteration 3 (Deployment med.qm1.ch) | Stefan / Alex |
| 3 | Besprechung Demo & Kundenfeedback | Julien |
| 4 | Stand SEO & URL-Struktur / Landingpage | Stefan |
| 5 | Stand Parallelisierung, Testing & Dokumentation | Julien / Christian / Dennis / Felix |
| 6 | Abschluss & nächste Schritte | Felix |

### 1 – [Begrüssung]

Kurze Begrüssung und Überblick über die Traktanden.

### 2 – [Demo Iteration 3]

Heute morgen hat Sergey die aktuellste Version (vom Sonntag 12.04.26) deployed.

Sergej hat angeboten, dass wir Zugriff auf den Server erhalten für das Deployment.
In Zukunft wird weiterhin Sergej das Deployment machen.
Hinweis: Server ist nicht der schnellste. Lokales Embedding sollte jedoch möglich sein.

Demonstration des aktuellen Stands der WebApp: Funktioniert grundlegend.

Schwerpunkte der Demo:
- Live-Deployment auf dem Server 
- Backend-Refactoring (main.py aufgeteilt in routers, models, services)
- Frontend-Anpassungen und Verbesserungen


### 3 – [Besprechung Demo & Kundenfeedback]

Kunde gibt Rückmeldung zur Demo und zum aktuellen Entwicklungsstand.

Leitfragen:
- Entspricht der aktuelle Stand den Erwartungen aus dem letzten Meeting (25.3.)?
- Wie beurteilt der Kunde Suchqualität und Benutzeroberfläche?
- Welche Anpassungen oder Ergänzungen gibt von Seite Kunde?

Feedback von Sergej und Simon:
- Deployment-Anleitung hat gut funktioniert und war verständlich.
- Chat-Funktion bekommt nicht den gesamten Kontext des Chatverlaufs, sollte so bleiben
- Ratelimiting einführen pro Benutzer (IP) oder auf andere Art und Weise in WebApp


Weiteres Vorgehen:
- Ein Fallback falls Gemini API überlastet ist
    - Alle Teammitglieder sollten für sich testen und weitere fehlende Fallbacks identifizieren


### 4 – [Stand SEO & URL-Struktur / Landingpage]

Bericht zum Umsetzungsstand der am 25.3. beschlossenen SEO-Massnahmen:

- URL-Struktur (z. B. `/diabetes`): Status
- Sitemap: Status
- Statische Landingpage mit gebündelten Suchbegriffen: Status
- Neuer Button mit Verweis auf extradoc.ch ist hinzugefügt worden

Wurde von Stefan demonstriert.

### 5 – [Stand Parallelisierung, Testing & Dokumentation]

Kurzberichte der zuständigen Teammitglieder:

**Parallelisierung** (Julien): Stand des separaten Branches, bisherige Implementierung, nächste Schritte.

**Testing** (Christian): Überarbeitetes Testkonzept (V2) liegt vor. Aktueller Stand der Testdurchführung.

**Dokumentation** (Dennis / Felix / Alex): Aktueller Stand der Frontend- und Backend-Dokumentation, Benutzerhandbuch, README.

### 6 - Externe Projekte

Simon Hölzer ist in Kontakt mit Deutschen Firmen, die ähnliche Projekte durchführen. (Bspw washabich.de)

Vorschlag von Simon:
- QR-Codes auf Patientenbriefe integrieren, die auf medcode verweisen
- Benötigt hierfür eine Kontaktperson aus unserem Termin; Julien/Felix haben sich freiwillig gemeldet.

### 6 – [Abschluss & nächste Schritte]

Zusammenfassung der Beschlüsse. Festhalten offener Punkte. Verabschiedung.

## Beschlussprotokoll

- [Beschluss] 
- Ratelimiting einführen (bspw. Error 503)
- Weitere Fallbacks einführen
- Weiteres Finetuning 
- Weiteres Feedback im Verlaufe der Woche von Simon
- Julien Chopin steht Simon bei für externe Projekte

## Offene Punkte

- [ ] [Aufgabe] 
- [ ] Ratelimiting einführen pro Benutzer (IP) oder auf andere Art und Weise
- [ ] Abklären, ob wir Zugriff auf Server benötigen 

## Nächster Termin

**12. Mai 2026** – [Länggassstrasse 31]
