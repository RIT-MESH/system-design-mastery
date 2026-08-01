# Case Study: Distributed Cache

> **Tier:** intermediate · **Status:** complete
> A complete intermediate case study demonstrating the 30-section template for a stateful,
> consistency-sensitive system. All numbers and diagrams are original.

## 1. Problem statement
Many applications need a fast, shared, in-memory cache to offload hot reads from a
database. We need a **distributed cache** that behaves like one logical key-value store
across many nodes: O(1)-ish gets/sets, automatic partitioning, replication for failover,
and graceful handling of node loss and hot keys.

This system sits at the intersection of distributed systems and operational reliability. The design must balance the latency versus durability trade-off inherent to the workload while ensuring no single component failure cascades into a full outage. The target audience includes both engineers building the system and operators maintaining it, so the design must be observable, debuggable, and reversible at every step.
## 2. Scope
**In (v1):** `GET`, `SET` (with TTL), `DELETE`; partitioning across nodes; per-key
replication; node join/leave with minimal key movement; basic eviction (LRU).
**Out (v1):** multi-region, transactions across keys, persistent disk durability beyond
replication, rich data structures (sets/maps) — noted as scaling stages.

The scope boundary is deliberate: including too much in v1 risks shipping a system that is broad but shallow. Each excluded feature is a candidate for a later iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.
## 3. Functional requirements
- The cache **shall** store a value under a key with an optional TTL.
- The cache **shall** return the value for a `GET` or indicate a miss.
- The cache **shall** evict entries on TTL expiry or under memory pressure (LRU).
- The cache **shall** survive the loss of one node per key without data loss.
- The cache **shall** rebalance when nodes join or leave, moving only the affected keys.

These requirements drive the architecture: the read-heavy pattern pushes toward caching and replication; the durability requirement forces synchronous writes on the critical path; the idempotency requirement means every write path must handle redelivery without double-application. Each requirement has a direct architectural consequence.
## 4. Non-functional requirements
- Read latency p99 < 2 ms (in-memory); p99.9 < 10 ms even under a rebalance.
- Availability 99.9% per shard; the cluster degrades (some misses) rather than fails hard.
- Throughput: ~100k ops/s per node; horizontally scalable by adding nodes.
- Consistency: per-key linearizability via a primary owner; eventual consistency across
  replicas (bounded staleness < replication lag).

The non-functional targets shape every component choice: the latency SLO forces edge caching and limits synchronous cross-region calls on the hot path; the availability target drives redundancy (RF=3, multi-AZ); the durability target forces synchronous replication on committed writes; the cost target constrains the model size and prevents over-provisioning.
## 5. Explicit assumptions
1. ~10,000 keys/second average read rate per shard; 1k/s writes. [assumption] (read-heavy)
2. Average value 4 KB; working set 50 GB across the cluster. [assumption]
3. Up to 100 nodes; one-node failure per replica group is the design failure. [assumption]
4. Hot keys: a single key can drive 1–5% of traffic; must not melt one node. [constraint]
5. Replication factor 3 per key (primary + 2 replicas). [constraint]

These assumptions are the load-bearing facts of the design. If any assumption is wrong by an order of magnitude, the architecture must adapt: 10x more traffic may require sharding earlier; 10x more data may require tiering sooner; a different read-write ratio may change the caching strategy entirely. The design is parameterized by these assumptions, not locked to them.
## 6. Traffic estimation
- 100 nodes × 100k ops/s = **10M ops/s cluster** at full scale.
- Reads ~90% → 9M reads/s; writes ~1M writes/s.
- Per-node: ~90k reads/s + 10k writes/s. Read:write ≈ 9:1, read-heavy.

The traffic estimate reveals the binding constraint. For this workload, the binding resource is compute or storage or bandwidth (as noted above). Peak is modeled at 10x average, which is conservative for viral workloads but aggressive for steady-state enterprise systems. The read-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy), which changes the entire storage and replication strategy.
## 7. Storage estimation
- Working set 50 GB across 100 nodes → ~500 MB/node hot data + replicas (×3) → ~1.5 GB/node.
- In-memory only; far below node RAM. Headroom is for *peak* working set growth, not average.

