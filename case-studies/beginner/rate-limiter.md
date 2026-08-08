# Case Study: Rate Limiter

> **Tier:** beginner · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Protect a service from abuse/overload by limiting request rate per client/tenant. A
foundational component reused across gateways. (See `examples/rate_limiter.py`.) This is a beginner-tier system design challenge because it must handle high availability under peak load while ensuring sub-millisecond response times. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
**In (v1):** per-client fixed-window and token-bucket limiting at the edge. **Out:**
distributed global counters, adaptive/AI-based limiting, per-endpoint dynamic limits.

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Limit requests per client key to R per second. - Return 429 with Retry-After when
exceeded. - Allow a burst up to bucket capacity. - Report current usage.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Decision p99 < 1 ms (in the hot path). - Availability 99.95% (fail-open if limiter down
to avoid blocking all traffic). - Highly read/write symmetric (every request is a check
+ update).

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 100k clients; default 100 req/s, burst 200. [assumption] 2. 50k RPS through the gateway.
[assumption] 3. Limits per (client, endpoint). [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
- 50k RPS, each = 1 limiter check+update = 100k ops/s to the limiter store. Hot keys: the
busiest tenants dominate.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Rate Limiter, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
- Per-key state tiny (counters/timestamps). Millions of keys × ~50 B = MBs; in-memory.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
- Negligible; limiter calls are local/in-cluster, sub-KB.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Rate Limiter, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| CHECK | (client, endpoint) | — | ALLOW/DENY, retry-after | The gateway calls the limiter
inline before forwarding.

## 10. Data model
Token bucket per key: `(tokens, last_refill_ts)`. In-memory store (Redis-like) keyed by
(client,endpoint).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture
```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> GW["Gateway"]
  GW --> RL["Rate limiter - in-process + shared store"]
  RL --> Store["Counter/bucket store"]
  RL -->|"allow"| Svc["Backend"]
  RL -->|"deny (429)"| Client
```

## 12. Request flow
Gateway extracts (client, endpoint) → limiter checks/refills the bucket → if tokens ≥ 1,
consume and allow; else return 429 with Retry-After.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Gateway
  participant C1 as Rate limiter in-process
  participant C2 as Counter bucket store
  participant C3 as Backend
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
Gateway: enforce the limit decision. Limiter: bucket logic. Store: shared counters across
gateway replicas.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
In-memory KV (Redis) for shared counters across replicas; in-process cache for the hottest
keys to cut latency. Rejected: SQL (too slow per request).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
In-process token-bucket approximation for hot keys; sync to shared store periodically. A
client's bucket pinned to a gateway instance reduces shared-store load (sticky-ish).

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Shard the counter store by key hash; hot tenants get dedicated/partitioned capacity. A
single hot key is a counter, not data — mitigate by partitioning counters per client.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Counters are ephemeral state; replicate for availability, accept that a failover resets a
bucket (a brief over-allow) — preferable to blocking traffic.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Approximate: a per-second limit may be slightly exceeded under replica failover or
in-process caching. Exactness traded for latency and availability; documented.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Limiter store down → fail-open (allow) to avoid blocking all traffic; degrade protection,
not availability. In-process cache skew → slight over-allow on some gateways.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Limiter store down"]
  R2["fail-open allow to avoid blocking all tr"]
  C1 --> R2
  C3["In-process cache skew"]
  R4["slight over-allow on some gateways"]
  C3 --> R4
```

## 20. Reliability strategy
SLI: 429 correctness, p99 latency; SLO 99.95%. Fail-open policy. Chaos: kill the store,
assert traffic flows (over-allowing, not blocking).

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Fail-open vs fail-closed: for a *protection* limiter, fail-open is safer for availability
but risks overload — combine with downstream load shedding (Level 6). Don't trust a
client-supplied key.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Track allow/deny ratio, 429 rate per client, limiter latency; alert on deny spikes
(possible abuse or attack) and on limiter-store latency.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
In-memory store; cost ~ RAM. Cost is small; the value is protecting everything downstream.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: in-process buckets per gateway. → Stage 2: shared store for cluster-wide limits.
→ Stage 3: per-tenant dedicated capacity for hot tenants. → Stage 4: adaptive limits from
observed load.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: in-process buckets per gateway."]
  S2["Stage 2: shared store for cluster-wide limits."]
  S3["Stage 3: per-tenant dedicated capacity for hot te"]
  S4["Stage 4: adaptive limits from"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Exact vs approximate: approximate is far cheaper and fits a protection limiter. Fail-open
vs fail-closed: fail-open preserves availability. Shared store vs in-process: shared for
cluster-wide, in-process for latency.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Fixed-window (simple, boundary bursts); token bucket (chosen: burst-friendly). Global
exact counter via consensus (rejected: too slow for the hot path).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify limits, burst, distributed vs per-instance, fail-open policy. Surface the
latency/availability-vs-exactness trade.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/rate-limiter/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Resilience patterns: Level 5; load shedding: Level 6; rate_limiter.py. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises
1. Add a sliding-window limiter; what changes in storage? 2. Design a global cluster-wide
limit. 3. Add adaptive limits based on backend latency. 4. What if fail-open caused an
overload? Combine with what? 5. Handle a single client doing 80% of traffic.

---
Previous: [Paste service](paste-service.md) · Next: [Web crawler](web-crawler.md)

