# Protokoll – Erstes Kundengespräch Medcode

**Datum:** Montag, 23. Februar 2026  
**Zeit:** 12:30 – ca. 13:30 Uhr  
**Ort:** ExWi, Sidlerstrasse 5, 3012 Bern  
**Sitzungsleitung:** Dennis Roduner  
**Protokoll:** Dennis Roduner  
**Betreuer:** Raphael Keller (TA)

## Teilnehmende

**Entwicklungsteam:**

| Name | Rolle |
|---|---|
| Felix Buchmüller | Key Account Manager |
| Alexander Bot | Master Tracker |
| Stefan Linder | Chief Deliverable Officer *(entschuldigt abwesend)* |
| Christian Gafner | Quality Evangelist |
| Dennis Roduner | Sitzungsleitung / Protokoll |
| Julien Chopin | Sitzungsleitung / Protokoll *(entschuldigt abwesend)* |

**Kundenseite:**

| Name | Rolle |
|---|---|
| Stefan Vogt | Geschäftsführer, Medcode GmbH |
| Simon Hölzer | Arzt, Medcode GmbH |

---

## Traktanden

| Nr. | Zeit | Traktandum | Verantwortlich |
|---|---|---|---|
| 1 | 12:30 | Begrüssung und Vorstellung | Dennis |
| 2 | 12:35 | Projektrahmen und Rahmenbedingungen | Felix |
| 3 | 12:45 | Klärung der Projektanforderungen | Team / Medcode |
| 4 | 13:00 | Planning Game: Iteration 1 | Team / Medcode |
| 5 | 13:20 | Kommunikation und Organisation | Felix |
| 6 | 13:25 | Zusammenfassung und nächste Schritte | Dennis |

---

### Traktandum 2 – Projektrahmen und Rahmenbedingungen

- Ablauf des PSE: 4 Iterationen, Zeitplan bis Ende Mai 2026
- Iteration 1: ca. 2–3 Wochen (Enddatum: 11. März 2026)
- Rollen im Team erläutern: Key Account (Felix), Master Tracker (Alex), Chief Deliverable Officer (Stefan L.), Quality Evangelist (Christian), Sitzungsleitung/Protokoll (Dennis & Julien)
- Deliverables: wöchentliche Statusberichte, Risikoanalyse, Sitzungsprotokolle
- Überblick über alle 4 Iterationen: Grobe Vorstellung des Gesamtzeitplans (bis Ende Mai 2026) und Abstimmung mit dem Kunden, welche Schwerpunkte pro Iteration vorgesehen sind (z.B. Analyse & Setup → KI-Prototyp → Frontend → Validierung)

### Traktandum 3 – Klärung der Projektanforderungen

- Bestätigung: Eigenständige Web-Applikation (keine Kopie von medcode.ch)
- Fokus auf KI-generierten Content (User Stories 1–3), nicht auf ICD-10-Auszüge
- Technologie-Entscheidungen: Backend (FastAPI?), Datenbank (PostgreSQL/pgvector?), LLM (Gemini oder Claude?) und Bereitstellung API-Key
- Umgang mit ICD-10-Daten (Version 2026, Quellen von BfArM)
- UI-Vorstellungen des Kunden: Suchfeld, bisherige Abfragen, SEO-Indexierung
- Gemini-Prototyp als Referenz besprechen
- Andere offene Fragen
- Zielgruppen klären: Soll die App sowohl Laien als auch Fachpersonen bedienen? Umschaltung zwischen "einfacher Sprache" und "Fachsprache" (z.B. Toggle) oder einheitliche Darstellung?

### Traktandum 4 – Planning Game: Iteration 1

- Kunde formuliert und priorisiert Stories für Iteration 1
- Team schätzt Aufwand pro Story (ideale Personentage)
- Team nennt verfügbares Budget (Personentage bis 11. März)
- Gemeinsame Festlegung: Welche Stories werden in Iteration 1 umgesetzt?
- Ziel des Kunden: Funktionsfähiger, anpassbarer Prototyp

### Traktandum 5 – Kommunikation und Organisation

- Bevorzugter Kommunikationskanal mit dem Kunden (E-Mail, Telefon, etc.)
- Dokumentation: Alle Entscheidungen inkl. Begründung, auch KI-generierte Inhalte
- Repository: Zugang für den Kunden
- Nächster Termin: Regelmässige Meetings vereinbaren

### Traktandum 6 – Zusammenfassung und nächste Schritte

- Zusammenfassung der Beschlüsse
- Offene Punkte
- Verabschiedung

---

## Zur Vorbereitung Planning Game (an Medcode)

