# Latency-Budget Template

> Break a user-facing SLO into a budget distributed across the call path. The total must fit
> inside the SLO; over-allocating any segment blows the budget.

## SLO
Target end-to-end p99 latency = ____ ms

## Budget allocation (example proportions; tune to your system)
| Segment | Budget (ms) | Notes |
|---------|:-----------:|-------|
| Network (client→edge) | | RTT, TLS |
| Edge / CDN | | cache hit/miss path |
| API gateway | | auth, rate-limit, routing |
| Service compute | | business logic |
| Cache lookup | | distributed cache hop |
| Database / downstream | | query + replication lag |
| Serialization / transfer | | payload size |
| **Total** | | must ≤ SLO |

## Rules
1. Budgets are percentiles, not averages; the slowest 1% must fit.
2. A single slow dependency consumes many budgets; set per-call timeouts summing below the
   end-to-end budget.
3. Leave headroom (e.g., budget to ~80% of SLO) for jitter and load spikes.
4. Measure each segment at p99 independently; redistribute when one overruns.

## Timeout cascade
Set downstream timeouts so their sum < end-to-end budget minus compute and transfer:
`Σ(downstream timeouts) < SLO − (gateway + compute + transfer)`

## Worked mini-example
- SLO p99 = 300 ms; reserve 60 ms headroom → 240 ms working budget.
- gateway 20, compute 40, cache 10, DB 60, transfer 10 → 140 ms used; 100 ms slack for
  retries/replication lag.
