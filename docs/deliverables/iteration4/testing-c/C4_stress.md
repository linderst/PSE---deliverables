# C4: Stress-Tests

Im Testkonzept wird verlangt, dass wir die Antwortzeiten und das Systemverhalten unter mehreren gleichzeitigen Benutzern prüfen. Uns interessieren dabei zwei realistische Extremfälle: der Best-Case, in dem alle Anfragen den Cache treffen, und der Worst-Case, in dem alle Anfragen ans LLM gehen. Beides testen wir mithilfe k6.

k6 ist ein Open-Source-Tool für Last- und Performance-Tests. Wir beschreiben in einem kurzen JavaScript-Skript, welche HTTP-Anfrage gestellt werden soll, wie viele virtuelle Benutzer (VUs) gleichzeitig laufen und wie lange. k6 führt das aus und liefert am Ende Kennzahlen wie die Anzahl der Iterationen, die Fehlerrate und die Antwortzeiten (Durchschnitt, Median, p95, max). Zusätzlich kann man Schwellen (Thresholds) setzen, zum Beispiel "p95 unter 200 ms" oder "Fehlerrate unter 1 %", die der Lauf bestehen muss.

```bash
brew install k6   # einmalig
docker compose up -d
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "DELETE FROM icd_ai_cache;"
curl -s -X POST http://localhost:8000/api/chat/explain \
     -H 'Content-Type: application/json' \
     -d '{"question":"E11: Diabetes mellitus, Typ 2"}' >/dev/null   # E11 "vorwärmen" für C4.1
k6 run --summary-export=C4_results/C4_1.json scripts/cache_hit.k6.js
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" \
     -c "DELETE FROM icd_ai_cache WHERE icd_code IN ('A09','B34','F32','G43','H10','K21','L20','M54','N39','R51');"
k6 run --summary-export=C4_results/C4_2.json scripts/cold_mix.k6.js
```

## Tests

```
Testname: C4.1 Cache-Hit-Last
Input: 20 virtuelle Benutzer, 60 s, alle stellen wiederholt dieselbe Anfrage
       POST /api/chat/explain {"question": "E11: Diabetes mellitus, Typ 2"}.
       Der Cache wurde vorher einmal warm gerufen.
Erwartetes Verhalten: Die Antworten kommen aus dem Cache, keine LLM-Calls.
                      Fehlerrate unter 1 %, p95 unter 200 ms.
Tatsächliches Verhalten: 11'254 Iterationen, 0 Fehler, p95 = 20 ms,
                         avg = 6 ms, Throughput 187 req/s.
                         Beide k6-Schwellen (rate<0.01, p95<200ms) sind eingehalten.
Ergebnis: bestanden
```

```
Testname: C4.2 Cold-Mix-Last
Input: 5 virtuelle Benutzer, 60 s, rotierend über zehn ICD-Codes
       (A09, B34, F32, G43, H10, K21, L20, M54, N39, R51).
       Der Cache für diese Codes wurde vorher geleert.
Erwartetes Verhalten: Die ersten Treffer pro Code laufen über das LLM, alle
                      weiteren werden aus dem Cache bedient. Fehlerrate unter 5 %.
Tatsächliches Verhalten: 229 Iterationen, 0 Fehler, p50 = 4 ms,
                         p95 = 3.68 s, avg = 321 ms, max = 6.88 s.
                         Der niedrige p50 kommt daher, dass der Cache schon nach
                         den ersten zehn Anfragen für alle zehn Codes warm war,
                         spätere Anfragen treffen den Cache. Nach dem Lauf hatte
                         icd_ai_cache 11 Einträge (E11 vom Vorwärmen plus die zehn
                         Cold-Mix-Codes).
                         k6-Schwelle (rate<0.05) eingehalten.
Ergebnis: bestanden
```

## Performance

| Kennzahl | C4.1 (warm) | C4.2 (cold-mix) |
|---|---|---|
| Concurrency | 20 VUs | 5 VUs |
| Iterationen | 11'254 | 229 |
| Fehler | 0 | 0 |
| Durchschnittliche Antwortzeit | 6 ms | 321 ms |
| Median (p50) | 2 ms | 4 ms |
| p90 | 13 ms | 7 ms |
| p95 | 20 ms | 3680 ms |
| max | 186 ms | 6880 ms |
| Throughput | 187 req/s | 4 req/s |

## Wie sich das System unter Last verhält

Bei reiner Cache-Last bleibt das System stabil und sehr schnell, mit knapp 200 Anfragen pro Sekunde, keinem einzigen Fehler und einer p95 weit unter unserer Schwelle. Die Antwortzeit wird hier von der Datenbank bestimmt, das LLM kommt gar nicht ins Spiel.

Beim Cold-Mix-Szenario hängt die Antwortzeit vom LLM ab. Auch hier hatten wir keine Fehler, der Retry-Backoff in der LLM-Brücke wurde nicht ausgelöst. Die p95 liegt erwartungsgemäss hoch (rund 3.7 s), weil die ersten Anfragen pro Code immer durchs LLM gehen. Sobald der Cache greift, fallen die Folgeanfragen auf wenige Millisekunden, und der Median bleibt deshalb bei nur 4 ms.

Damit haben wir den im Testkonzept geforderten Spezialfall "Cache" aus Abschnitt 7.3 abgedeckt: Die erste Anfrage geht ans LLM, alle weiteren auf denselben Code werden aus dem Cache bedient.

## Logs

- `logs/C4_1.log`, `logs/C4_2.log`: k6-Konsolen-Output
- `C4_results/C4_1.json`, `C4_results/C4_2.json`: k6 Summary-Export
