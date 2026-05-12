[//]: # (this is a .md comment)

# Protokoll – [Abschlussmeeting & Übergabe]

**Datum:** [12. Mai 2026]  
**Zeit:** [16:30 – 17:30 Uhr]  
**Ort:** [Länggassstrasse 31]  
**Sitzungsleitung:** [Julien]  
**Protokoll:** [Julien]

## Teilnehmer

**Entwicklungsteam:**

| Name | Rolle | anwesend |
|---|---|---|
| Felix Buchmüller  | Key Account Manager       |x|
| Alexander Bot     | Master Tracker            |-|
| Stefan Linder     | Chief Deliverable Officer |-|
| Christian Gafner  | Quality Evangelist        |x|
| Dennis Roduner    | Leitung / Protokoll       |-|
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
| 1 | 5min | Begrüssung | Julien |
| 2 | 15min | Demo der finalen Updates | Christian |
| 3 | 10min | Letzte Änderungen / Abschlussstand | Felix |
| 4 | 10min | Weiterführendes & Zukunft | Felix |
| 5 | 15min | Übergabe & Dokumentation | Julien |
| 6 | 10min | Meeting mit deutscher Firma | Christian |
| 7 | 5min | Abschluss & gemeinsames Grillen | Julien |



### 1 – [Begrüssung]

Kurze Begrüssung und Überblick über das Abschlussmeeting.


### 2 – [Demo der finalen Updates]

Vorstellung der letzten implementierten Änderungen und finalen Features.

Fokus auf:
* Verbesserungen seit der letzten Iteration
* Benutzererfahrung
* Deployment / aktueller Stand
* Kurze Live-Demo


### 3 – [Letzte Änderungen / Abschlussstand]

Besprechung der finalen Anpassungen vor Projektabschluss.

Themen:
* Offene Punkte
* Letzte Fixes
* Aktueller Projektstatus
* Abschluss der Entwicklungsphase


### 4 – [Weiterführendes & Zukunft]

Diskussion möglicher zukünftiger Erweiterungen und Ideen.

Mögliche Themen:
* Weitere Optimierungen
* Skalierung
* Zusätzliche Features
* Wartung / Weiterentwicklung


### 5 – [Übergabe & Dokumentation]

Durchgehen der Dokumentation und Anleitung gemeinsam mit der Kundenseite.

Inhalte:
* Deployment-Anleitung
* Projektstruktur
* Wartung / Betrieb
* Zugriff und Verwaltung
* Übergabe relevanter Informationen


### 6 – [Meeting mit deutscher Firma]

Besprechung eines möglichen Meetings mit der deutschen Firma zusammen mit Alex und Julien.

Themen:
* Zusammenarbeit
* Präsentation des Projekts
* Mögliche nächste Schritte
* Termin


### 7 – [Abschluss & gemeinsames Grillen]

Offizieller Abschluss des Projekts.

Zusätzlich:
* Gemeinsames Grillen eine Woche nach Projektabschluss
* Organisation / Terminfindung


## Beschlussprotokoll

* Die finale Version der Plattform wurde erfolgreich vorgestellt und positiv bewertet.
* Die letzten Änderungen und Optimierungen wurden gemeinsam überprüft.
* Die Sitemap funktioniert grundsätzlich, jedoch wurden trotz 17 indexierter Seiten zwischenzeitlich 35 Seiten angezeigt, wovon nur 2 indexiert wurden.  
  Das Problem scheint nicht direkt an den einzelnen Seiten zu liegen.
* Die Sitemap wurde bereits dynamisch umgesetzt, ist jedoch aktuell auf dem produktiven Server noch nicht vollständig angepasst.
* Das Favicon wurde erfolgreich dynamisch integriert.
* Teile der Sitemap sind im Source-Code aktuell noch statisch hinterlegt und sollen entfernt bzw. vollständig dynamisiert werden.
* Ein Fehler bezüglich der Benennung „ICD-10-GM-2024“ wurde festgestellt. Die Bezeichnung soll auf „ICD-10“ angepasst werden.
* Das Thema Parallelität wurde nochmals kurz besprochen, jedoch wurde entschieden, dass dies aktuell keine Priorität hat.
* Verbesserungen beim Error Handling wurden angesprochen und sollen bei zukünftigen Erweiterungen berücksichtigt werden.
* Die Problematik bezüglich möglicher API-Overbookings besteht weiterhin, liegt jedoch ausserhalb des direkten Einflussbereichs des Teams.
* Werbung wurde testweise im Header integriert, führte jedoch zu einem 403-Fehler.
* Als mögliche Ursache wurde das fehlende bzw. problematische Privacy- und Ad-Consent-Handling identifiziert.
* Die Werbeintegration im Header wird deshalb vorerst wieder entfernt.
* Weitere offene Punkte und kleinere Verbesserungen wurden gesammelt und dokumentiert.
* Das Meeting mit Medcode und der deutschen Firma wurde auf Mi 15:00 Uhr terminiert (betrifft nur Julien).

### Offene Punkte

* Anpassung „ICD-10-GM-2024“ → „ICD-10“
* Vollständige Entfernung statischer Sitemap-Einträge im Source-Code
* Werbung und Ad-Consent wieder rausnehmen

## Beschluss

Als finale Schritte wurden festgelegt:

* Anpassung und Deployment der dynamischen Sitemap auf dem Server
* Bereinigung der verbleibenden statischen Sitemap-Einträge
* Korrektur der ICD-10-Bezeichnung
* Vorläufig kein weiterer Fokus auf Parallelisierung
* Dokumentation und Anleitung gelten als übergeben

## Nächster Termin

Zur Feier des Projektabschlusses werden zwei mögliche Termine für ein gemeinsames Treffen / Biertrinken vorgeschlagen:

* **[Datum 1 einfügen]** – [Ort einfügen]
* **[Datum 2 einfügen]** – [Ort einfügen]
