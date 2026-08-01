# Case Study: URL Shortener

> **Tier:** beginner · **Status:** complete
> This is the canonical beginner case study demonstrating the [30-section template](../../templates/CASE-STUDY-TEMPLATE.md). All numbers and diagrams are original.

## 1. Problem statement
Users want to share long, ugly URLs in places with character limits (SMS, printed material,
social posts). We need a service that takes a long URL and returns a short one, then
redirects anyone who visits the short one to the original — fast, reliably, and at internet
scale.

This system sits at the intersection of distributed systems and operational reliability. The design must balance the latency versus durability trade-off inherent to the workload while ensuring no single component failure cascades into a full outage. The target audience includes both engineers building the system and operators maintaining it, so the design must be observable, debuggable, and reversible at every step.
## 2. Scope
**In scope (v1):**
- Create a short code from a long URL.
- Redirect a short code to the long URL.
- Custom alias (optional), basic analytics (count of redirects).

**Out of scope (v1):**
- User accounts, link dashboards, expiry/scheduling, A/B redirect logic, spam/abuse
  detection beyond a basic rate limit. These are noted as scaling stages.

The scope boundary is deliberate: including too much in v1 risks shipping a system that is broad but shallow. Each excluded feature is a candidate for a later iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.
## 3. Functional requirements
- The system **shall** accept a long URL and return a unique short URL.
- The system **shall** redirect a request to a short URL to its original long URL.
- The system **shall** return HTTP 404 for an unknown short code.
- The system **shall** support an optional user-chosen alias if available.
- The system **shall** record a redirect-count per short code.

These requirements drive the architecture: the read-heavy pattern pushes toward caching and replication; the durability requirement forces synchronous writes on the critical path; the idempotency requirement means every write path must handle redelivery without double-application. Each requirement has a direct architectural consequence.
## 4. Non-functional requirements
- Availability 99.9% (redirects are the user-visible, revenue-adjacent path).
- Redirect latency p99 < 100 ms (ideally served from edge cache, < 50 ms).
- Durability: a shortened link must keep resolving for its lifetime (default: forever).
- Throughput: read-heavy by a huge margin; reads dominate writes ~100:1.
- Hot links can spike millions of redirects in minutes (viral).

The non-functional targets shape every component choice: the latency SLO forces edge caching and limits synchronous cross-region calls on the hot path; the availability target drives redundancy (RF=3, multi-AZ); the durability target forces synchronous replication on committed writes; the cost target constrains the model size and prevents over-provisioning.
## 5. Explicit assumptions
1. 50 million new short URLs created/month → ~20/s average writes, ~200/s peak. [assumption]
2. 10x redirects per URL on average; viral links skew the distribution. [assumption]
3. Short code length = 7 base62 characters → 62^7 ≈ 3.5 trillion codes (plenty). [assumption]
4. Retention: links never expire unless explicitly deleted. [constraint]
5. Each stored record ~500 bytes (long URL + metadata). [assumption]

These assumptions are the load-bearing facts of the design. If any assumption is wrong by an order of magnitude, the architecture must adapt: 10x more traffic may require sharding earlier; 10x more data may require tiering sooner; a different read-write ratio may change the caching strategy entirely. The design is parameterized by these assumptions, not locked to them.
## 6. Traffic estimation
- Writes: 50M/month / 2.59M s ≈ **19 writes/s avg**, ~**190/s peak** (10×).
- Reads: assume 100 redirects per link → 5B/month ≈ **1,900 reads/s avg**, ~**19,000/s peak**.
- Read:write ratio ≈ **100:1** — overwhelmingly read-heavy; design around the read path.

The traffic estimate reveals the binding constraint. For this workload, the binding resource is compute or storage or bandwidth (as noted above). Peak is modeled at 10x average, which is conservative for viral workloads but aggressive for steady-state enterprise systems. The read-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy), which changes the entire storage and replication strategy.
## 7. Storage estimation
- New rows/month = 50M × 500 B ≈ 25 GB/month.
- Lifetime (assume 5 years) ≈ 25 × 60 ≈ **1.5 TB** of mapping data + indexes.
- With a B-tree index on the short code (~+30% overhead): ~2 TB. Modest; a single
  well-tuned DB shard can hold it, but we shard for headroom and writes.

