# C3: GUI-Tests

Im Testkonzept (Abschnitt 6) wird verlangt, dass die wichtigsten Bedienflows im Browser sauber funktionieren: die Suche von der Landing-Page aus, eine weitere Suche ohne Reload, die Reaktion auf eine ungültige Eingabe und eine Folgefrage im Chat. Diese Tests führen wir manuell im Browser auf `http://localhost:5173` durch. Pro Test legen wir einen Screenshot in `C3_screenshots/` ab.

## Tests

```
Testname: C3.1 Suche von der Landing-Page
Input: Browser auf http://localhost:5173, ins Suchfeld klicken, "E11.9" eingeben, Enter
Erwartetes Verhalten: Der Treffer "E11 Diabetes mellitus, Typ 2" wird angezeigt
                      und die URL wechselt auf /diabetes-mellitus-typ-2/E11.
Tatsächliches Verhalten: Trefferkarte ist sichtbar, URL stimmt.
                         Screenshot: C3_screenshots/C3_1_landing_search.png
Ergebnis: bestanden
```

```
Testname: C3.2 Weitere Suche ohne Seiten-Reload
Input: Im laufenden SPA in das Suchfeld klicken, "Asthma" eingeben, Enter
Erwartetes Verhalten: Eine neue Trefferliste erscheint, ohne dass die Seite
                      komplett neu lädt; J45 ist Teil der Treffer.
Tatsächliches Verhalten: Die Trefferliste wird ausgetauscht, J45 Asthma bronchiale
                         steht in den Top-Treffern. Es gibt keinen Full-Reload
                         (man sieht den Loading-Indikator der SPA, keine weisse Seite).
                         Screenshot: C3_screenshots/C3_2_followup_search.png
Ergebnis: bestanden
```

```
Testname: C3.3 Ungültige Eingabe
Input: Suchfeld leeren, "xyzabc" eingeben, Enter
Erwartetes Verhalten: Die Anwendung zeigt eine Meldung, dass kein passender
                      ICD-Code gefunden wurde, und stürzt nicht ab.
Tatsächliches Verhalten: Statt der erwarteten "Keine passenden Treffer"-Meldung
                         erscheint die generische Fehlermeldung
                         "Fehler bei der Suche. Bitte erneut versuchen."
                         Die Anwendung stürzt zwar nicht ab und das Suchfeld
                         bleibt bedienbar, aber der Nutzer erhält keine
                         korrekte Rückmeldung darüber, dass schlicht kein
                         passender Code existiert. Damit ist das im
                         Testkonzept geforderte Verhalten nicht erfüllt.
                         Screenshot: C3_screenshots/C3_3_invalid_input.png
Ergebnis: nicht bestanden (Bug: Free-Text- bzw. Nichttreffer-Suche
          liefert harten Fehler statt leerer Trefferliste)
```

```
Testname: C3.4 Symptomsuche mit LLM-Refinement
Input: Suchfeld leeren, "pulsierende Kopfschmerzen mit Lichtempfindlichkeit"
       eingeben, Enter
Erwartetes Verhalten: Während der Suche wird ein Ladeindikator angezeigt;
                      das Ergebnis enthält Migräne (G43) und/oder
                      Kopfschmerzsyndrome (G44).
Tatsächliches Verhalten: Bei der Wiederholung des Tests am 06.05.2026 lieferte
                         die Symptomsuche keine Treffer, sondern die generische
                         Meldung "Fehler bei der Suche. Bitte erneut versuchen."
                         Die URL blieb auf der vorher geöffneten Diagnose-Seite
                         (/asthma-bronchiale/J45) stehen, es wurden weder G43
                         Migräne noch G44 Kopfschmerzsyndrome angezeigt.
                         Damit ist das LLM-Refinement im aktuellen Stand für
                         diese Art von Mehrwort-Symptomeingaben nicht
                         funktionsfähig.
                         Screenshot: C3_screenshots/C3_4_symptom_search.png
Ergebnis: nicht bestanden (Bug: Mehrwort-Symptomsuche löst harten Fehler aus,
          kein LLM-Refinement-Treffer; siehe auch C5 U2 mit "Lumboischialgie
          welcher code")
```

```
Testname: C3.5 Folgefrage im Chat
Input: Auf einer Diagnose-Detailseite (z. B. E11) im Chat eine Folgefrage
       zur Behandlung stellen ("Was sollte jetzt tun?")
Erwartetes Verhalten: Die Antwort erscheint in der Chatansicht; der Inhalt bezieht
                      sich auf die geöffnete Diagnose (Stichworte zu Blutzucker,
                      Diabetes-Schulung, Ernährung, Diabetes-Medikamenten).
Tatsächliches Verhalten: Die Antwort kommt nach kurzem Laden in der Chatansicht.
                         Sie enthält die Punkte Arztgespräch und Therapieplan
                         (Hausarzt, Diabetologe, Metformin), Patientenschulung
                         (Diabetes-Schulung) und Ernährungsanpassung
                         (Diät, weniger Zucker, Vollkorn, Gemüse). Die Antwort
                         bezieht sich klar auf die geöffnete Diagnose
                         "Diabetes mellitus, Typ 2".
                         Screenshot: C3_screenshots/C3_5_chat_followup.png
Ergebnis: bestanden
```

## Zusammenfassung

Bestanden: C3.1, C3.2, C3.5.
Nicht bestanden: C3.3 und C3.4. Beide laufen in denselben Bug — eine Suche, die
sich nicht direkt auf einen ICD-Code mappen lässt (sei es eine reine
Phantasie-Eingabe wie "xyzabc" oder eine Mehrwort-Symptomeingabe), liefert die
generische Meldung "Fehler bei der Suche. Bitte erneut versuchen." statt einer
leeren Trefferliste oder eines LLM-Refinement-Ergebnisses. Derselbe Bug ist auch
in C5 U2 (Person 1, "Lumboischialgie welcher code") aufgetreten und sollte vor
der Abgabe gefixt werden.