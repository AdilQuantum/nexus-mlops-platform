import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const predictionLatency = new Trend('prediction_latency_ms');

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // ramp up
    { duration: '1m',  target: 20 },  // sustained load
    { duration: '30s', target: 50 },  // spike
    { duration: '30s', target: 0 },   // ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    'errors':            ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8082';

export default function () {
  const payload = JSON.stringify({
    features: [
      Math.random() * 500,              // transaction_amount
      Math.floor(Math.random() * 24),   // transaction_hour
      Math.floor(Math.random() * 3650), // account_age_days
      Math.floor(Math.random() * 50),   // num_transactions_today
      Math.random() * 200,              // distance_from_home
    ],
  });

  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post(`${BASE_URL}/v1/predict`, payload, params);

  const ok = check(res, {
    'status 200':        (r) => r.status === 200,
    'has prediction':    (r) => r.json('prediction') !== undefined,
    'has confidence':    (r) => r.json('confidence') !== undefined,
    'latency < 500ms':   (r) => r.timings.duration < 500,
  });

  errorRate.add(!ok);
  predictionLatency.add(res.timings.duration);

  sleep(0.05);
}

export function handleSummary(data) {
  return {
    stdout: `
=== Nexus MLOps Load Test Results ===
Requests:     ${data.metrics.http_reqs.values.count}
Error rate:   ${(data.metrics.errors.values.rate * 100).toFixed(2)}%
p95 latency:  ${data.metrics.http_req_duration.values['p(95)'].toFixed(0)}ms
p99 latency:  ${data.metrics.http_req_duration.values['p(99)'].toFixed(0)}ms
Throughput:   ${data.metrics.http_reqs.values.rate.toFixed(1)} req/s
`,
  };
}
