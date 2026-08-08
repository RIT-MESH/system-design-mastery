# Case Study: Prompt-Management Platform

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
A platform that versions, tests, deploys, and monitors prompt templates across AI features, with A/B testing, rollback, and change review. This is a ai-systems-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In: prompt template registry, versioning, A/B testing, deployment, change review, rollback, monitoring. Out: automated prompt optimization.

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Store and version prompt templates.
- Test prompts against eval sets before deploy.
- A/B test prompt versions.
- Deploy with rollback.
- Review prompt changes (cost, safety, quality).
- Monitor performance.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Prompt deploy < 1 min.
- No production change without review.
- Availability 99.9 percent.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 100 templates across 10 features. 2. 1-2 changes/week per feature. 3. A/B 10 percent for 24h.

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Prompt lookups at request rate (cached); changes infrequent; A/B continuous.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Prompt-Management Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Prompt versions + eval results + A/B data + monitoring; small, versioned.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Prompt text small; eval results small.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Prompt-Management Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /prompts (template) -> version; POST /prompts/:id/deploy -> deployed; POST /prompts/:id/ab-test -> results; GET /prompts/:id/performance.

## 10. Data model
prompts(id, feature, versions[]); versions(id, template, status, eval_results, deploy_ts); ab_tests(id, prompt, version_a, version_b, traffic_split, results); performance(prompt, version, metrics, ts).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

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

## 12. Request flow
Author writes prompt -> version + eval -> change review (cost, safety, quality) -> deploy or A/B (10 percent for 24h) -> monitor -> if regression: rollback -> all versioned and audited.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Version and eval
  participant C1 as Change review
  participant C2 as Deploy or A B test
  participant C3 as Monitor performance
  participant C4 as Rollback
  C0 ->> C1: send request
  C1 ->> C2: validate and process
  C2 ->> C3: query or persist
  C3 ->> C4: acknowledge
  C4 -->> C3: result
  C3 -->> C2: response
  C2 -->> C1: response
  C1 -->> C0: response
  alt operation succeeds
    C0 -->> C0: confirm
  else operation fails
    C4 -->> C4: log error
    C0 -->> C0: retry with backoff
  end
```

## 13. Component responsibilities
Prompt registry, version manager, eval runner, change reviewer, A/B manager, deployer, performance monitor.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Prompt registry (Git-backed); eval results (time-series); A/B data (relational); performance (time-series).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Hot prompts cached in-memory; eval results cached per version; A/B assignment cached per user.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Prompts by feature; A/B by user; performance by prompt + version + time.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Prompt registry in Git; cache replicated; A/B data RF=3.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Prompt versions immutable once deployed; A/B assignment sticky per user; performance eventual.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Eval fail -> block deploy. A/B inconclusive -> extend or default to control. Performance regression -> rollback. Cache stale -> TTL + manual refresh.

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

## 20. Reliability strategy
SLI deploy latency, no-unreviewed-change; SLO 99.9 percent. Block deploy without eval.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Prompt review for PII/injection safety; per-feature access control; audit all changes; rollback always available; no prompt with secrets.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Deploy frequency, eval pass rate, A/B win rate, regression count, prompt cost trend, latency per version.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Eval inference per change; A/B inference (duplicate traffic); monitor negligible. Amortize across changes.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: version + deploy + rollback. -> Stage 2: eval + A/B + monitoring. -> Stage 3: automated optimization + multi-feature. -> Stage 4: enterprise prompt governance.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: version deploy rollback."]
  S2["Stage 2: eval A B monitoring."]
  S3["Stage 3: automated optimization multi-feature."]
  S4["Stage 4: enterprise prompt governance."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Versioning (safety) vs speed. A/B (data-driven) vs direct deploy (fast). Strict review (safe) vs lightweight (agile). Cache (latency) vs freshness.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
No versioning (no rollback). Hardcoded prompts (no A/B). No review (unsafe). No A/B (guess).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify change frequency, A/B policy, eval requirements. Surface versioning, eval, A/B, monitoring, rollback, change review.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/prompt-management-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Prompt management refs; docs/ai-systems/10-ai-evaluation; templates/ai/prompt-change-review.md; LLM gateway: 13-llm-gateway. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Version + eval + deploy a prompt. 2. A/B test design. 3. Regression + rollback. 4. Change review checklist. 5. Cost impact of prompt length.

---
Previous: AI evaluation · Next: AI safety and policy gateway

