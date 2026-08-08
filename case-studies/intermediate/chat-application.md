# Case Study: Chat Application

> **Tier:** intermediate · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Real-time 1:1 and group chat: low-latency message delivery, online presence, message
history, and delivery/read receipts. A connection-stateful, latency-sensitive system. This is a intermediate-tier system design challenge because it must handle real-time latency under load while ensuring low-latency bidirectional communication. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
**In (v1):** 1:1 and small-group chat, presence, history, delivery/read receipts. **Out:**
voice/video, end-to-end encryption, large-channel fanout (noted as stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Send/receive messages in real time.
- Show presence (online/offline).
- Persist history
and load on demand. - Delivery/read receipts.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Message delivery latency < 200 ms p99.
- Availability 99.9%.
- Connection-scale: hold
millions of concurrent connections.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 10M DAU, 50 messages/user/day = 500M/day. [assumption] 2. Avg connection held 20 min;
peak 2M concurrent connections. [assumption] 3. Messages ~200 B. [assumption]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
- 500M/day ≈ 5,800 msg/s avg, ~58k/s peak. Connection-keepalive load dominates compute.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Chat Application, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
- 500M × 200 B = 100 GB/day; retain 1 year ≈ 36 TB. Hot recent history in cache.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
- 5,800 msg/s × ~200 B ≈ 1.2 MB/s avg; peak ~12 MB/s — modest; the challenge is connection
fan-out, not bytes.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Chat Application, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
WebSocket for delivery; REST for history (`GET /messages/:channel?before=`); REST for
send. Presence via the connection layer.

## 10. Data model
`messages(id, channel_id, sender, body, ts, status)`; `channels(id, type, members)`;
`presence(user_id, status, last_seen)`. History keyed/sorted by (channel, ts).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture
```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> Gateway["Connection gateway<br/> - stateful, async I/O"]
  Gateway --> Presence["Presence store"]
  Gateway --> MsgSvc["Message service"]
  MsgSvc --> Store["Message store"]
  MsgSvc --> Fanout["Fanout / channel router"]
  Fanout --> Gateway
  Client --> Hist["History API"] --> Store
```

## 12. Request flow
Send: client → gateway → message service → persist → fanout routes to each recipient's
gateway → pushed over their socket. Receipts flow back the same path. History loaded via
REST on scroll.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Connection gateway<br >
  participant C1 as Presence store
  participant C2 as Message service
  participant C3 as Message store
  participant C4 as Fanout channel router
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
Connection gateway: hold connections (stateful, async). Message service: persist + fanout.
Presence store: who's online. History API: paginated reads.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Message store: a sharded store keyed by channel, ordered by ts (Cassandra/Scylla-like or
sharded KV with ts index) — write-heavy, time-ordered. Presence: a fast in-memory store.
Rejected: a single DB (can't hold millions of connections / write rate).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Recent messages per channel cached (the common "open a chat" read). Presence cached in
memory; fall back to store.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Messages sharded by `channel_id` (co-locates a channel's history). Connection gateway
sharded by `user_id` so a user's socket lives on one node (affinity) — failover re-binds.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Messages RF=3 for durability; presence ephemeral, replicated for availability. Gateway
nodes stateless-ish except held connections; reconnect on failure (client retries).

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Within a channel: messages ordered by server-assigned monotonic ID (total order per
channel). Cross-device: eventual (a second device may lag). Presence is eventually
consistent.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Gateway node loss: clients reconnect to another; in-flight messages redelivered (at-least
-once + client dedup by id). Message store shard down → promote follower. Presence
conflict → last-seen wins.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Message store shard down"]
  R2["promote follower"]
  C1 --> R2
  C3["conflict"]
  R4["last-seen wins"]
  C3 --> R4
```

## 20. Reliability strategy
SLI delivery latency, delivery success; SLO 99.9%. At-least-once + idempotent sends.
Connection-level heartbeats to detect dead connections. Chaos: kill a gateway, assert
reconnect + redelivery.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Per-channel authorization; TLS on sockets; rate-limit sends per user; redact PII in logs;
content moderation hooks.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Active connections, msg delivery latency, delivery success, presence store latency,
reconnect rate. Alert on connection drops and delivery latency.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Connections (memory) + history storage dominate. Keep presence in-memory cheap; tier old
history to cold storage.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: gateway + message store. → Stage 2: shard by channel, connection-scale gateways.
→ Stage 3: presence fanout for large channels (read-replica presence). → Stage 4:
multi-region, large-channel fanout (Level 10).

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: gateway message store."]
  S2["Stage 2: shard by channel, connection-scale gatew"]
  S3["Stage 3: presence fanout for large channels read-"]
  S4["Stage 4: multi-region, large-channel fanout Level"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Connection-stateful gateway (unavoidable) vs stateless ideal. Total order per channel vs
global order (per-channel is cheaper). At-least-once + dedup vs exactly-once.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Polling (rejected: latency + battery). A single global message bus (rejected: can't scale
to millions of connections). CRDT for offline edits (for richer clients; stage 4).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify 1:1 vs group, scale, latency, offline behavior. Surface connection-statefulness,
fan-out, ordering, and at-least-once.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/chat-application/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Async I/O: Level 0; queues/fanout: Level 2; ordering/dedup: Level 4. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises
1. Add group chat with 1k-member channels — fanout strategy? 2. Offline messages: store &
deliver on reconnect. 3. End-to-end encryption: key exchange design. 4. Reconnect storm on
a gateway restart — mitigation. 5. Re-estimate at 100M DAU.

---
Previous: [Notification platform](../beginner/notification-platform.md) · Next: [Social-media feed](social-media-feed.md)

