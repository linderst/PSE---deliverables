# C5: Usability-Tests

Im Testkonzept wird verlangt, dass mindestens zwei Personen ohne medizinisches Fachwissen die Anwendung benutzen und die Verständlichkeit, die Bedienbarkeit und die Geschwindigkeit subjektiv bewerten. Das lässt sich nicht automatisieren, denn die Personen müssen wirklich am Gerät sitzen und dabei laut denken.

Diese Datei nutzen wir als Vorlage und füllen sie während des Tests live aus.

## Setup pro Person (rund 15 Minuten)

1. Browser auf `http://localhost:5173` offen, Stack läuft.
2. Bildschirmaufnahme starten: `Cmd + Shift + 5`, Speicherort `C5_recordings/<person>.mov`.
3. Briefing vorlesen, ohne Lösungshinweise zu geben:
   > Du testest eine Webseite, die medizinische Diagnosen erklärt. Bitte löse die folgenden drei Aufgaben und sage währenddessen laut, was du denkst und tust.
4. Die drei Aufgaben in der vorgegebenen Reihenfolge durchgehen lassen.
5. Anschliessend den Likert-Fragebogen ausfüllen lassen und die zwei offenen Fragen stellen.

## Aufgaben (aus Testkonzept 8.2)

```
Testname: U1 Bedeutung von E11.9 herausfinden
Input: "Finde heraus, was E11.9 bedeutet."
Erwartetes Verhalten: Die Person tippt E11.9 ins Suchfeld, öffnet das Ergebnis
                      und liest die Erklärung. Time-to-Success unter 60 s.
Tatsächliches Verhalten:
  Person 1 (Person A): 7 s bis zum Ergebnis, Antwort verstanden. Sie hat
                       versucht, auf den Block "Wer behandelt das?" zu klicken,
                       weil sie dort einen weiterführenden Link erwartet hat.
  Person 2 (Person B): hat "was bedeutet e11.9" als ganzen Satz ins Suchfeld
                       eingegeben. Statt eines Treffers erschien die Meldung
                       "Fehler bei der Suche. Bitte erneut versuchen.".
                       Person 2 hat die Aufgabe nicht gelöst, weil ihr nicht
                       klar war, dass nur der nackte Code eingegeben werden
                       darf. Damit zeigt sich derselbe Bug wie in C3.3, C3.4
                       und U2: Sobald eine Eingabe nicht direkt auf einen
                       ICD-Code passt, liefert das System einen harten Fehler
                       statt einer leeren Trefferliste oder eines
                       LLM-Refinements.
Ergebnis: P1 bestanden, P2 nicht bestanden
```

```
Testname: U2 Lumboischialgie suchen
Input: "Suche nach Lumboischialgie und finde den dazugehörigen Code."
Erwartetes Verhalten: Die Person tippt Lumboischialgie ein, findet M54 oder M54.4
                      in den Treffern und kann den Code benennen.
Tatsächliches Verhalten:
  Person 1 (Person A): hat "Lumboischialgie welcher code" eingegeben.
                       Antwort vom System: "Fehler bei der Suche. Bitte erneut
                       versuchen." Sie hat nach 7 s aufgegeben. Wir vermuten
                       hier einen Bug: eine Mehrwort-Query mit Stichwort und
                       Frage löst einen harten Fehler aus, statt ein
                       Suchergebnis oder eine leere Trefferliste zu liefern.
  Person 2 (Person B): hat "Lumboischalgie" (mit Tippfehler, ohne "i" nach
                       "sch") eingegeben. Antwort vom System: "Fehler bei der
                       Suche. Bitte erneut versuchen." Person 2 hat die
                       Aufgabe nicht gelöst. Damit ist der Bug aus U1 und C3
                       reproduzierbar: Sobald die Eingabe nicht exakt auf
                       einen vorhandenen ICD-Code oder Bezeichner passt
                       (sei es durch einen Tippfehler oder durch eine als
                       Frage formulierte Suche), liefert das System einen
                       harten Fehler. Eine fehlertolerante Suche oder ein
                       LLM-Refinement, wie es das Testkonzept (Abschnitt 6.3)
                       in Aussicht stellt, greift hier nicht.
Ergebnis: P1 nicht bestanden, P2 nicht bestanden
```

```
Testname: U3 Behandlung von Diabetes verstehen
Input: "Finde heraus, wie Diabetes typischerweise behandelt wird."
Erwartetes Verhalten: Die Person sucht nach Diabetes, öffnet einen Diabetes-Eintrag,
                      stellt im Chat eine Folgefrage zur Behandlung und kann den
                      Inhalt knapp wiedergeben.
Tatsächliches Verhalten:
  Person 1 (Person A): nach 9 s war das Ergebnis sichtbar, weitere 3 s zum Lesen.
                       Die Erklärung war ausreichend, eine Folgefrage im Chat war
                       nicht nötig.
  Person 2 (Person B): rund 38 s bis zur erfolgreichen Lösung. Person 2 hat
                       zuerst nach Diabetes gesucht, das Ergebnis geöffnet und
                       den Block "Wie wird behandelt?" gelesen. Weil ihr die
                       Erklärung zu lang war, hat sie zusätzlich eine
                       Folgefrage im Chat gestellt und über die kürzere
                       Chat-Antwort die Behandlung knapp wiedergeben können.
                       Damit hat Person 2 - im Gegensatz zu Person 1 - den
                       Chat tatsächlich genutzt; die Folgefrage-Funktion war
                       hier wertvoll.
Ergebnis: P1 bestanden, P2 bestanden
```

## Likert-Fragebogen

Skala 1 bis 5: 1 = stimme gar nicht zu, 5 = stimme voll zu.