- Bitte bereiten Sie Ihre Wünsche und Prioritäten für die erste Iteration vor (als Stories formuliert).
- Welche User Stories haben in der ersten Iteration am meisten Priorität?
- Gibt es zusätzliche Anforderungen oder Einschränkungen, die wir noch nicht kennen?

**Referenz aus Projektskizze:**

- US 1: Als Patient möchte ich einen ICD-Code eingeben und eine Erklärung in "einfacher Sprache" erhalten.
- US 2: Als Nutzer möchte ich wissen, zu welchem Facharzt ich mit einer Diagnose gehen muss.
- US 3: Als Nutzer möchte ich Verhaltensregeln für meine bevorstehende Behandlung abfragen.
- US 4: Als Anwender möchte ich Begriffe über eine semantische Suche finden, auch ohne exakten Fachterminus.

---

## Beschlussprotokoll

### 1 – Begrüssung und Vorstellung

Das Projektteam und Simon Hölzer haben sich gegenseitig vorgestellt.

### 2 – Projektrahmen und Rahmenbedingungen

Alle Teamrollen wurden dem Kunden erläutert.

Für Iteration 1 (bis 11. März 2026) wird ein Prototyp entwickelt, der möglichst viele Ideen abbildet und als Spielwiese dient. Der Prototyp sollte voller Ideen sein ("packed with features").

Alle weiteren Iterationen wurden Simon Hölzer erläutert.

### 3 – Klärung der Projektanforderungen

**Zielgruppe:** Die Anwendung richtet sich nur an Patienten/Versicherungsnehmer. Es wird versucht diese Zielgruppe in Kunden für die Webseite extradoc.ch zu vermitteln.

**Vorgenerierte Inhalte:** Ziel: nicht abschliessende Antworten, Marketing = abschliessende Antworten → Verweis auf extradoc (echte Ärzte)

**Eigenständige Web-Applikation:** Die Applikation wird eigenständig entwickelt, keine Kopie von medcode.ch.

**Hosting:** Der Kunde (Medcode) stellt einen eigenen Server für das Hosting bereit.

**Performance:** KI verursacht Latenz, insbesondere bei viel Kontext. Schnelle Interaktionen sollen trotzdem möglich sein (z.B. vorgeschlagene Themen, alte Suchen). Vielleicht ist es auch sinnvoll vorgenerierten Inhalt zu speichern.

**ICD-Code-Logik:** 3-stellige Codes (z.B. B13) geben die Themenhöhe wieder; spezifischere Codes liefern detailliertere Informationen. Krankheiten können mehrere Codes gleichzeitig umfassen.

**Suche:** Medcode selbst verwendet Elasticsearch. Für unser Projekt wird PostgreSQL mit pgvector als Datenbank eingesetzt (Versuchsansatz). Kein supergesichertes Qualitätsprodukt, packed with features, sondern viele Ideen umsetzen.

**API-Keys:** Für die Zukunft wird Medcode API-Keys für Gemini bereitstellen. Vorerst verwendet das Entwicklungsteam eigene Keys.

**Darstellung der Inhalte:** Die Inhaltswiedergabe nach einer Suche ist dem Entwicklungsteam frei überlassen. Die Suchergebnisse müssen nicht wie bei medcode.ch als Katalogsuche/-darstellung aufgelistet werden.

Eigenständige Web-Applikation. Hosting (eigener Server bei Medcode).

### 4 – Planning Game: Iteration 1

Simon Hölzer gibt dem Team viel Freiheiten bei der Umsetzung. Das Ziel ist ein Prototyp, mit dem man spielen kann. Der Schwerpunkt liegt auf der Datenbank (Vektor-Prototyp). Bis Ende Iteration 1 sollen folgende Ergebnisse vorliegen: ein Landing-Page-Design, ein Datenbank-Vektor-Prototyp sowie eine LLM-generierte Abfrage.

### 5 – Kommunikation und Organisation

**Kommunikationskanal:** Weiterhin per E-Mail an info@medcode.ch oder direkt an Simon Hölzer.

**Dokumentation:** Es wird ein zentrales Dokument (Journal) geführt, in dem alle Schritte und Entscheidungen begründet festgehalten werden, inklusive KI-generierter Inhalte.

**Nächster Termin:** 11. März 2026. Treffpunkt wird ein Büro in der Längasse/Stadt sein; Stefan Vogt hat vorgeschlagen, das Meeting informell bei einem Bier abzuhalten.

### 6 – Zusammenfassung und nächste Schritte

Alle Beschlüsse wurden zusammengefasst. Die Sitzung wurde beendet.

---

## Nächster Termin

**11. März 2026** – Büro Längasse/Stadt
