# Case Study: Prompt-Management Platform

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  Author --> Version[Version and eval]
  Version --> Review[Change review]
  Review --> Deploy[Deploy or A/B test]
  Deploy --> Monitor[Monitor performance]
  Monitor -.regression.-> Rollback[Rollback]
  A/B --> Results[Compare]
  Results --> Deploy
```


## 28. Original Mermaid diagrams

Standalone sources under `diagrams/case-studies/prompt-management-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. Request sequence and failure flow:

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant P0 as Client
  participant P1 as Prompt-Management Platfo
  participant P2 as Store
  P0 ->> P1: query
  P1 ->> P2: look up or fetch
  P2 -->> P1: response
  P1 -->> P0: response
  alt success
    P0 -->> P0: done
  else failure
    P0 -->> P0: retry or fallback
  end
```

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Eval fail"]
  R2["block deploy"]
  C1 --> R2
  C3["A B inconclusive"]
  R4["extend or default to control"]
  C3 --> R4
  C5["Performance regression"]
  R6["rollback"]
  C5 --> R6
  C7["Cache stale"]
  R8["TTL manual refresh"]
  C7 --> R8
```

## 1. Problem statement

A platform that versions, tests, deploys, and monitors prompt templates across AI features, with A/B testing, rollback, and change review.

This system sits at the intersection of distributed systems and operational reliability. The design must balance latency versus durability while ensuring no single component failure cascades. The target audience includes engineers and operators, so the design must be observable, debuggable, and reversible.
## 2. Scope

In: prompt template registry, versioning, A/B testing, deployment, change review, rollback, monitoring. Out: automated prompt optimization.

The scope boundary is deliberate: including too much in v1 risks a system that is broad but shallow. Each excluded feature is a candidate for a later iteration once the core loop is proven.
## 3. Functional requirements

- Store and version prompt templates. - Test prompts against eval sets before deploy. - A/B test prompt versions. - Deploy with rollback. - Review prompt changes (cost, safety, quality). - Monitor performance.

These requirements drive the architecture: the read-heavy pattern pushes toward caching; the durability requirement forces synchronous writes; the idempotency requirement means every write path handles redelivery without double-application.
## 4. Non-functional requirements

- Prompt deploy < 1 min. - No production change without review. - Availability 99.9 percent.

The non-functional targets shape every component choice: the latency SLO forces edge caching and limits synchronous cross-region calls; the availability target drives redundancy (RF=3, multi-AZ); the cost target constrains the model size.
## 5. Explicit assumptions

1. 100 templates across 10 features. 2. 1-2 changes/week per feature. 3. A/B 10 percent for 24h.

These assumptions are the load-bearing facts of the design. If any is wrong by an order of magnitude, the architecture must adapt: 10x more traffic may require sharding earlier; a different read-write ratio changes the caching strategy entirely.
## 6. Traffic estimation

Prompt lookups at request rate (cached); changes infrequent; A/B continuous.

The traffic estimate reveals the binding constraint. Peak is modeled at 10x average. The read-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy), which changes the storage and replication strategy.
## 7. Storage estimation

Prompt versions + eval results + A/B data + monitoring; small, versioned.

Storage growth is linear with time and must be planned with retention. The estimate includes metadata and index overhead (20-30 percent above raw). Without a retention policy, storage grows unboundedly.
## 8. Bandwidth estimation

Prompt text small; eval results small.

Bandwidth is often not the binding constraint but becomes significant at the edge during viral spikes. CDN and edge caching cut origin egress; compression cuts bandwidth by 50-80 percent where applicable.
## 9. API design

POST /prompts (template) -> version; POST /prompts/:id/deploy -> deployed; POST /prompts/:id/ab-test -> results; GET /prompts/:id/performance.

The API follows REST for external clients and gRPC for internal calls. Every write endpoint accepts an idempotency key. Rate limiting is enforced at the gateway before the service tier.
## 10. Data model

prompts(id, feature, versions[]); versions(id, template, status, eval_results, deploy_ts); ab_tests(id, prompt, version_a, version_b, traffic_split, results); performance(prompt, version, metrics, ts).

The data model is designed around the access pattern, not the entity shape. The primary access path determines the partition key; secondary paths determine indexes. Denormalization is applied selectively where the hot read path would otherwise require expensive joins.
## 12. Request flow

Author writes prompt -> version + eval -> change review (cost, safety, quality) -> deploy or A/B (10 percent for 24h) -> monitor -> if regression: rollback -> all versioned and audited.

The request flow reveals the critical path: any component on the hot path that fails or slows degrades the user experience. The design applies timeouts, circuit breakers, and bulkheads to each hop. The write path includes an idempotency check before any state mutation.
## 13. Component responsibilities

Prompt registry, version manager, eval runner, change reviewer, A/B manager, deployer, performance monitor.

