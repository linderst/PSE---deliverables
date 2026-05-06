#!/usr/bin/env bash
# C2 - Follow-up Chat / Kontextueller Chat
# Stellt Folgefragen zu unterschiedlichen Diagnosen.
# Erwartung: Antworten unterscheiden sich kontextspezifisch.
#
# Usage:
#   bash scripts/contextual_demo.sh | tee logs/C2_run.log

set -euo pipefail

API="http://localhost:8000/api/chat/contextual"
HDR='Content-Type: application/json'

ask() {
  local id="$1" code="$2" title="$3" question="$4"
  echo "----- ${id} -----"
  echo "condition_code: ${code}"
  echo "condition_title: ${title}"
  echo "question: ${question}"
  local body
  body=$(python3 -c "import json,sys; print(json.dumps({'condition_code':'${code}','condition_title':'${title}','question':'${question}'}))")
  curl -s -X POST "$API" -H "$HDR" -d "$body" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("antwort:"); print(d.get("answer",""))'
  echo ""
}

ask C2.1 "E11.9" "Diabetes mellitus, Typ 2" "Darf ich Sport machen?"
ask C2.2 "I10"   "Essentielle Hypertonie"    "Darf ich Sport machen?"
ask C2.3 "E11.9" "Diabetes mellitus, Typ 2" "Ist das ansteckend?"
ask C2.4 "J45"   "Asthma bronchiale"         "Welche Medikamente helfen typischerweise?"