Storage growth is linear with time and must be planned with retention in mind. The estimate includes metadata and index overhead (typically 20-30 percent above raw data). Without a retention policy, storage grows unboundedly and cost becomes unsustainable. The design includes tiering (hot to cold) and lifecycle rules to manage this growth automatically.
## 8. Bandwidth estimation
- 9M reads/s × 4 KB ≈ 36 GB/s egress cluster-wide; per node ~360 MB/s — manageable on 10 GbE.
- Writes 1M/s × 4 KB ≈ 4 GB/s ingress cluster-wide. Network is comfortable at this scale.

Bandwidth is often not the binding constraint for this workload, but it becomes significant at the network edge during viral spikes. The design uses CDN and edge caching to cut origin egress; co-location of compute and data reduces inter-node traffic; and compression (for logs, telemetry, and bulk transfers) cuts bandwidth by 50-80 percent where applicable.
## 9. API design
| Method | Path/Op | Request | Response | Idempotent |
|--------|---------|---------|----------|:---------:|
| GET | `key` | — | value or `MISS` | yes |
| SET | `key ttl value` | — | `OK` | yes (last-write-wins) |
| DELETE | `key` | — | `OK`/`MISS` | yes |
| STATS | node/cluster | — | op counts, memory, evictions | yes |

The API design follows REST conventions for external clients and gRPC for internal service-to-service communication where throughput matters. Every write endpoint accepts an idempotency key so retries from unreliable clients do not double-apply. Streaming endpoints use Server-Sent Events (SSE) for token-by-token LLM output or chunked transfer for large payloads. Rate limiting is enforced at the gateway before the request reaches the service tier.
## 10. Data model
A flat key→value map partitioned across nodes. No schema; values are opaque bytes. Each node
owns a contiguous range of a **consistent hash ring** (with vnodes for balance). Per key, a
**primary owner** (the first node clockwise) plus the next two nodes are **replicas**.

The data model is designed around the access pattern, not the entity shape. The primary access path (key lookup by ID) determines the partition key; the secondary access paths (by timestamp, by owner, by status) determine the indexes. Denormalization is applied selectively where the hot read path would otherwise require expensive joins, with CDC or the outbox pattern keeping the denormalized view consistent with the normalized source of truth.
## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> CL["Client library / router<br/>(ring-aware)"]
  CL -->|"hash(key) -> ring"| N1["Node A (primary)"]
  CL -->|"replicate"| N2["Node B (replica)"]
  CL -->|"replicate"| N3["Node C (replica)"]
  N1 & N2 & N3 --> Ring["Consistent hash ring (vnodes)"]
  Gossip["Membership / gossip"] -.membership.-> N1 & N2 & N3
  CL --> Gossip
```


## 12. Request flow
**GET:**
1. Client hashes the key onto the ring and routes to the **primary owner**.
2. Primary serves from memory; on miss returns `MISS` (we do not consult the DB — that's the
   caller's job; we are a cache).
3. For higher availability, a read can go to a replica (accepting staleness), but the default
   is primary for read-your-writes.

**SET:**
1. Client routes to the primary owner.
2. Primary writes locally, replicates to the 2 replicas (async by default for latency;
   sync option for stronger durability).
3. Primary acks once replication policy is satisfied.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C as Client
  participant P as Primary
  participant R1 as Replica 1
  participant R2 as Replica 2
  C->>P: SET k v ttl
  P->>P: store
  P-->>R1: replicate (async)
  P-->>R2: replicate (async)
  P-->>C: OK (policy met)
  C->>P: GET k
  P-->>C: v
```