| Aussage | P1 | P2 |
|---|---|---|
| Die Erklärungen waren verständlich. | 4 | 5 |
| Die Anwendung war angenehm zu bedienen. | 5 | 4 |
| Die Antworten kamen schnell genug. | 5 | 5 |
| Ich hatte Vertrauen in die angezeigten Informationen. | 3 | 5 |
| Ich würde die Anwendung wieder benutzen. | 5 | 5 |

## Offene Fragen

1. Was hat dich am meisten verwirrt?
   - Person A: dass man erst später Fragen stellen kann (der Chat ist erst nach
     der Auswahl einer Diagnose verfügbar).
   - Person B: dass so oft die Meldung "Fehler bei der Suche" kam und nicht
     ersichtlich war, was an der eigenen Eingabe falsch gewesen sein soll.
2. Was hat dir am besten gefallen, und was würdest du verändern?
   - Person A: am besten gefallen hat ihr die übersichtliche, einfach gehaltene
     Webseite. Verändern würde sie die Personalisierung der Ergebnisse.
   - Person B: am besten gefallen hat ihr das Design. Verändern würde sie die
     Fehlerbehandlung der Suche, sodass klar wird, was an der Eingabe nicht
     gepasst hat oder dass die Suche auch frei formulierte Eingaben verstehen
     sollte.

## Beobachtungsprotokoll pro Person

```
Person:                    P1 (Person A)
Alter ungefähr:            25
Technische Affinität:      3 / 5
Medizinischer Hintergrund: nein
Datum:                     04.05.2026

Auffälligkeiten:           U1: hat versucht, auf den Block "Wer behandelt das?"
                           zu klicken und dort einen weiterführenden Link erwartet.
                           U2: hat "Lumboischialgie welcher code" eingegeben,
                           das System hat einen harten Fehler statt einer
                           Trefferliste geliefert, die Aufgabe wurde abgebrochen.
                           Wunsch: Chat-Funktion früher zugänglich machen,
                           personalisiertere Ergebnisse anbieten.
```

```
Person:                    P2 (Person B)
Alter ungefähr:            60
Technische Affinität:      4 / 5
Medizinischer Hintergrund: nein
Datum:                     06.05.2026

Auffälligkeiten:           U1: hat "was bedeutet e11.9" als ganzen Satz
                           eingegeben und damit den Suchfehler ausgelöst,
                           Aufgabe nicht gelöst.
                           U2: hat "Lumboischalgie" mit Tippfehler eingegeben
                           und denselben Fehler erhalten, Aufgabe nicht gelöst.
                           U3: hat über die Diagnose-Suche und eine Folgefrage
                           im Chat nach 38 s zum Ziel gefunden, weil ihr der
                           "Wie wird behandelt?"-Block zu lang war.
                           Wunsch: deutlich klarere Fehlermeldungen oder eine
                           tolerantere Suche, die auch frei formulierte
                           Eingaben verarbeiten kann.
```

## Zusammenfassung der Befunde

Bestanden: U1 P1, U3 P1, U3 P2.
Nicht bestanden: U1 P2, U2 P1, U2 P2.

Beide Personen sind mindestens einmal in denselben Bug gelaufen, der bereits in
C3.3 und C3.4 dokumentiert ist: Sobald die Suchanfrage nicht exakt einem
ICD-Code oder einer korrekt geschriebenen Diagnose entspricht, antwortet das
System mit "Fehler bei der Suche. Bitte erneut versuchen." Drei verschiedene
Eingabearten lösen dasselbe Problem aus:

- "Lumboischialgie welcher code" (P1, Mehrwort-Frage)
- "was bedeutet e11.9" (P2, natürlich-sprachliche Frage mit gültigem Code)
- "Lumboischalgie" (P2, einzelnes Wort mit Tippfehler)

Ein Mensch, der die Anwendung zum ersten Mal benutzt, weiss nicht, in welcher
Form die Eingabe erwartet wird. Beide Personen haben in der offenen Befragung
genau diesen Punkt aufgegriffen (P1 wünscht Personalisierung,
P2 wünscht eine klarere Fehlermeldung bzw. eine tolerantere Suche).

Auf der positiven Seite: Beide Personen finden die Anwendung verständlich,
schnell und würden sie wieder benutzen (P1 4-5-5-3-5, P2 5-4-5-5-5). Das
Vertrauen in die Informationen ist bei P2 deutlich höher (5) als bei P1 (3),
was wir als Zufallsbefund bei nur zwei Testpersonen werten.

Folgerung: Die fehlertolerante Suche bzw. das Mapping von Mehrwort-/
Tippfehler-/Frage-Eingaben auf passende ICD-Codes ist die mit Abstand
wichtigste Usability-Verbesserung vor der Auslieferung. Alles andere
funktioniert gut genug.

## Bildschirmaufnahmen

Die Aufnahmen liegen auf Youtube.

| Person | Datei                        | YouTube-Link                       |
|--------|------------------------------|------------------------------------|
| P1     | C5_recordings/P1.mov         | https://youtu.be/t_QF7qvh8yo       |
| P1     | C5_recordings/P1_part2.mov   | https://youtu.be/Ju5mqwBDV6k       |
| P1     | C5_recordings/P1_part3.mov   | https://youtu.be/nd2YUDBUjnk       |
| P2     | C5_recordings/P2.mov         | https://youtu.be/btdeTzq2CwM       |
| P2     | C5_recordings/P2_part2.mov   | https://youtu.be/ueSgDQLEuZk       |
| P2     | C5_recordings/P2_part3.mov   | https://youtu.be/oOcL5bi1xtw       |
