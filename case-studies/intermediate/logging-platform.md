# Case Study: Logging Platform

> **Tier:** intermediate · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Ingest, store, and query logs from many services at high event rates, with retention and
search. Write-heavy, append-only, tiered storage. This is a intermediate-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
**In (v1):** ingest (batched), store, search recent logs, retention/tiering. **Out:**
metrics/traces (separate; observability chapter), alerting UI.

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Ingest structured logs from services (batched).
- Store with retention.
- Search recent
logs by service/severity/text/time. - Tier old logs to cold storage.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Ingest throughput: millions of events/s. - Search latency p99 < 2 s (recent window).
- Durability 11 nines (via replication + cold tier).

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M events/s peak, avg ~500 B each. [assumption] 2. Retain 7 days hot, 1 year cold.
[constraint] 3. ~95% of queries touch the last 24h. [assumption]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
- 1M/s ingest = 500 MB/s ingress. Queries far fewer but scan large windows.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Logging Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
- 1M/s × 500 B × 86400 ≈ 43 TB/day hot; 7 days ≈ 300 TB hot; 1 year cold ≈ 15 PB (object
storage, compressed).

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
- Ingress 500 MB/s sustained; queries scan GBs–TBs. Ingest bandwidth is significant.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Logging Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | /ingest (batch) | [events] | ack |
| GET | /search | query, time window | results |

## 10. Data model
Events partitioned by `(service, ts)`, stored as compressed columnar/batched objects for
cold, and in a hot search index for recent. Fields: service, severity, ts, message, attrs.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture
```mermaid
%% created-for: system-design-mastery
flowchart LR
  Src["Services"] --> Ingest["Ingest - batched, LZ4"]
  Ingest --> Stream["Partitioned stream"]
  Stream --> Hot["Hot search index - recent"]
  Stream --> Tier["Cold tier - object storage, partitioned"]
  Search["Search API"] --> Hot
  Search --> Tier
```

## 12. Request flow
Ingest: services batch logs → ingest compresses → stream → hot index (recent) + cold tier
(partitioned objects). Search: route by time window to hot index (recent) or cold (old,
slower); merge results.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Services
  participant C1 as Ingest batched, LZ4
  participant C2 as Partitioned stream
  participant C3 as Hot search index recent
  participant C4 as Cold tier object storage
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
Ingest: batch + compress. Stream: partition by service/ts. Hot index: searchable recent.
Cold tier: cheap durable retention. Search API: route + merge.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Hot: a search/OLAP store (Elasticsearch/OpenSearch or a columnar store) for recent queries.
Cold: object storage partitioned by date, queried via a scan engine. Rejected: one hot
index for a year (cost); pure object (slow recent search).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Cache common queries (by service/severity/window). Hot shards cached in memory; cold queries
scan object storage.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Partition by `(service, date)` so a query touches one partition slice; cold storage
partitioned by date for cheap scans and lifecycle (delete/tier whole days).

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Hot index RF=3; cold tier uses object storage durability. Ingest at-least-once; dedup by
event id where needed.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Recent logs: near-real-time (seconds of lag). Cold tier: immutable once written. Search is
eventually consistent with ingest.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Hot index shard down → recent search degrades or returns partial. Cold tier unavailable →
old queries fail (not the hot path). Ingest backlog → logs lag, alert.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Hot index shard down"]
  R2["recent search degrades or returns partia"]
  C1 --> R2
  C3["Cold tier unavailable"]
  C4["Ingest backlog"]
  R5["logs lag, alert"]
  C4 --> R5
```

## 20. Reliability strategy
SLI ingest success, search latency; SLO 99.9% ingest. Backpressure on ingest backlog; DLQ
for undeliverable batches. Chaos: kill a hot shard, assert partial-but-serving recent
search.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Redact secrets/PII at ingest (don't store them); per-tenant log isolation; access control on
search; retention/deletion for compliance.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Ingest rate, ingest backlog/lag, hot index size, cold tier growth, search latency by
window, query rate. Alert on ingest lag and hot-index saturation.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Cold tier (object storage) is cheap; hot index is expensive → keep hot window minimal (7
days). Compress; partition by date for clean lifecycle.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: ingest + hot index. → Stage 2: partitioned cold tier + date lifecycle. → Stage 3:
stream-based ingest, columnar cold for cheap scans. → Stage 4: federated search across
hot+cold, sampling for huge scans.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: ingest hot index."]
  S2["Stage 2: partitioned cold tier date lifecycle."]
  S3["Stage 3: stream-based ingest, columnar cold for c"]
  S4["Stage 4: federated search across"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Hot window size (cost vs search speed). Partition by date (clean lifecycle, scan-friendly)
vs by hash (better load balance, harder retention). Compress (saves storage, CPU).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
All-hot for a year (cost explosion). Pure object no index (slow recent search). One big
index unpartitioned (can't scale ingest/search).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify ingest rate, retention, query patterns. Surface write-heaviness, tiering, and
partition-by-date for lifecycle — the cost levers.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/logging-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Search engines: Level 2; tiering/lifecycle: Level 3; streams: Level 10; logs/metrics/traces:
Level 8. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises
1. Re-estimate with 5-year retention — cold tier size and cost. 2. Add structured field
search — index trade-offs. 3. Design ingest backpressure without dropping logs. 4. A query
scans a year — how to make it affordable (sampling/summary). 5. Add alerting on log
patterns.

---
Previous: [Search autocomplete](search-autocomplete.md) · Next: (next intermediate case study)