Each component has a single, well-defined responsibility. The gateway handles auth and routing; the service tier is stateless and horizontally scalable; the data tier is the stateful core, carefully partitioned and replicated. The separation allows each tier to scale independently.
## 14. Database selection

Prompt registry (Git-backed); eval results (time-series); A/B data (relational); performance (time-series).

The database choice is driven by the access pattern. The rejected alternatives were rejected for specific reasons: a relational DB was rejected if the workload is a single key lookup at massive scale; a KV store was rejected if joins and transactions are needed.
## 15. Caching strategy

Hot prompts cached in-memory; eval results cached per version; A/B assignment cached per user.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default; write-through is used where read-after-write consistency is required. Stampede protection is applied to any key that can go viral. Cache entries are namespaced by tenant.
## 16. Partitioning strategy

Prompts by feature; A/B by user; performance by prompt + version + time.

The partition key co-locates related data while distributing load evenly. Consistent hashing with virtual nodes minimizes data movement when nodes change. A hot key is mitigated by caching, extra replication, or key splitting.
## 17. Replication strategy

Prompt registry in Git; cache replicated; A/B data RF=3.

Replication is synchronous on the write-confirmation path where durability is critical and asynchronous elsewhere. RF=3 tolerates one failure. Failover is tested, not just configured. Cross-region replication is asynchronous with a documented RPO.
## 18. Consistency model

Prompt versions immutable once deployed; A/B assignment sticky per user; performance eventual.

The consistency model is the weakest that users can tolerate. Read-your-writes is provided where the user expects to see their own write. Eventual consistency is bounded (seconds) and monitored. The system documents what eventual means to users.
## 19. Failure scenarios

Eval fail -> block deploy. A/B inconclusive -> extend or default to control. Performance regression -> rollback. Cache stale -> TTL + manual refresh.

Each failure scenario has a documented response: which component detects it, how failover happens, what the user experiences, and how recovery is verified. Bulkheads and circuit breakers prevent one slow dependency from cascading.
## 20. Reliability strategy

SLI deploy latency, no-unreviewed-change; SLO 99.9 percent. Block deploy without eval.

The SLO defines what good means measurably; the error budget is the allowed unavailability spent on deploys and feature risk. The system is tested with chaos engineering to verify resilience. An untested failover is not a failover.
## 21. Security considerations

Prompt review for PII/injection safety; per-feature access control; audit all changes; rollback always available; no prompt with secrets.

Security is defense in depth: TLS, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed: on any error, the system refuses to act.
## 22. Observability strategy

Deploy frequency, eval pass rate, A/B win rate, regression count, prompt cost trend, latency per version.

Observability uses logs, metrics, and traces with correlation IDs. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not raw thresholds. The on-call runbook for each alert is tested.
## 23. Cost considerations

Eval inference per change; A/B inference (duplicate traffic); monitor negligible. Amortize across changes.

Cost is dominated by the binding resource. Primary levers: caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing. Cost is tracked as a first-class metric and alerted on when unit cost spikes.
## 24. Scaling stages

Stage 1: version + deploy + rollback. -> Stage 2: eval + A/B + monitoring. -> Stage 3: automated optimization + multi-feature. -> Stage 4: enterprise prompt governance.

The scaling stages are triggered by specific thresholds, not by calendar. Each stage is a deliberate architectural change: Stage 1 handles initial load; Stage 2 when a single node saturates; Stage 3 when latency exceeds the SLO; Stage 4 when hot keys threaten the origin.
## 25. Trade-offs

Versioning (safety) vs speed. A/B (data-driven) vs direct deploy (fast). Strict review (safe) vs lightweight (agile). Cache (latency) vs freshness.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct; it presents the chosen option, the rejected alternative, and the workload-specific reason.
## 26. Alternative designs

No versioning (no rollback). Hardcoded prompts (no A/B). No review (unsafe). No A/B (guess).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements that make them inferior here but not universally inferior.
## 27. Interview discussion points

Clarify change frequency, A/B policy, eval requirements. Surface versioning, eval, A/B, monitoring, rollback, change review.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply, discuss failure modes explicitly, and offer an alternative with a reason.
## 29. Further reading

Prompt management refs; docs/ai-systems/10-ai-evaluation; templates/ai/prompt-change-review.md; LLM gateway: 13-llm-gateway.

The further reading cites primary sources (RFCs, papers, official documentation) via stable IDs in SOURCES.md, not secondary blog posts. Each citation is chosen because it is the authoritative source for a specific technical claim.
## 30. Practical exercises

1. Version + eval + deploy a prompt. 2. A/B test design. 3. Regression + rollback. 4. Change review checklist. 5. Cost impact of prompt length.


---
Previous: AI evaluation · Next: AI safety and policy gateway

The exercises push the reader beyond v1: re-estimating at 10x reveals capacity limits; adding a new requirement forces an architectural change; designing the failover test reveals whether resilience claims are real.
