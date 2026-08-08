# Case Study: Collaborative Document Editor

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Real-time co-editing of a document by many users with conflict-free merging and presence — a CRDT/OT-based, offline-capable state system. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): real-time co-edit, presence, offline + merge, history. Out: comments, version branching (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Multiple users edit concurrently.
- Merge edits without conflict.
- Show presence/cursors.
- Work offline and merge on reconnect.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Keystroke-to-render < 50 ms local.
- Merge correctness (no lost edits).
- Availability 100% for editing (offline ok).

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. ~20 concurrent editors/doc, 10M docs. [assumption] 2. Ops ~1 KB. [assumption] 3. Merge must never lose edits. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Edit ops per active doc; presence heartbeats. Modest aggregate; correctness is the challenge.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Collaborative Document Editor, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Doc as a CRDT/OT op log; snapshots for fast load. ~10M docs x KB-MB.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Small ops streamed; modest aggregate.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Collaborative Document Editor, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

WebSocket for ops/presence; REST for snapshots/history.

## 10. Data model
doc(id, crdt state, op log, snapshots); presence(user, doc, cursor). Op log is the source of truth; state derived.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  U1 & U2 --> Relay[Op relay / gateway]
  Relay --> Doc[Doc service - CRDT/OT]
  Doc --> Store[Op log + snapshots]
  Doc -->|merge| U1 & U2
  U3[Offline] -.reconnect.-> Relay
```

## 12. Request flow
Edits sent as ops -> doc service applies to CRDT -> merges deterministically -> broadcasts to all -> persisted in op log. Offline users accumulate ops locally and merge on reconnect.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Op relay gateway
  participant C1 as Doc service CRDT OT
  participant C2 as Op log snapshots
  participant C3 as Offline
  C0 ->> C1: send request
  C1 ->> C2: validate and process
  C2 ->> C3: query or persist
  C3 -->> C2: result
  C2 -->> C1: response
  C1 -->> C0: response
  alt operation succeeds
    C0 -->> C0: confirm
  else operation fails
    C3 -->> C3: log error
    C0 -->> C0: retry with backoff
  end
```

## 13. Component responsibilities
Op relay/gateway, doc service (CRDT/OT engine), op log + snapshots, presence.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Op log (append-only) + snapshots; CRDT state in memory derived. Rejected: last-write-wins (lost edits); server-locked editing (no offline).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Doc state in memory; snapshots for fast load.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Per doc (one doc's state on a shard); presence sharded by doc.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Op log RF=3; CRDT state replicated for availability. CRDTs converge without coordination.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Causal/eventual with no lost edits (CRDT). Concurrency safe; ordering preserved per the CRDT rules.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Relay down -> clients reconnect to another; CRDT merge resumes. Doc shard down -> promote; op log persists. Offline -> local ops merge later.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Relay down"]
  R2["clients reconnect to another"]
  C1 --> R2
  C3["Doc shard down"]
  R4["promote"]
  C3 --> R4
  C5["Offline"]
  R6["local ops merge later"]
  C5 --> R6
```

## 20. Reliability strategy
SLI merge correctness, edit latency; SLO 99.9%. CRDTs give offline + no-lost-edits. Chaos: partition clients, assert merge on heal.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Per-doc auth; PII in docs; audit of edits; presence privacy.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Edit latency, merge conflicts rate, presence freshness, op-log lag, snapshot freshness.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Op-log storage + memory per active doc; snapshots cut load cost.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: op relay + CRDT. -> Stage 2: per-doc sharding + snapshots. -> Stage 3: offline + merge at scale. -> Stage 4: large docs, presence fan-out.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: op relay CRDT."]
  S2["Stage 2: per-doc sharding snapshots."]
  S3["Stage 3: offline merge at scale."]
  S4["Stage 4: large docs, presence fan-out."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
CRDT (offline, no-lost) vs state metadata growth. OT (smaller state) vs central transform complexity. Snapshots (fast load) vs build cost.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Last-write-wins (lost edits). Lock-based (no concurrency/offline). Mutable state (no audit/merge).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify offline, concurrency, no-lost-edits. Surface CRDT/OT, op log, offline merge.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/collaborative-document-editor/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
CRDTs: Level 4; real-time: Level 10; op log/event sourcing: Level 5. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. CRDT metadata compaction. 2. Large doc (book) editing. 3. Presence fan-out for 100 cursors. 4. Snapshot cadence vs load latency. 5. Merge two long-offline branches.

---
Previous: Online multiplayer game · Next: Code-hosting platform

