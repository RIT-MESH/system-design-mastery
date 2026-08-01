# Level 6 — Reliability & Resilience — Exercises

Practice problems keyed to the [06-reliability](../../docs/06-reliability/README.md) level.

## Estimation & reasoning drills

- 1. Set an SLO of 99.95% over 28 days; compute the error budget in minutes and a 2x/14d burn-rate alert.
- 2. Design a failover test for a region loss that proves RTO without taking users down.
- 3. A slow dependency cascades; show how a bulkhead + circuit breaker + load shedding contain it.

## Design prompts

- 4. A retry storm amplifies an outage. Give the three mitigations.
- 5. Mixing liveness and readiness causes unwanted restarts. Redesign the probes.

## What would break? / when NOT to use

- 6. Why shed load BEFORE overload collapses latency, not after?

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
