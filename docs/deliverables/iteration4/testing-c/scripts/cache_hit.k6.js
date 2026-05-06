// C4.1 - Stress: Cache-Hit-Last
// 20 virtuelle User, 60s, immer derselbe Code (vorher 1x aufrufen, damit Cache warm ist).
//
// Run:
//   k6 run --out json=docs/deliverables/iteration4/testing-c/C4_results/C4_1.json \
//          docs/deliverables/iteration4/testing-c/scripts/cache_hit.k6.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '60s',
  thresholds: {
    'http_req_failed': ['rate<0.01'],
    'http_req_duration': ['p(95)<200'],
  },
};

export default function () {
  const payload = JSON.stringify({ question: 'E11: Diabetes mellitus, Typ 2' });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post('http://localhost:8000/api/chat/explain', payload, params);
  check(res, {
    'status 200': (r) => r.status === 200,
    'has answer': (r) => (r.json('answer') || '').length > 10,
  });
  sleep(0.1);
}