Storage growth is linear with time and must be planned with retention in mind. The estimate includes metadata and index overhead (typically 20-30 percent above raw data). Without a retention policy, storage grows unboundedly and cost becomes unsustainable. The design includes tiering (hot to cold) and lifecycle rules to manage this growth automatically.
## 8. Bandwidth estimation
- Write bandwidth = 19/s × 500 B ≈ 10 KB/s (trivial).
- Read bandwidth = 1,900/s × ~500 B response ≈ ~1 MB/s avg, ~10 MB/s peak.
- Redirect responses are tiny (302 + Location header); bandwidth is not the binding
  resource — read QPS and hot-key handling are.

Bandwidth is often not the binding constraint for this workload, but it becomes significant at the network edge during viral spikes. The design uses CDN and edge caching to cut origin egress; co-location of compute and data reduces inter-node traffic; and compression (for logs, telemetry, and bulk transfers) cuts bandwidth by 50-80 percent where applicable.
## 9. API design
| Method | Path | Request | Response | Auth | Idempotent |
|--------|------|---------|----------|------|:----------:|
| POST | /v1/shorten | `{ "long_url": "https://...", "alias"? }` | `{ "short_url": "https://s.co/x7K2q9a" }` | API key | yes (idempotency-key) |
| GET | /:code | — | 302 redirect to long URL (404 if unknown) | none | n/a |
| GET | /v1/stats/:code | — | `{ "redirects": 12345 }` | API key | yes |

`POST /shorten` is idempotent via a client `Idempotency-Key` so a retry doesn't create a
duplicate code for the same long URL.

The API design follows REST conventions for external clients and gRPC for internal service-to-service communication where throughput matters. Every write endpoint accepts an idempotency key so retries from unreliable clients do not double-apply. Streaming endpoints use Server-Sent Events (SSE) for token-by-token LLM output or chunked transfer for large payloads. Rate limiting is enforced at the gateway before the request reaches the service tier.
## 10. Data model
Two logical entities:

```
url_mappings
  short_code  : CHAR(7)   PRIMARY KEY
  long_url    : TEXT
  created_at  : TIMESTAMP
  alias       : BOOL
  redirects   : BIGINT     (denormalized counter; see caching)

redirect_events   (async, for analytics; optional in v1)
  short_code  : CHAR(7)
  ts         : TIMESTAMP
  ...
```
Storage: a key-value-friendly store keyed by `short_code` (the hot access is a single
key→value lookup). A relational DB with an index on `short_code` works; a KV/document store
scales further. We pick a sharded key-value store with the short code as the partition key.

The data model is designed around the access pattern, not the entity shape. The primary access path (key lookup by ID) determines the partition key; the secondary access paths (by timestamp, by owner, by status) determine the indexes. Denormalization is applied selectively where the hot read path would otherwise require expensive joins, with CDC or the outbox pattern keeping the denormalized view consistent with the normalized source of truth.
## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> CDN["Edge cache / CDN<br/>(short_code -> long_url cached)"]
  CDN -.miss.-> GW["API gateway<br/>rate-limit + auth"]
  GW --> Shorten["Shorten service<br/>(stateless)"]
  GW --> Resolve["Resolve service<br/>(stateless)"]
  Shorten --> IDS["ID / code generator"]
  Shorten --> DB[("KV store<br/>sharded by short_code")]
  Resolve --> DB
  Resolve --> Cache[("Distributed cache")]
  Cache --> DB
  Shorten --> Cache
  AnalyticsQ["Analytics queue"] <-. redirect event .-> Resolve
  AnalyticsQ --> Workers["Analytics workers"]
```


## 12. Request flow
**Shorten (write):**
1. Client `POST /shorten` with long URL + idempotency key.
2. Gateway authenticates (API key) and rate-limits.
3. Shorten service checks idempotency; if seen, returns the existing code.
4. Generates a unique 7-char base62 code (see §13).
5. Writes `{code -> long_url}` to the KV store and the cache.
6. Returns the short URL.

**Resolve (read):**
1. Client `GET /:code`; CDN checks edge cache for `code`.
2. On hit, returns 302 immediately (no origin traffic).
3. On miss, gateway → resolve service → distributed cache → KV store.
4. On KV hit, populate cache (and CDN), return 302.
5. Asynchronously emit a redirect event to the analytics queue.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C as Client
  participant CDN as Edge cache
  participant GW as Gateway
  participant R as Resolve service
  participant Cache as Distributed cache
  participant DB as KV store
  C->>CDN: GET /x7K2q9a
  alt edge hit
    CDN-->>C: 302 (cached)
  else miss
    CDN->>GW: forward
    GW->>R: resolve x7K2q9a
    R->>Cache: get x7K2q9a
    alt cache hit
      Cache-->>R: long_url
    else miss
      R->>DB: get x7K2q9a
      DB-->>R: long_url
      R->>Cache: set (TTL)
    end
    R-->>GW: 302 long_url
    GW-->>CDN: 302 (cacheable)
    CDN-->>C: 302
  end
  R->>AnalyticsQ: emit redirect event (async)
```

