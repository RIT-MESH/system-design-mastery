# Reliability Review Checklist

> Applied to every design and PR. Focuses on keeping the system dependable under failure and
> overload.

## Objectives & budgets
- [ ] SLI(s) defined per user-visible journey.
- [ ] SLO targets set with error budgets.
- [ ] SLA (external) differentiated from SLO (internal) where relevant.

## Redundancy & topology
- [ ] No single point of failure on the hot path.
- [ ] Replication factor chosen with failure tolerance rationale (e.g., 3 to tolerate 1).
- [ ] Active-active vs active-passive chosen with region/zone reasoning.
- [ ] Failover tested (not just ""replicas exist"").

## Capacity & overload
- [ ] Sized for peak with headroom buffer (e.g., ~70% target utilization).
- [ ] Load shedding / throttling defined before overload collapses latency.
- [ ] Backpressure propagates to upstream callers.
- [ ] Queue-based load leveling for bursty writes.

## Failure containment
- [ ] Bulkheads isolate per-dependency/per-tenant resources.
- [ ] Circuit breakers wrap unreliable dependencies.
- [ ] Timeouts set on all outbound calls (no unbounded waits).
- [ ] Retries are bounded, jittered, and capped to avoid retry storms.
- [ ] Thundering-herd mitigation (jitter, request coalescing, warm-up).

## Resilience & recovery
- [ ] DR plan: RTO and RPO stated; backups/restores tested.
- [ ] Graceful shutdown drains in-flight work; brownouts considered.
- [ ] Chaos tests / game days planned for the top failure modes.
- [ ] Split-brain and partition behavior documented (Level 4 consistency choice).

## Operations
- [ ] Health/readiness/liveness probes defined and distinguishable.
- [ ] On-call runbooks exist for the top alerts.
- [ ] Postmortem workflow defined; blameless.
- [ ] Capacity and error-budget burn monitored with alerts.
