# Case Study Template

> Copy this file into the appropriate `case-studies/<tier>/` directory, rename it to the
> system name (kebab-case), and fill in every section. **All** 30 sections are required.
> Numbers (traffic, storage, bandwidth) must be **original** to this case study — do not
> reuse another system's estimates verbatim. Diagrams must be original Mermaid.

<!--
Metadata
- Title: <System Name>
- Tier: beginner | intermediate | advanced | extreme
- Author:
- Status: draft | review | complete
-->

## 1. Problem statement
Describe, in 2–4 sentences, the real-world problem the system solves and for whom.

## 2. Scope
What is in scope and explicitly out of scope for this design (v1). List the boundaries that
prevent scope creep during the interview/real design.

## 3. Functional requirements
Bullet list of behaviors the system must support. Use ""the system shall"" phrasing.

## 4. Non-functional requirements
Quantified quality attributes: availability (e.g., 99.9%), latency (p99), durability,
throughput, geographic reach, security/compliance constraints.

## 5. Explicit assumptions
Numbered list of assumptions, each tagged [constraint] or [assumption]. State user counts,
usage patterns, data sizes, and retention explicitly.

## 6. Traffic estimation
Back-of-envelope RPS for reads and writes, peak multiplier, read:write ratio. Show the
arithmetic.

## 7. Storage estimation
Per-day and lifetime storage, including metadata and indexes. Show the arithmetic.

## 8. Bandwidth estimation
Ingress and egress bandwidth at average and peak. Show the arithmetic.

## 9. API design
REST and/or gRPC endpoint table: method, path, request, response, auth, idempotency.

## 10. Data model
Entities, relationships, and an example schema. Note the storage engine chosen and why.

## 11. High-level architecture
Original Mermaid context/component diagram of the whole system.

## 12. Request flow
Step-by-step trace of the primary read and write paths, with an original sequence diagram.

## 13. Component responsibilities
One bullet per component describing its single responsibility.

## 14. Database selection
Which database(s) and the reasoning. Compare at least two alternatives and explain the
rejection of the others.

## 15. Caching strategy
What is cached, where (edge/in-process/distributed), TTL, invalidation, stampede protection.

## 16. Partitioning strategy
Shard key, partition count, hot-key mitigation, rebalancing approach (consistent hashing
where relevant).

## 17. Replication strategy
Topology (leader-follower / multi-leader / leaderless), sync vs async, fan-out, lag handling.

## 18. Consistency model
What consistency the system offers to users (strong / eventual / read-after-write), and why.

## 19. Failure scenarios
List specific failures (node, zone, dependency, network partition) and the system's response.

## 20. Reliability strategy
SLI/SLO, error budget use, failover, backpressure, graceful degradation, chaos tests.

## 21. Security considerations
AuthN/Z, encryption, secrets, input validation, tenant isolation, audit, threat model.

## 22. Observability strategy
Metrics (golden signals), logs, traces, correlation IDs, dashboards, alerting, on-call.

## 23. Cost considerations
Dominant cost drivers (compute, storage, egress) and the optimizations chosen.

## 24. Scaling stages
A staged evolution: from MVP (single region, small) to extreme scale, with the change
triggers at each stage. Include a scaling-evolution diagram.

## 25. Trade-offs
The decisions made and what was sacrificed. Each trade-off: option chosen, option rejected,
reason.

## 26. Alternative designs
At least two meaningfully different architectures and why they were not chosen.

## 27. Interview discussion points
Ambiguities a candidate should surface, clarifying questions to ask, and depth cues.

## 28. Original Mermaid diagrams
Reference the `.mmd` files under `diagrams/case-studies/<name>/` and embed the key ones
(context, request-sequence, failure-flow, scaling-evolution, replication).

## 29. Further reading
Citations using stable IDs from [SOURCES.md](../SOURCES.md).

## 30. Practical exercises
3–5 exercises that deepen understanding (e.g., ""re-estimate at 100× scale"",
""add a write-ahead requirement"", ""design the failover test"").

---
Previous: <link> · Next: <link>
