# Case Study: Real-Time Analytics Platform

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Ingest events continuously, aggregate, and serve sub-second dashboards/queries over recent and historical data — a stream + serving store. This is a advanced-tier system design challenge because it must handle high-throughput data ingestion while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): ingest events, real-time aggregations, dashboards, alerts. Out: ad-hoc SQL on raw (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Ingest events continuously.
- Compute real-time aggregations (windows).
- Serve dashboards sub-second.
- Alert on aggregates.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Dashboard refresh < 1 s.
- Ingest millions of events/s.
- Recent data low-latency; historical queryable.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M events/s, ~200 B. [assumption] 2. Dashboards on 1-min/1h windows. [assumption] 3. Retain 1 year. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
1M events/s ingest; dashboard reads bursty; queries scan aggregates not raw.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Real-Time Analytics Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Raw stream retained (replay) + aggregates; PB over a year. Tier cold.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Ingress ~200 MB/s; dashboards pull aggregates (small).

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Real-Time Analytics Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST /ingest (batch) | events | ack |
| GET |/dashboard | query | series |

## 10. Data model
events(stream, partitioned by key); aggregates(metric, window, value); dashboards(query -> cached result).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Src[Sources] --> Stream[Stream] --> Proc[Stream processors]
  Proc --> Agg[Aggregates store]
  Proc --> Raw[Raw retention]
  Dash[Dashboard API] --> Agg
  Dash --> Cache[Result cache]
  Alert[Alert engine] --> Agg
```

## 12. Request flow
Ingest -> stream -> processors compute windowed aggregates -> aggregates store (+ raw retained for replay) -> dashboard API reads aggregates (cached) -> alerts on thresholds.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Sources
  participant C1 as Stream
  participant C2 as Stream processors
  participant C3 as Aggregates store
  participant C4 as Raw retention
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
Ingest, stream, processors (windowed, stateful), aggregates store, dashboard API, alert engine.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Aggregates: a fast serving store (columnar/KV) for sub-second reads; raw: retained stream/object for replay. Rejected: query raw for every dashboard (slow).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Dashboard results cached (short TTL); aggregates in memory for hot windows.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Stream partitioned by key; aggregates by (metric, window); raw by time for replay.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Aggregates RF=3; raw retained in durable storage; processors checkpoint (effectively-once).

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Aggregates near-real-time (window lag seconds). Exactly-once via checkpoints + idempotent aggregation. Historical via replay.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Processor failure -> restore from checkpoint, replay (idempotent). Aggregate store down -> dashboard degrades to cached/last. Raw retention gap -> historical loss (alert).

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Processor failure"]
  R2["restore from checkpoint, replay idempote"]
  C1 --> R2
  C3["Aggregate store down"]
  R4["dashboard degrades to cached last"]
  C3 --> R4
  C5["Raw retention gap"]
  R6["historical loss alert"]
  C5 --> R6
```

## 20. Reliability strategy
SLI ingest lag, dashboard latency; SLO 99.9%. Checkpoint recovery. Chaos: kill processors, assert replay + no double counts.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Per-tenant data isolation; redact PII at ingest; access control on dashboards; retention/deletion.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Ingest rate, processor lag, window freshness, dashboard p99, query rate, checkpoint failures.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Storage (raw + aggregates) + compute (processors). Downsample old aggregates; tier raw cold.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: stream + aggregates + dashboards. -> Stage 2: windowed processors + checkpointing. -> Stage 3: tiered raw, rollups. -> Stage 4: federated queries, ML features.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: stream aggregates dashboards."]
  S2["Stage 2: windowed processors checkpointing."]
  S3["Stage 3: tiered raw, rollups."]
  S4["Stage 4: federated queries, ML features."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Precompute aggregates (fast reads, write cost) vs query raw (slow). Retain raw (replay) vs cost. Exactly-once (correctness) vs throughput.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Query raw per dashboard (slow). No checkpointing (double counts on recovery). All-hot retention (cost).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify event rate, dashboard latency, retention. Surface stream + aggregates + serving store + checkpointing.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/real-time-analytics/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Streams: Level 10; checkpointing/CDC: Level 4; dashboards: Level 8. Sources: `S-MAPREDUCE` `S-LAMBDA`.

## 30. Practical exercises

1. Window with late events (watermarks). 2. Replay a day of events to rebuild aggregates. 3. Sub-second dashboard at 10M events/s. 4. Exactly-once across a processor restart. 5. Tier raw cold — recall latency.

---
Previous: Identity & access-management · Next: Recommendation engine

