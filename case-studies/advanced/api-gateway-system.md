# Case Study: API Gateway

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
A single entry point for a fleet of APIs: auth, rate limit, routing, transformation, and aggregation — a high-QPS, policy-heavy edge. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): auth, rate limit, route, transform, aggregate, observability. Out: full BFF logic (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Authenticate/authorize requests.
- Rate-limit per client/tenant.
- Route to backends.
- Transform request/response.
- Aggregate multiple backends.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- p99 < 50 ms overhead.
- Availability 99.95% (it's the front door).
- High QPS; horizontally scalable.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 100k RPS, 50 backends. [assumption] 2. Mostly stateless routing. [assumption] 3. Policy config hot-reloadable. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
100k RPS; every request passes through. The gateway is on the critical path of everything.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For API Gateway, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Config (routes, quotas) small; rate-limit counters ephemeral. Negligible durable storage.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
In+out equals backend traffic; the gateway is a pass-through — bandwidth is whatever the fleet moves.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For API Gateway, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

The gateway itself is the API; backends are internal.

## 10. Data model
routes(host,path -> backend, policy); quotas(client, limit); counters(client, window).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> GW[Gateway]
  GW --> Auth[AuthN/Z]
  GW --> RL[Rate limiter]
  GW --> Route[Router]
  Route --> B1 & B2 & B3
  GW --> Agg[Aggregator] --> B1 & B2
  Config[Policy config] -.hot reload.-> GW
```

## 12. Request flow
Request -> auth -> rate-limit -> route (or aggregate fan-out) -> backend(s) -> transform response -> client. Config hot-reloads without dropping requests.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Gateway
  participant C1 as AuthN Z
  participant C2 as Rate limiter
  participant C3 as Router
  participant C4 as Aggregator
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
Auth, rate limiter, router, transformer, aggregator, config service, counter store.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Config in a KV with hot reload; rate-limit counters in a fast in-memory store. Rejected: per-request DB lookup for routing.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Route config cached in-process (hot-reload); rate-limit hot keys in-process; response caching for cacheable endpoints.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Counters sharded by client; gateway instances stateless behind a LB; config pushed to all.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Gateway stateless (RF = instances); counter store replicated; config replicated.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Config eventually consistent across instances (a route change propagates in seconds). Counters approximate.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Counter store down -> fail-open rate-limit (over-allow) to keep traffic flowing. Config service down -> keep last config. A backend down -> circuit-break/503.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Counter store down"]
  R2["fail-open rate-limit over-allow to keep"]
  C1 --> R2
  C3["Config service down"]
  R4["keep last config"]
  C3 --> R4
  C5["A backend down"]
  R6["circuit-break 503"]
  C5 --> R6
```

## 20. Reliability strategy
SLI overhead latency, availability; SLO 99.95%. Stateless + redundancy. Chaos: kill a gateway instance, assert no client impact.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Authn/Z at the edge; mTLS to backends; per-tenant quotas; WAF hooks; no secrets in config.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
RPS, p99 latency, 4xx/5xx, rate-limit denials, per-backend latency/errors, circuit-break trips.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Compute (always-on, critical path) + counter store. Efficiency (low overhead) directly cuts cost.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: auth+route+ratelimit. -> Stage 2: aggregation + config hot-reload. -> Stage 3: service-mesh integration + WAF. -> Stage 4: multi-region, edge auth.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: auth route ratelimit."]
  S2["Stage 2: aggregation config hot-reload."]
  S3["Stage 3: service-mesh integration WAF."]
  S4["Stage 4: multi-region, edge auth."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Centralized policy (consistency) vs a shared SPOF/bottleneck. Fail-open rate-limit (availability) vs over-allow. Aggregation (fewer client calls) vs gateway coupling.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Per-service auth (duplicated, inconsistent). Fat gateway (business logic, unmaintainable). Single instance (SPOF).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify QPS, policies, aggregation. Surface stateless edge, hot-reload config, fail-open rate-limit.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/api-gateway-system/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
API gateway: Level 2; rate limiting: Level 5; auth: Level 7. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Hot-reload config with zero dropped requests. 2. Fail-open vs fail-closed rate-limit. 3. Aggregate 3 backends within p99 budget. 4. Per-tenant quotas at 100k RPS. 5. Multi-region gateway failover.

---
Previous: Continuous integration platform · Next: Identity & access-management