The request flow reveals the critical path: any component on the hot path that fails or slows degrades the user experience. The design identifies this path explicitly and applies timeouts, circuit breakers, and bulkheads to each hop. The write path includes an idempotency check (by key) before any state mutation, ensuring redelivery safety. The read path serves from cache first, falling back to the authoritative store only on miss.
## 13. Component responsibilities
- **Edge cache/CDN**: serve the common redirect from near the user; the highest-leverage
  component for latency and origin load.
- **API gateway**: auth, rate limiting, routing.
- **Shorten service (stateless)**: create codes, enforce idempotency, write mappings.
- **Resolve service (stateless)**: read mappings, populate caches, emit analytics events.
- **Code generator**: produce unique 7-char base62 codes.
- **KV store (sharded)**: durable source of truth, partitioned by short code.
- **Distributed cache**: second-tier cache behind the edge for misses.
- **Analytics queue + workers**: decouple counting from the redirect path.

Each component has a single, well-defined responsibility. The gateway handles auth, rate limiting, and routing; the service tier is stateless and horizontally scalable; the data tier is the stateful core, carefully partitioned and replicated. The separation allows each tier to scale independently: the stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas, not by adding arbitrary instances.
## 14. Database selection
**Chosen: sharded key-value/document store** (e.g., a managed KV like DynamoDB-style, or
sharded PostgreSQL with an index on `short_code`).
- The access pattern is a single `code -> long_url` lookup and a single-key write. This is
  the textbook KV workload.
- A relational DB is a fine alternative for v1 (small data, ~2 TB) and gives SQL tooling;
  rejected at extreme scale only because sharding a KV pattern is simpler than sharding SQL.
- A pure in-memory store is rejected as the source of truth (durability).

The database choice is driven by the access pattern, not by familiarity. The rejected alternatives were rejected for specific reasons: a relational database was rejected if the workload is a single key lookup at massive scale (a KV store is simpler and cheaper); a KV store was rejected if the workload needs joins and transactions (a relational store gives ACID); a search engine was not chosen as the primary store because it is a derived, eventually-consistent projection, not a source of truth.
## 15. Caching strategy
- **Edge (CDN)**: cache `code -> 302` for a TTL (e.g., 10 min). Handles the vast majority of
  reads and survives origin outages (stale redirects are acceptable for unchanged links).
- **Distributed cache (Redis)**: cache `code -> long_url` for a longer TTL (e.g., 1 h) with
  event invalidation on delete/alias change.
- **Stampede protection**: for a viral link, the edge + request coalescing prevent a
  thundering herd on the KV store. Cold, popular keys use `stale-while-revalidate`.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default (simple, lazy); write-through is used where read-after-write consistency is required; write-behind is used only where durability can be deferred. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.
