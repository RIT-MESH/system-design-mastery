# Case Study: Configuration Drift Detection Platform

> **Tier:** network-ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Continuously compare live device configurations against approved baselines/policies, detect drift, classify intent (authorized change vs unauthorized/error), and route to change-management with risk scoring. This is a network-ai-systems-tier system design challenge because it must handle high availability under peak load while ensuring human approval for all high-risk changes. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): baseline + policy definitions, periodic + on-change config collection, diff engine, drift classification (rule + AI), risk scoring, ticketing, compliance reporting. Out: auto-remediation (human approval).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Define baselines/policies per device class.
- Collect current configs.
- Diff vs baseline.
- Classify drift (authorized/unauthorized/error/policy violation).
- Score risk.
- Open change ticket with context.
- Report compliance.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Detect drift within 15 min of change.
- No false auto-remediation.
- Full audit.
- Multi-vendor config parsing.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 10k devices, configs pulled hourly + on-change traps. [assumption] 2. ~5 percent drift, most authorized. [assumption] 3. Baselines versioned. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Config pulls hourly (bursts) + on-change; read-dominated analysis.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Configuration Drift Detection Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Versioned configs (GBs, retained for audit) + baselines + diffs + tickets.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Config pull egress modest; small configs.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Configuration Drift Detection Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

GET /drift; POST /baselines; GET /compliance; POST /drift/:id/ack.

## 10. Data model
baselines(device_class, version, config); configs(device, version, config, hash); diffs(device, baseline, changes, class, risk); tickets(id, drift, status).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  Dev[Devices] --> Coll[Config collector]
  Coll --> Diff[Diff vs baseline]
  Diff --> Class[Rule + AI drift classifier]
  Class --> Risk[Risk scorer]
  Risk --> Ticket[Change ticket + context]
  Risk --> Comp[Compliance report]
  Baselines -.versioned.-> Diff
```

## 12. Request flow
Collector pulls configs (scheduled + on-change) -> diff vs versioned baseline -> rule+AI classifies drift (authorized/unauthorized/error/violation) -> risk score -> open change ticket with context + suggested review -> compliance report; human approves remediation.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Devices
  participant C1 as Config collector
  participant C2 as Diff vs baseline
  participant C3 as Rule AI drift classifier
  participant C4 as Risk scorer
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
Config collector, baseline store, diff engine, classifier (rule+AI), risk scorer, ticketing, compliance reporter.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Versioned configs in object storage (append-only, auditable); baselines + diffs + tickets in a relational store. Rejected: in-place config overwrite (no audit).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Baselines cached; recent diffs cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Configs by device/site; diffs by date; baselines by device class.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Config store durable RF/erasure; baselines RF=3; collector stateless, idempotent pulls.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Baselines strongly versioned; drift classification advisory; remediation requires human approval.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Collector can't reach device -> retry/backoff, alert. Classifier down -> fall back to rules. Baseline missing -> block classification, alert.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Collector can't reach device"]
  R2["retry backoff, alert"]
  C1 --> R2
  C3["Classifier down"]
  R4["fall back to rules"]
  C3 --> R4
  C5["Baseline missing"]
  R6["block classification, alert"]
  C5 --> R6
```

## 20. Reliability strategy
SLI drift-detection latency, coverage; SLO 99.9 percent. Rule fallback. Chaos: kill collector, assert resumable no missed devices.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Config encryption at rest; RBAC on baselines/configs; AI never auto-remediates; PII/secret redaction in configs; audit.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Drift rate, classification distribution, risk distribution, ticket MTTR, compliance %, collector coverage.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Config storage (versioned, grows) + compute (periodic). Retention policy cuts cost; tier old configs.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: scheduled pulls + diff + reports. -> Stage 2: on-change + AI classification + ticketing. -> Stage 3: policy-as-code, compliance dashboards. -> Stage 4: fleet-scale, AI risk scoring, air-gapped.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: scheduled pulls diff reports."]
  S2["Stage 2: on-change AI classification ticketing."]
  S3["Stage 3: policy-as-code, compliance dashboards."]
  S4["Stage 4: fleet-scale, AI risk scoring, air-gapped"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Pull (simple) vs push/on-change (fresh). Rule (deterministic) vs AI (intent) classification. Auto-ticket (fast) vs noise. Retention (audit) vs cost.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Manual diff (no scale). Auto-remediation (unsafe). Snapshot only without classification (noise).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify cadence, vendor variety, auto-remediation tolerance. Surface diff/classify/risk/ticket pipeline and human-approval principle.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/configuration-drift-detection/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Config compliance: Level 7; change management: Level 6; AI classifier. Sources: `S-OTEL` `S-SLO`.

## 30. Practical exercises

1. Policy-as-code baseline. 2. AI intent classification vs rules. 3. On-change vs hourly trade. 4. Secret redaction in stored configs. 5. Compliance reporting across sites.

---
Previous: Device upgrade management · Next: AI-assisted NOC