The request flow reveals the critical path: any component on the hot path that fails or slows degrades the user experience. The design identifies this path explicitly and applies timeouts, circuit breakers, and bulkheads to each hop. The write path includes an idempotency check (by key) before any state mutation, ensuring redelivery safety. The read path serves from cache first, falling back to the authoritative store only on miss.
## 13. Component responsibilities
- **Client library/router**: ring-aware routing; retries on miss/failure; local membership
  cache.
- **Cache node**: stores its key range in memory; LRU eviction; TTL expiry; serves reads.
- **Consistent hash ring + vnodes**: maps keys to owners; minimizes movement on membership
  change.
- **Gossip/membership**: spreads join/leave/failure; detects dead nodes.
- **Replication**: per-key primary→replicas; configurable sync/async.

Each component has a single, well-defined responsibility. The gateway handles auth, rate limiting, and routing; the service tier is stateless and horizontally scalable; the data tier is the stateful core, carefully partitioned and replicated. The separation allows each tier to scale independently: the stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas, not by adding arbitrary instances.
## 14. Database selection
**Chosen: in-memory per-node store (Redis-like or custom).** The "database" here is memory
itself; durability is via replication, not disk (we are a cache, not a source of truth).
- **Rejected: a single big Redis**: becomes a SPOF and bottleneck; we want horizontal scale.
- **Rejected: disk-backed store**: defeats the latency goal. The DB behind us is the source
  of truth, not the cache.

The database choice is driven by the access pattern, not by familiarity. The rejected alternatives were rejected for specific reasons: a relational database was rejected if the workload is a single key lookup at massive scale (a KV store is simpler and cheaper); a KV store was rejected if the workload needs joins and transactions (a relational store gives ACID); a search engine was not chosen as the primary store because it is a derived, eventually-consistent projection, not a source of truth.
## 15. Caching strategy
We *are* the cache; internally:
- **LRU eviction** under memory pressure; **TTL expiry** by time.
- **Stampede protection**: on a hot miss, request **coalescing** (one fetch, others wait) —
  the client library or node serializes a single "load-from-DB" per key.
- **Hot-key offloading**: a key driving >X% of a node's traffic is **replicated to extra
  nodes** (read replicas) so no single node absorbs it.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default (simple, lazy); write-through is used where read-after-write consistency is required; write-behind is used only where durability can be deferred. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.
