# Case Study: Logging Platform

> **Tier:** intermediate · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Ingest, store, and query logs from many services at high event rates, with retention and
search. Write-heavy, append-only, tiered storage. This is a intermediate-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
**In (v1):** ingest (batched), store, search recent logs, retention/tiering. **Out:**
metrics/traces (separate; observability chapter), alerting UI.

For Logging Platform, these boundaries keep the first version focused on the core user value. Adding more features would dilute the design and delay shipping. Each excluded item is a scaling stage — a candidate for the next iteration once the baseline is proven.

## 3. Functional requirements
- Ingest structured logs from services (batched).
- Store with retention.
- Search recent
logs by service/severity/text/time. - Tier old logs to cold storage.

For Logging Platform, these requirements drive specific architectural decisions: the read-write ratio determines the caching strategy, the durability target sets the replication mode, and the idempotency requirement shapes the API contract.

## 4. Non-functional requirements
- Ingest throughput: millions of events/s. - Search latency p99 < 2 s (recent window).
- Durability 11 nines (via replication + cold tier).

For Logging Platform, each non-functional target constrains a specific component: the latency SLO bounds the number of synchronous hops, the availability target forces redundancy across availability zones, and the cost ceiling limits the replication factor and storage tier.

## 5. Explicit assumptions
1. 1M events/s peak, avg ~500 B each. [assumption] 2. Retain 7 days hot, 1 year cold.
[constraint] 3. ~95% of queries touch the last 24h. [assumption]

For Logging Platform, if these assumptions are off by an order of magnitude, the architecture must adapt: 10x traffic may require earlier sharding, a different read-write ratio changes the caching strategy, and a higher peak multiplier demands more headroom.

## 6. Traffic estimation
- 1M/s ingest = 500 MB/s ingress. Queries far fewer but scan large windows.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Logging Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
- 1M/s × 500 B × 86400 ≈ 43 TB/day hot; 7 days ≈ 300 TB hot; 1 year cold ≈ 15 PB (object
storage, compressed).

For Logging Platform, storage growth is projected from the daily write volume and retention policy. Index overhead and compression factors are accounted for in the total.

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

For Logging Platform, the data model follows the access pattern. The primary lookup determines the partition key; secondary lookups determine indexes. Denormalization is used selectively on hot read paths.

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

For Logging Platform, each component has one job. The gateway authenticates and routes. Services are stateless and scale horizontally. The data tier is the stateful core that scales by sharding.

## 14. Database selection
Hot: a search/OLAP store (Elasticsearch/OpenSearch or a columnar store) for recent queries.
Cold: object storage partitioned by date, queried via a scan engine. Rejected: one hot
index for a year (cost); pure object (slow recent search).

For Logging Platform, the database was chosen by access pattern, not familiarity. The rejected alternatives were wrong for this workload, not bad in general.

## 15. Caching strategy
Cache common queries (by service/severity/window). Hot shards cached in memory; cold queries
scan object storage.

For Logging Platform, the cache strategy matches the staleness tolerance. Cache-aside for most data, write-through where read-after-write matters, stampede protection on hot keys.

## 16. Partitioning strategy
Partition by `(service, date)` so a query touches one partition slice; cold storage
partitioned by date for cheap scans and lifecycle (delete/tier whole days).

For Logging Platform, the partition key balances query locality with even load distribution. Sharding strategy matters because a poor key creates hot spots under real traffic patterns.

## 17. Replication strategy
Hot index RF=3; cold tier uses object storage durability. Ingest at-least-once; dedup by
event id where needed.

For Logging Platform, replication mode is split: synchronous where durability is critical, asynchronous elsewhere for throughput. RF=3 tolerates one failure. Failover is tested regularly.

## 18. Consistency model
Recent logs: near-real-time (seconds of lag). Cold tier: immutable once written. Search is
eventually consistent with ingest.

For Logging Platform, the consistency level is the weakest users accept. Read-your-writes is provided where needed. Eventual consistency is bounded and monitored, not unbounded and silent.

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

For Logging Platform, the SLO makes reliability measurable. The error budget balances feature velocity with stability. Chaos testing validates that resilience claims hold under real failures.

## 21. Security considerations
Redact secrets/PII at ingest (don't store them); per-tenant log isolation; access control on
search; retention/deletion for compliance.

For Logging Platform, security layers TLS, encryption at rest, RBAC, PII redaction, and audit. The policy gateway is fail-closed for AI-augmented operations.

## 22. Observability strategy
Ingest rate, ingest backlog/lag, hot index size, cold tier growth, search latency by
window, query rate. Alert on ingest lag and hot-index saturation.

For Logging Platform, observability combines logs, metrics, and traces with correlation IDs. Golden signals drive the first dashboard. Alerts fire on burn rate, not raw thresholds.

## 23. Cost considerations
Cold tier (object storage) is cheap; hot index is expensive → keep hot window minimal (7
days). Compress; partition by date for clean lifecycle.

For Logging Platform, cost is driven by the binding resource. Caching, tiering, batching, and right-sizing are the levers. Cost per request is tracked and alerted on.

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

For Logging Platform, each trade-off lists what was chosen, what was rejected, and why. This makes the design defensible in review — every decision has documented reasoning.

## 26. Alternative designs
All-hot for a year (cost explosion). Pure object no index (slow recent search). One big
index unpartitioned (can't scale ingest/search).

For Logging Platform, the alternatives are real architectures that work under different constraints. They were rejected for this workload's specific requirements, not because they are bad designs.

## 27. Interview discussion points
Clarify ingest rate, retention, query patterns. Surface write-heaviness, tiering, and
partition-by-date for lifecycle — the cost levers.

For Logging Platform in an interview: clarify scope first, surface the read-write ratio, design the hot path deeply, discuss failures, and offer an alternative. Weak candidates skip failure modes.

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

