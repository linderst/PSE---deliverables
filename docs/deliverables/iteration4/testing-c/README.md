# Testing Part C

In diesem Ordner sammeln wir die Tests aus dem Teil "Person C" des Testkonzepts. Konkret geht es um das Antwortverhalten des LLMs mit und ohne Cache, um Folgefragen im Chat, um die Bedienung im Frontend, um das Verhalten unter Last und um die Usability mit echten Personen.

## Voraussetzungen

- Docker ist gestartet: `docker compose up -d --build`
- In der `.env` ist ein gültiger `GEMINI_API_KEY` hinterlegt
- k6 ist installiert: `brew install k6`
- Frontend läuft auf `http://localhost:5173`, Backend auf `http://localhost:8000`

## Reihenfolge

1. C3 (GUI) zuerst, weil wir damit gleich sehen, ob das Setup grundsätzlich steht.
2. C1 (Cache): vorher den Cache leeren und jeden Code zweimal aufrufen.
3. C2 (Folgefragen): kann unabhängig laufen.
4. C4 (Stress): am besten nach C1, weil das Cache-Hit-Szenario einen warmen Cache braucht.
5. C5 (Usability): zum Schluss, mit zwei realen Testpersonen.

## Dateien

- `C1_cache.md`: Cache-Tests
- `C2_followup.md`: Folgefragen im Chat
- `C3_gui.md`: GUI-Tests
- `C4_stress.md`: Stress-Tests mit k6
- `C5_usability.md`: Usability-Tests
- `scripts/`: Bash-Skripte für C1 und C2, k6-Skripte für C4
- `logs/`: Roh-Output der Skript-Läufe
- `C3_screenshots/`: Browser-Screenshots zu C3
- `C4_results/`: k6-Summary-Exporte
- `C5_recordings/`: Bildschirmaufnahmen der Usability-Tests (nicht im Repo)
