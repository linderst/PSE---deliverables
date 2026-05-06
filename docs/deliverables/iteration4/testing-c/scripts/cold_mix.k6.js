// C4.2 - Stress: Cold-Mix-Last
// 5 virtuelle User, 60s, rotierend über 10 Codes (bewirkt LLM-Calls).
// Achtung: Gemini Rate-Limits beachten. VU-Zahl bewusst klein.
//
// Run:
//   k6 run --out json=docs/deliverables/iteration4/testing-c/C4_results/C4_2.json \
//          docs/deliverables/iteration4/testing-c/scripts/cold_mix.k6.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '60s',
  thresholds: {
    'http_req_failed': ['rate<0.05'],
  },
};

const codes = [
  'A09: Sonstige und nicht näher bezeichnete Gastroenteritis',
  'B34: Virusinfektion nicht näher bezeichneter Lokalisation',
  'F32: Depressive Episode',
  'G43: Migräne',
  'H10: Konjunktivitis',
  'K21: Gastroösophageale Refluxkrankheit',
  'L20: Atopisches Ekzem',
  'M54: Rückenschmerzen',
  'N39: Sonstige Krankheiten des Harnsystems',
  'R51: Kopfschmerz',
];

export default function () {
  const code = codes[Math.floor(Math.random() * codes.length)];
  const payload = JSON.stringify({ question: code });
  const params = { headers: { 'Content-Type': 'application/json' }, timeout: '30s' };
  const res = http.post('http://localhost:8000/api/chat/explain', payload, params);
  check(res, {
    'status 200': (r) => r.status === 200,
  });
  sleep(1);
}
