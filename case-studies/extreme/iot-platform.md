# Case Study: Internet of Things Platform

> **Tier:** extreme · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Ingest telemetry from billions of intermittently-connected devices, maintain per-device digital twins, and support bidirectional commands at fleet scale. This is a extreme-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): device ingest (intermittent), digital-twin state, command delivery, fan-out analytics. Out: edge compute, OTA (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Ingest telemetry from devices (intermittent).
- Maintain a digital twin per device.
- Deliver commands with acknowledged delivery.
- Fan-out analytics.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Handle billions of devices, intermittent connectivity.
- Twin update near-real-time.
- Command delivery when device reconnects.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1B devices, ~1 telemetry/min when online. [assumption] 2. ~30 percent online at once. [assumption] 3. Commands queued for offline devices. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Reconnect storms; per-device small messages at massive fleet scale.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Internet of Things Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Per-device twin state + telemetry history; PB over time, tiered cold.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Telemetry ingress large in aggregate; commands small.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Internet of Things Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

device MQTT/HTTP for telemetry + commands; app API to query twins / send commands.

## 10. Data model
devices(id, twin state, last_seen); telemetry(device, ts, metrics); commands(device, queued commands).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Dev[Devices, intermittent] --> GW[IoT gateway/broker]
  GW --> Twin[Digital twins]
  Twin --> Apps[Apps/analytics]
  Apps -.commands.-> GW -.delivered when online.-> Dev
  GW --> Tier[Telemetry -> cold tier]
```

## 12. Request flow
Devices connect (when online), push telemetry -> gateway updates the twin + stores telemetry -> apps query twins / send commands -> commands queued and delivered on reconnect; telemetry tiered cold.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Devices, intermittent
  participant C1 as IoT gateway broker
  participant C2 as Digital twins
  participant C3 as Apps analytics
  participant C4 as Telemetry -> cold tier
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
Device gateway/broker, twin store, telemetry store, command queue, fan-out analytics.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Twin store: per-device KV (fast); telemetry: time-series/object tiered; command queue per device. Rejected: per-device connections in a single broker (can't scale).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Hot twins cached; recent telemetry cached; gateway coalesces messages.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Twin store sharded by device id; brokers sharded by device for connection affinity; telemetry by (device, time).

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Twins replicated (availability); telemetry durable (object/tiered); commands durable until acked.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Twin eventually consistent with telemetry (lag seconds). Commands delivered at-least-once; idempotent device actions.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Broker down -> devices reconnect to another (stagger to avoid storm). Twin shard down -> those twins unavailable (read last-known). Command queue down -> commands re-queued.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Broker down"]
  R2["devices reconnect to another stagger to"]
  C1 --> R2
  C3["Twin shard down"]
  R4["those twins unavailable read last-known"]
  C3 --> R4
  C5["Command queue down"]
  R6["commands re-queued"]
  C5 --> R6
```

## 20. Reliability strategy
SLI twin freshness, command delivery; SPO 99.9%. Staggered reconnect. Chaos: kill a broker, assert reconnect without a storm.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Device identity/cert (mTLS); per-device auth; telemetry PII; command authorization; OTA integrity.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Connected devices, telemetry rate, twin freshness, command delivery latency, reconnect rate, backlog.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Telemetry storage (PB) + brokers (connections). Tier cold; coalesce messages; size brokers to connections.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: gateway + twins + commands. -> Stage 2: sharded brokers + tiered telemetry. -> Stage 3: reconnect staggering, fan-out analytics. -> Stage 4: edge compute, OTA, multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: gateway twins commands."]
  S2["Stage 2: sharded brokers tiered telemetry."]
  S3["Stage 3: reconnect staggering, fan-out analytics."]
  S4["Stage 4: edge compute, OTA, multi-region."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Intermittent design (queue commands) vs low-latency assumption. Twin freshness vs cost. Sharded brokers (connection scale) vs failover complexity.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Assume always-on devices (wrong). Single broker (can't scale). Sync commands (fail on offline).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify device count, online percent, command latency, retention. Surface intermittent design, twins, reconnect storms.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/iot-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
IoT/edge: Level 10; time-series: Level 3; reconnect/thundering-herd: Level 6. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Stagger a reconnect storm. 2. Command delivery to offline devices. 3. Twin at 1B devices. 4. Telemetry tiering cost. 5. OTA rollout at fleet scale.

---
Previous: RAG platform · Next: Feature store / model-serving