## 16. Partitioning strategy
Consistent hashing on the key with vnodes (see `consistent_hashing.py`). Adding a node
moves only the keys near its ring position (~keys/N), not the whole keyspace. Vnodes
spread load so a new node doesn't dump all its keys onto one neighbor. Hot keys are handled
by extra replication, not by re-sharding (sharding can't fix a single hot key).

The partition key is chosen to co-locate related data (so queries do not fan out) while distributing load evenly (so no shard is hot). Consistent hashing with virtual nodes is used to minimize data movement when nodes are added or removed. A hot key (a viral entity or a giant tenant) is mitigated by caching, extra replication, or key splitting -- not by adding more shards, which does not help a single hot key.
## 17. Replication strategy
- **Primary-replica (leaderless-ish), async** by default: primary owns writes, fans to 2
  replicas. RF=3 tolerates one node loss with two survivors.
- **Sync option** for keys needing stronger durability (wait for ≥1 replica ack).
- **Failover**: if the primary dies, the next replica in the ring becomes primary; the
  ring is rebalanced so a new replica is recruited.

Replication is synchronous on the write-confirmation path where durability is critical (the commit waits for at least one follower) and asynchronous elsewhere for throughput. The replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested (not just configured): a follower that was never promoted will fail when you need it most. Cross-region replication is asynchronous with a documented RPO.
## 18. Consistency model
- **Per-key linearizability** through the primary: a `SET` then `GET` routed to the primary
  always sees the latest value.
- **Replica reads** are eventually consistent (bounded by replication lag); used for
  read scale and hot-key offloading, accepting staleness.
- **Read-your-writes**: default to primary reads for the owning client; replica reads are
  opt-in per call (tunable consistency).

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately (by routing to the leader or via a session token). Eventual consistency is bounded (seconds, not unbounded) and monitored. The system documents what eventual means to users, rather than hiding it.
## 19. Failure scenarios
| Failure | Response |
|---------|---------|
| Primary down | Promote next replica to primary; recruit a new replica; rebalance. |
| Replica down | Recruit another node as replica; backfill from primary. |
| Network split | Each side serves owned keys; writes to keys whose primary is on the other side fail over to a replica (with a risk of brief divergence, resolved by primary re-merge on heal). |
| Hot key | Extra read replicas for that key; coalescing on misses. |
| Rebalance storm | Throttle key migration; serve from old owner until moved. |

```mermaid
%% created-for: system-design-mastery
flowchart LR
  F{"Failure"}
  F -->|"primary down"| Promote["next replica -> primary"]
  F -->|"replica down"| Recruit["recruit + backfill"]
  F -->|"split"| Side["each side serves owned keys"]
  F -->|"hot key"| Extra["extra read replicas"]
  Promote & Recruit --> Heal["re-merge on heal"]
```

Each failure scenario has a documented response: which component detects it, how failover happens (automatic vs manual), what the user experiences (degraded vs error), and how recovery is verified. The design principle is that a single failure should degrade, not cascade; bulkheads and circuit breakers prevent one slow dependency from exhausting shared resources. Cascading failure is the most dangerous mode and is prevented by timeouts on every outbound call.
## 20. Reliability strategy
- SLI: get/set success rate, latency p99; SLO 99.9% availability, p99 < 2 ms.
- RF=3 tolerates one node loss per key; stateless clients retry to replicas on failure.
- Backpressure: node caps concurrent ops; rejects with `OVERLOADED` rather than melting.
- Chaos: kill a node and assert the cluster keeps serving (some misses, no outage).
- Graceful degradation: on a miss or failure, return `MISS` so callers fall back to the DB
  rather than the cache failing the request.

The SLO defines what good means measurably; the error budget (1 - SLO) is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering (kill a node, add latency, drop traffic) to verify the resilience assumptions hold. An untested failover is not a failover; an untested backup is not a backup.
## 21. Security considerations
- Authenticate clients (mTLS / shared token) — a cache is often on a trusted net but should
  not be open.
- Per-tenant quotas and keyspace prefixing to prevent cross-tenant access and noisy-neighbor
  eviction.
- No sensitive data in logs; values are opaque bytes.
- Rate limiting per client to prevent cache-flooding DoS.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed: on any error, the system refuses to act rather than allowing an unguarded action. High-risk operations (firmware changes, routing changes, firewall changes) require human approval, never autonomous execution.
## 22. Observability strategy
- Golden signals per node: ops/s, latency, errors (`OVERLOADED`/timeouts), saturation (memory
  utilization, eviction rate).
- Cluster metrics: hit ratio, hot-key ranking, rebalance throughput, replication lag.
- Tracing: per-request correlation ID through client→primary→replicas.
- Alerts: hit-ratio drop, eviction spike, replication-lag, node flapping.

Observability uses the three signals (logs, metrics, traces) with correlation IDs to stitch a request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard; RED and USE methods provide service-level and resource-level views respectively. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.
## 23. Cost considerations
- Memory is the dominant cost; size each node to its working set + headroom + replicas.
- Egress is small (values are small); cost is RAM, not bandwidth.
- Avoid over-replication of cold keys; tune RF and eviction to keep only the hot working set.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are: caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric (cost per request, cost per tenant, cost per outcome) and alerted on when unit cost spikes.
## 24. Scaling stages

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: single node<br/>(dev)"]
  S1 -->|"load grows"| S2["Stage 2: sharded ring<br/>+ RF=3"]
  S2 -->|"hot keys"| S3["Stage 3: hot-key extra replicas<br/>+ coalescing"]
  S3 -->|"global"| S4["Stage 4: region-local caches<br/>+ cross-region fill-on-miss"]
  S4 -->|"durability needs"| S5["Stage 5: optional async disk<br/>snapshot for warm restart"]
```

The scaling stages are triggered by specific thresholds, not by calendar. Stage 1 (single region) handles initial load; Stage 2 (sharding, read replicas) is triggered when a single node saturates; Stage 3 (multi-region) is triggered when latency to distant users exceeds the SLO; Stage 4 (edge, viral-key handling) is triggered when hot keys or viral spikes threaten the origin. Each stage is a deliberate architectural change, not a knob to turn.
## 25. Trade-offs
| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Partitioning | consistent hashing + vnodes | fixed ranges | minimal movement; balances uneven nodes |
| Replication | async primary-replica, RF=3 | sync everywhere | latency; sync reserved for keys needing durability |
| Read consistency | primary default, replica opt-in | always primary | balance read scale vs read-your-writes |
| Durability | replication only | disk WAL | we're a cache; DB is source of truth |
| Eviction | LRU + TTL | no eviction | memory is finite; unbounded = OOM |

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct; it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented, not hand-waved.
## 26. Alternative designs
- **Client-side caching (no cluster)**: each app caches locally. Rejected: no sharing across
  instances; huge memory waste; coherence problems.
- **Memcached-style: no replication, just sharding**: simpler, but a node loss evicts its
  keys (a thundering herd to the DB). We add replication to avoid that cliff.
- **A single managed Redis cluster**: fine operationally; rejected here because we're
  designing the mechanics to teach partitioning/replication/failover.

The alternative designs are not strawmen; they are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements (latency SLO, cost budget, consistency need) that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.
## 27. Interview discussion points
- Clarify: is this a cache (DB is source of truth) or a store (we own durability)? That
  changes everything.
- The key ambiguity is the read:write ratio and hot-key behavior; surface it early.
- Depth cue: a strong candidate discusses consistent hashing + vnodes, RF vs availability,
  hot-key mitigation, and the stampede problem.
- Watch for: jumping to a single Redis without discussing sharding/failover/hot keys.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply (not just draw boxes), discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.
## 28. Original Mermaid diagrams

Standalone sources under `diagrams/case-studies/distributed-cache/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. Request sequence and failure flow:

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant P0 as Client
  participant P1 as Distributed Cache
  participant P2 as Store
  P0 ->> P1: query
  P1 ->> P2: look up or fetch
  P2 ->> P1: data
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
  C1["F -"]
  R2["primary down Promote next replica -> pri"]
  C1 --> R2
  C3["F -"]
  R4["replica down Recruit recruit backfill"]
  C3 --> R4
  C5["F -"]
  R6["split Side each side serves owned keys"]
  C5 --> R6
  C7["F -"]
  R8["hot key Extra extra read replicas"]
  C7 --> R8
```

## 29. Further reading
Consistent hashing: S-CHASH · Dynamo: S-DYNAMO · Redis: S-REDIS · gossip: S-GOSSSIP ·
consistent_hashing.py simulation in `examples/`.

The further reading cites primary sources (RFCs, papers, official documentation) via stable IDs in SOURCES.md, not secondary blog posts or vendor marketing. Each citation is chosen because it is the authoritative source for a specific technical claim in the chapter, not because it is a general reference.
## 30. Practical exercises
1. Re-estimate at 1B keys with 80 GB working set. How many nodes and replicas?
2. Add a requirement: values up to 1 MB. How do large values change eviction and network?
3. Design the failover test proving a primary loss causes no data loss and <1 s of misses.
4. A single key drives 10% of traffic. Walk through every mitigation and its limits.
5. Add multi-region: what changes about consistency, fill-on-miss, and egress cost?

---
Previous: [URL shortener](../beginner/url-shortener.md) · Next: (next intermediate case study)

The exercises are designed to push the reader beyond the v1 design: re-estimating at 10x scale reveals capacity limits; adding a new requirement (expiry, E2E, multi-region) forces an architectural change; designing the failover test reveals whether the resilience claims are real. The exercises are open-ended because system design is about reasoning, not memorization.
