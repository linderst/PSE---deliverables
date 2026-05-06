# C2: Folgefragen im Kontext-Chat

Beim Chat-Endpoint geben wir mit jeder Folgefrage die aktuell betrachtete Diagnose mit (`condition_code`, `condition_title`). Die Antwort soll sich nachweislich auf diese Diagnose beziehen und nicht generisch ausfallen. Wir prüfen das auf zwei Wegen: einmal mit drei verschiedenen Diagnosen und einmal mit derselben Frage zu zwei unterschiedlichen Diagnosen. Im zweiten Fall müssen sich die Antworten klar unterscheiden, sonst hätte der mitgegebene Kontext keine Wirkung.

```bash
bash scripts/contextual_demo.sh | tee logs/C2_run.log
```

## Tests

```
Testname: C2.1 Sport bei Diabetes Typ 2
Input: POST /api/chat/contextual
       {"condition_code":"E11.9","condition_title":"Diabetes mellitus, Typ 2",
        "question":"Darf ich Sport machen?"}
Erwartetes Verhalten: Die Antwort enthält diabetes-spezifische Stichworte
                      (Blutzucker, Insulin, Unterzuckerung, Belastung).
Tatsächliches Verhalten: Die Antwort spricht über die Blutzuckersenkung durch Bewegung,
                         das Risiko der Unterzuckerung bei Insulin, den Hinweis auf
                         Traubenzucker beim Sport und die Fusspflege.
Ergebnis: bestanden
```

```
Testname: C2.2 Sport bei Hypertonie (gleiche Frage, andere Diagnose)
Input: POST /api/chat/contextual
       {"condition_code":"I10","condition_title":"Essentielle Hypertonie",
        "question":"Darf ich Sport machen?"}
Erwartetes Verhalten: Die Antwort enthält blutdruck-spezifische Stichworte
                      (Blutdruck, Belastungs-EKG, Gefässe, moderate Ausdauer).
Tatsächliches Verhalten: Die Antwort behandelt die Blutdrucksenkung durch Ausdauer,
                         elastische Gefässe, Vorsicht beim Krafttraining
                         und die Empfehlung eines Belastungs-EKG.
Ergebnis: bestanden
```

```
Testname: C2.3 Asthma und Medikamente
Input: POST /api/chat/contextual
       {"condition_code":"J45","condition_title":"Asthma bronchiale",
        "question":"Welche Medikamente helfen typischerweise?"}
Erwartetes Verhalten: Die Antwort nennt Inhalations-Medikamente (Salbutamol bzw.
                      Reliever, inhalatives Cortison bzw. Controller).
Tatsächliches Verhalten: Die Antwort unterscheidet zwischen Bedarfsmedikamenten
                         (Salbutamol als Reliever) und Dauermedikamenten
                         (niedrig dosiertes inhalatives Cortison als Controller).
Ergebnis: bestanden
```

## Vergleich C2.1 gegen C2.2

Bei identischer Frage und unterschiedlicher Diagnose unterscheiden sich die Antworten nicht nur in den Stichworten, sondern auch in der Empfehlungslogik:

- C2.1 Diabetes: Schwerpunkt liegt auf Blutzucker, Insulin, Unterzuckerungsrisiko und Traubenzucker zum Mitnehmen.
- C2.2 Hypertonie: Schwerpunkt liegt auf Blutdruck, Gefässelastizität, Belastungs-EKG und Vorsicht beim Krafttraining.

Damit ist gezeigt, dass der mitgegebene Kontext die Antwort wirklich steuert.

Die kompletten Antworten liegen in `logs/C2_run.log`.