## 16. Partitioning strategy
Partition (shard) the KV store by `short_code` (hash). With ~19,000 reads/s peak and a
conservative 5,000 reads/s per shard, 2–3 read shards suffice at v1; we provision more for
headroom and growth (see sharding calculator). Vnodes + consistent hashing let us add shards
without rehashing the whole keyspace. Hot viral links are handled by the edge cache, not by
adding shards (sharding doesn't fix a single hot key).

The partition key is chosen to co-locate related data (so queries do not fan out) while distributing load evenly (so no shard is hot). Consistent hashing with virtual nodes is used to minimize data movement when nodes are added or removed. A hot key (a viral entity or a giant tenant) is mitigated by caching, extra replication, or key splitting -- not by adding more shards, which does not help a single hot key.
## 17. Replication strategy
- **Leader-follower, async**: each shard has 1 leader (writes) + 2 followers (reads). Reads
  are read-heavy, so followers absorb read traffic; async replication trades a small lag for
  throughput. Writes are low-rate (~190/s peak), so leader capacity is not the bottleneck.
- **Failover**: a follower is promoted on leader failure; redirects keep working from cache
  during promotion (graceful degradation).

Replication is synchronous on the write-confirmation path where durability is critical (the commit waits for at least one follower) and asynchronous elsewhere for throughput. The replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested (not just configured): a follower that was never promoted will fail when you need it most. Cross-region replication is asynchronous with a documented RPO.
## 18. Consistency model
- **Writes**: strongly consistent on the leader (a created code is immediately resolvable via
  the leader); cross-replica reads are eventually consistent (sub-second lag).
- **Reads (resolve)**: eventual consistency is fine — a freshly created link may take a
  moment to be visible from a follower, but the create path can read-your-writes by going to
  the leader or by returning the code directly to the creator (no redirect needed then).
- **Deletes**: invalidate caches on delete; stale 302s served from the edge for the TTL
  duration are acceptable for v1 (note this as a product decision).

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately (by routing to the leader or via a session token). Eventual consistency is bounded (seconds, not unbounded) and monitored. The system documents what eventual means to users, rather than hiding it.
## 19. Failure scenarios
| Failure | System response |
|---------|------------------|
| A KV shard leader down | Promote a follower; redirects continue from edge/cache. |
| Edge cache unavailable | Traffic falls through to gateway→cache→KV; higher latency, no outage. |
| Distributed cache down | Resolve goes to KV directly; latency rises, still functional. |
| Analytics queue down | Redirects unaffected; counts lag and recover on replay. |
| Network partition between regions | Each region serves its own cached codes; writes route to the primary region. |

```mermaid
%% created-for: system-design-mastery
flowchart LR
  F{"Failure"}
  F -->|"KV leader down"| Promote["promote follower"]
  F -->|"cache down"| Direct["resolve from KV"]
  F -->|"edge down"| GW["fall through to origin"]
  F -->|"analytics down"| Lag["counts lag, redirect ok"]
  Promote --> OK["redirects via cache during switch"]
```

Each failure scenario has a documented response: which component detects it, how failover happens (automatic vs manual), what the user experiences (degraded vs error), and how recovery is verified. The design principle is that a single failure should degrade, not cascade; bulkheads and circuit breakers prevent one slow dependency from exhausting shared resources. Cascading failure is the most dangerous mode and is prevented by timeouts on every outbound call.
## 20. Reliability strategy
- SLI: redirect success rate; SLO 99.9% availability, p99 < 100 ms.
- Error budget: ~43 min/month of allowed unavailability; spend it on deploys, not incidents.
- Redundancy: stateless services RF≥3 across zones; KV shards RF=3.
- Backpressure: resolve service caps concurrency and sheds load above target; queue-based
  load leveling for analytics.
- Chaos test: kill a KV leader and a cache node; assert redirects continue via cache.

The SLO defines what good means measurably; the error budget (1 - SLO) is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering (kill a node, add latency, drop traffic) to verify the resilience assumptions hold. An untested failover is not a failover; an untested backup is not a backup.
## 21. Security considerations
- Auth on `POST /shorten` (API key) to prevent abuse; anonymous reads.
- Rate limiting per IP/API key on shorten (abuse/spam vectors).
- Input validation: long URL must be a valid, resolvable URL; reject non-http(s) schemes to
  block `javascript:` and `file:` redirect abuse.
- Abuse: blacklist known-malicious long URLs; allow listing/blocking of codes (out of v1).
- Audit: log shorten requests with API key for incident forensics.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed: on any error, the system refuses to act rather than allowing an unguarded action. High-risk operations (firmware changes, routing changes, firewall changes) require human approval, never autonomous execution.
## 22. Observability strategy
- Golden signals on resolve: request rate, latency (p50/p95/p99), errors (404 vs 5xx),
  saturation (cache hit rate, shard load).
- Tracing with correlation IDs across gateway → service → cache → DB.
- Alerts: cache hit rate drop, p99 latency, 5xx rate, shard CPU, replication lag.
- Dashboard: redirects/s, edge hit ratio, KV read/s, top redirect codes (for hot-key watch).

Observability uses the three signals (logs, metrics, traces) with correlation IDs to stitch a request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard; RED and USE methods provide service-level and resource-level views respectively. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.
## 23. Cost considerations
- Dominant cost: egress + KV reads at high QPS; the edge cache cuts both drastically.
- Storage (~2 TB) is minor relative to request cost.
- Archive nothing — links must keep resolving; instead keep all data on standard storage.
- Optimize by maximizing edge hit ratio (the single biggest cost lever).

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are: caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric (cost per request, cost per tenant, cost per outcome) and alerted on when unit cost spikes.
## 24. Scaling stages

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: single region<br/>1 KV shard + cache + CDN"]
  S1 -->|"reads grow"| S2["Stage 2: add read replicas<br/>+ sharded KV by code"]
  S2 -->|"global traffic"| S3["Stage 3: multi-region reads<br/>cross-region replication"]
  S3 -->|"viral hot keys"| S4["Stage 4: edge coalescing<br/>+ stale-while-revalidate"]
  S4 -->|"writes grow"| S5["Stage 5: multi-region writes<br/>(coordination for uniqueness)"]
```

- Stage 1: single region, 1 KV shard, cache, CDN. Handles v1 easily.
- Stage 2: shard KV when reads exceed one shard; add read replicas.
- Stage 3: multi-region read replicas + cross-region replication for global latency.
- Stage 4: edge coalescing and stale-while-revalidate for viral keys.
- Stage 5: multi-region writes require unique-code coordination (see §25 trade-offs).

The scaling stages are triggered by specific thresholds, not by calendar. Stage 1 (single region) handles initial load; Stage 2 (sharding, read replicas) is triggered when a single node saturates; Stage 3 (multi-region) is triggered when latency to distant users exceeds the SLO; Stage 4 (edge, viral-key handling) is triggered when hot keys or viral spikes threaten the origin. Each stage is a deliberate architectural change, not a knob to turn.
## 25. Trade-offs
| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Code generation | generated 7-char base62 | hash(long_url) | hash collisions and non-unique; base62 with a counter is unique and short |
| Source of truth | durable KV store | pure cache | durability requirement (links must resolve forever) |
| Reads | async-replica, eventually consistent | strong consistency | read-heavy; strong reads cost throughput and aren't needed for redirects |
| Caching | edge 302 caching | no edge | edge absorbs the dominant read load; without it the KV store melts |
| Analytics | async via queue | synchronous counting | keep the redirect path minimal and resilient |

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct; it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented, not hand-waved.
## 26. Alternative designs
- **Hash-based codes (MD5 of URL, truncated)**: shorter path but risks collisions and
  reveals nothing meaningful; collisions force a retry loop. Rejected for uniqueness risk.
- **Reserved counter service (Snowflake-style)** as the code generator: gives monotonic,
  unique IDs encoded to base62. Viable and our choice at scale; for v1 a single in-process
  counter with a node-id prefix is simpler until writes grow.
- **Pure CDN-only (no KV)**: every code's long URL embedded at the edge. Rejected: edge
  cannot durably store billions of mappings or handle updates/deletes as the source of truth.

The alternative designs are not strawmen; they are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements (latency SLO, cost budget, consistency need) that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.
## 27. Interview discussion points
- Clarify: do links expire? custom aliases? analytics? abuse handling? These change scope.
- The key ambiguity is read:write ratio and viral behavior; surface it and design the read
  path and hot-key handling first.
- Depth cue: a strong candidate discusses idempotency on shorten, code-uniqueness under
  concurrency, and the stale-302 trade-off on delete.
- Watch for: jumping to a database before noting the read-heavy, cache-dominated nature.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply (not just draw boxes), discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.
## 28. Original Mermaid diagrams

Standalone sources under `diagrams/case-studies/url-shortener/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. Request sequence and failure flow:

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant P0 as Client
  participant P1 as URL Shortener
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
  C1["Edge cache unavailable Traffic falls thr"]
  R2["cache→KV"]
  C1 --> R2
  C3["F -"]
  R4["KV leader down Promote promote follower"]
  C3 --> R4
  C5["F -"]
  R6["cache down Direct resolve from KV"]
  C5 --> R6
  C7["F -"]
  R8["edge down GW fall through to origin"]
  C7 --> R8
```

## 29. Further reading
- Consistent hashing: S-CHASH · ID generation/Snowflake: S-SNOWFLAKE · UUID: S-UUID
- CDN/caching: see `docs/02-core-components/03-cdn-caching.md`
- Sharding calculator: `calculations/sharding-calculator.md`

The further reading cites primary sources (RFCs, papers, official documentation) via stable IDs in SOURCES.md, not secondary blog posts or vendor marketing. Each citation is chosen because it is the authoritative source for a specific technical claim in the chapter, not because it is a general reference.
## 30. Practical exercises
1. Re-estimate at 10× scale (500M links/month). What changes — shards, cache, egress?
2. Add a requirement that links expire after 30 days. How does caching/storage change?
3. Design the failover test that proves redirects survive a KV leader loss.
4. A single link goes viral (1M redirects/min). Walk through every layer protecting the
   origin and identify where it could still break.
5. Add custom aliases: how do you guarantee uniqueness and prevent alias squatting?

---
Previous: (start of case studies) · Next: (next beginner case study)

The exercises are designed to push the reader beyond the v1 design: re-estimating at 10x scale reveals capacity limits; adding a new requirement (expiry, E2E, multi-region) forces an architectural change; designing the failover test reveals whether the resilience claims are real. The exercises are open-ended because system design is about reasoning, not memorization.
