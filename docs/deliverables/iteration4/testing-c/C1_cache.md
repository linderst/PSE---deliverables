# C1: Cache-Tests

Der Cache soll verhindern, dass wir die teuren LLM-Anfragen mehrfach absetzen, wenn derselbe ICD-Code mit demselben Endpoint schon einmal beantwortet wurde. Dafür rufen wir jeden Code zweimal kurz hintereinander auf und schauen, ob der zweite Aufruf wirklich aus dem Cache kommt. Als Beleg dienen uns zwei Dinge: die Antwortzeit und die Marker `[cache-miss] saved` und `Cache hit:` im Backend-Log.

Vor dem Lauf leeren wir den Cache:

```bash
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" \
  -c "DELETE FROM icd_ai_cache;"
```

Danach starten wir das Skript:

```bash
bash scripts/cache_demo.sh | tee logs/C1_run.log
```

## Tests

```
Testname: C1.1 Erst- und Zweitaufruf I10 (explain)
Input: POST /api/chat/explain {"question": "I10: Essentielle Hypertonie"}, zweimal hintereinander
Erwartetes Verhalten: Der erste Aufruf geht ans LLM (mehrere Sekunden Antwortzeit),
                      der zweite kommt aus dem Cache (unter 100 ms).
                      Im Backend-Log erscheint zuerst "[cache-miss] saved explain for I10",
                      danach "Cache hit: returned explain for I10".
Tatsächliches Verhalten: 1. Aufruf 3874 ms, 2. Aufruf 47 ms. Beide Marker stehen im Log.
Ergebnis: bestanden
```

```
Testname: C1.2 Erst- und Zweitaufruf J45 (explain)
Input: POST /api/chat/explain {"question": "J45: Asthma bronchiale"}, zweimal
Erwartetes Verhalten: Erster Aufruf langsam (LLM), zweiter Aufruf schnell (Cache).
                      Beide Log-Marker tauchen auf.
Tatsächliches Verhalten: 1. Aufruf 3167 ms, 2. Aufruf 51 ms. Marker im Log vorhanden.
Ergebnis: bestanden
```

```
Testname: C1.3 Erst- und Zweitaufruf E11 (explain)
Input: POST /api/chat/explain {"question": "E11: Diabetes mellitus, Typ 2"}, zweimal
Erwartetes Verhalten: Gleicher Verlauf wie bei C1.1 und C1.2.
Tatsächliches Verhalten: 1. Aufruf 6769 ms, 2. Aufruf 55 ms. Marker im Log vorhanden.
Ergebnis: bestanden
```

```
Testname: C1.4 Schlüssel-Trennung pro Endpoint (E11 specialist)
Input: POST /api/chat/specialist {"question": "E11: Diabetes mellitus, Typ 2"}, zweimal
Erwartetes Verhalten: Der Cache-Schlüssel besteht aus (icd_code, prompt_type).
                      Auch wenn E11/explain aus C1.3 schon gecacht ist, soll
                      E11/specialist beim ersten Aufruf trotzdem ans LLM gehen
                      und erst beim zweiten aus dem Cache kommen.
Tatsächliches Verhalten: 1. Aufruf 4912 ms, 2. Aufruf 51 ms. Im Log "[cache-miss] saved
                         specialist for E11" gefolgt von "Cache hit: returned specialist for E11".
Ergebnis: bestanden
```

## Cache-Übersicht (wie im Testkonzept verlangt)

```
ICD Code              | LLM Call | Cache verwendet
I10 (1. Aufruf)       | Ja       | Nein
I10 (2. Aufruf)       | Nein     | Ja
J45 (1. Aufruf)       | Ja       | Nein
J45 (2. Aufruf)       | Nein     | Ja
E11 (1. Aufruf)       | Ja       | Nein
E11 (2. Aufruf)       | Nein     | Ja
E11 specialist (1.)   | Ja       | Nein
E11 specialist (2.)   | Nein     | Ja
```

## Was uns bei den Antwortzeiten aufgefallen ist

Die Erstaufrufe brauchen drei bis sieben Sekunden, die Zweitaufrufe stabil unter 60 ms. Das ist ein Speed-up von rund Faktor sechzig bis hundert. Für identische Anfragen löst das System keine zusätzlichen LLM-Calls mehr aus. Das sieht man auch direkt am Backend-Log.

## Cache-Inhalt nach dem Lauf

```
 icd_code | prompt_type | created_at
----------+-------------+----------------------------
 E11      | explain     | 2026-05-04 08:41:46
 E11      | specialist  | 2026-05-04 08:41:52
 I10      | explain     | 2026-05-04 08:40:26
 J45      | explain     | 2026-05-04 08:40:30
```

## Logs

- `logs/C1_run.log`: Skript-Output mit Antwortzeiten
- `logs/C1_backend.log`: Backend-Marker `[cache-miss] saved` und `Cache hit:`
