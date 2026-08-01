# Design Review Checklist

> Use during the design and PR review of any chapter or case study. Each item should be
> answerable with evidence (a section, diagram, or sentence in the design).

## Scope & requirements
- [ ] Problem statement present and scoped (in/out).
- [ ] Functional requirements enumerated.
- [ ] Non-functional requirements quantified (availability, latency p99, durability).
- [ ] Explicit assumptions listed and tagged [constraint]/[assumption].
- [ ] Read:write ratio stated.

## Estimation
- [ ] RPS, storage, bandwidth arithmetic shown.
- [ ] Peak multiplier assumed (not just average).
- [ ] Metadata/index sizes included.
- [ ] Binding resource identified.

## Architecture
- [ ] High-level diagram (context/components) is original Mermaid.
- [ ] Each component has a single stated responsibility.
- [ ] Storage(s) chosen with reasons; alternatives rejected.
- [ ] Caching strategy: what/where/TTL/invalidation/stampede.
- [ ] Partitioning strategy and hot-key handling.
- [ ] Replication topology and sync/async rationale.

## Consistency & transactions
- [ ] Consistency model stated and justified for users.
- [ ] Idempotency and deduplication addressed for writes.
- [ ] Distributed-transaction approach (if cross-service) chosen.

## Reliability & failure
- [ ] Failure scenarios enumerated with system responses.
- [ ] Failover, backpressure, graceful degradation described.
- [ ] SLI/SLO and error budget stated.
- [ ] No unaddressed single point of failure on the hot path.

## Security
- [ ] AuthN/AuthZ model described.
- [ ] Encryption in transit and at rest noted.
- [ ] Input validation and tenant isolation addressed.

## Observability
- [ ] Golden signals metrics listed.
- [ ] Logging, tracing, correlation IDs addressed.
- [ ] Alerting and dashboards sketched.

## Trade-offs & alternatives
- [ ] Trade-off table present (chosen vs rejected with reasons).
- [ ] At least one alternative design offered.
- [ ] ""When NOT to use this"" addressed.

## Navigation & quality
- [ ] Examples, common mistakes, review questions present.
- [ ] Previous/Next links present.
- [ ] Further reading cites SOURCES.md IDs.
