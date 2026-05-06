#!/usr/bin/env bash
# C1 - Cache-Tests
# Ruft jeden Code zweimal auf demselben Endpoint auf und misst die Antwortzeit.
# Erwartung: 1. Aufruf langsam (LLM), 2. Aufruf schnell (Cache).
#
# Usage:
#   bash scripts/cache_demo.sh | tee logs/C1_run.log
#
# Voraussetzungen:
#   - Stack läuft (docker compose up -d)
#   - Cache vorher leeren:
#       docker compose exec db psql -U $DB_USER -d $DB_NAME \
#         -c "DELETE FROM icd_ai_cache WHERE icd_code IN ('E11','I10','J45');"

set -euo pipefail

API="http://localhost:8000/api/chat"
HDR='Content-Type: application/json'

call() {
  local endpoint="$1"
  local question="$2"
  local label="$3"
  local body
  body=$(printf '{"question":"%s"}' "$question")
  local start end dur status
  start=$(python3 -c 'import time; print(time.time())')
  status=$(curl -s -o /tmp/resp.json -w '%{http_code}' \
            -X POST "$API/$endpoint" -H "$HDR" -d "$body")
  end=$(python3 -c 'import time; print(time.time())')
  dur=$(python3 -c "print(round(($end - $start) * 1000, 1))")
  local len
  len=$(python3 -c "import json; print(len(json.load(open('/tmp/resp.json')).get('answer','')))")
  echo "[${label}] endpoint=${endpoint} status=${status} dauer_ms=${dur} antwort_zeichen=${len}"
}

echo "=== C1.1: E11.9 explain (zwei Aufrufe) ==="
call explain "E11.9: Diabetes mellitus, Typ 2" "C1.1-1.Aufruf"
sleep 1
call explain "E11.9: Diabetes mellitus, Typ 2" "C1.1-2.Aufruf"

echo ""
echo "=== C1.2: I10 explain ==="
call explain "I10: Essentielle (primäre) Hypertonie" "C1.2-1.Aufruf"
sleep 1
call explain "I10: Essentielle (primäre) Hypertonie" "C1.2-2.Aufruf"

echo ""
echo "=== C1.3: J45 explain ==="
call explain "J45: Asthma bronchiale" "C1.3-1.Aufruf"
sleep 1
call explain "J45: Asthma bronchiale" "C1.3-2.Aufruf"

echo ""
echo "=== C1.4: E11.9 specialist (anderer prompt_type) ==="
call specialist "E11.9: Diabetes mellitus, Typ 2" "C1.4-1.Aufruf"
sleep 1
call specialist "E11.9: Diabetes mellitus, Typ 2" "C1.4-2.Aufruf"

echo ""
echo "Fertig. Backend-Log mit 'Cache hit:' und '[cache-miss] saved' parallel prüfen."
