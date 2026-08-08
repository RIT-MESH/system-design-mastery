# Case Study: Message Broker

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
A durable, partitioned, multi-consumer message broker (Kafka-like): producers publish to topics partitioned by key; consumer groups read independently and replay from retained logs. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): produce/consume topics, partitioned logs, consumer groups, retention, at-least-once + idempotent. Out: exactly-once transactions, schema registry (noted as stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Publish events to a partitioned topic.
- Multiple consumer groups read independently.
- Retain events by time/size for replay.
- Per-partition ordering.
- At-least-once; idempotent consumers.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Ingest millions of events/s.
- Consumer lag bounded.
- Durability 11 nines (replicated log).
- Availability 99.9%.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M events/s, avg 1 KB. [assumption] 2. Retain 7 days. [constraint] 3. RF=3 per partition. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
1M events/s ingest; many consumer groups replay concurrently. Write-heavy, append-only.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Message Broker, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
1M/s x 1 KB x 86400 x 7 = ~600 TB retained (RF=3 -> ~1.8 PB raw). Partitioned; tier old to object storage.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
1M/s x 1 KB = ~1 GB/s ingress; consumers read the same data N times (fan-out read amplification).

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Message Broker, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| produce(topic,key,payload) | ack offsets | | consume(topic,group,offset) | batch of events |

## 10. Data model
Topics partitioned by key into append-only logs; each partition is an ordered, replicated sequence of (offset, ts, key, value). Offsets are consumer cursors.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  P[Producers] --> Part[Partitioned logs - RF=3]
  Part --> CG1[Consumer group A]
  Part --> CG2[Consumer group B]
  Part -.retention/tier.-> Cold[Object storage]
```

## 12. Request flow
Produce: route by key to a partition leader, append, replicate to followers, ack on RF. Consume: a group splits partitions; each consumer reads its partitions by offset, commits offsets.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Producers
  participant C1 as Partitioned logs RF 3
  participant C2 as Consumer group A
  participant C3 as Consumer group B
  participant C4 as Object storage
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
Brokers (partition leaders/followers), partition log store, consumer-group coordinator (offsets), tiering job, controller (metadata).

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Append-only logs on local disk (fast sequential writes) + replicated; metadata in a consensus store (Raft). Rejected: a DB as the log (loses the throughput/retention model).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Consumers cache offsets; hot partitions cached in OS page cache. No app-level cache on the write path.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Partition by key for ordering locality; partition count sized for parallelism + throughput; rebalance consumers across partitions.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Each partition: leader + 2 followers (RF=3), async by default; leader handles reads/writes, followers fetch. ISR (in-sync replicas) controls ack quorum.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Per-partition total order. Within a partition, ordering is strict; across partitions, no global order. At-least-once delivery; effectively-once with idempotent consumers + transactional output.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Leader down -> elect an ISR follower; minor data loss only if an un-replicated leader is lost (ack=all prevents). Consumer down -> rebalance partitions; offsets resume. Partition skew -> add partitions/consumers.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Leader down"]
  R2["elect an ISR follower"]
  C1 --> R2
  C3["Consumer down"]
  R4["rebalance partitions"]
  C3 --> R4
  C5["Partition skew"]
  R6["add partitions consumers"]
  C5 --> R6
```

## 20. Reliability strategy
SLI ingest latency, consumer lag, durability; SLO 99.9%. ack=all + RF=3 for no data loss on one failure. Chaos: kill a broker, assert election + no loss.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
TLS + SASL auth; per-topic ACLs; per-tenant quotas; don't log payloads with PII.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Bytes/s per topic, consumer lag per group, ISR shrink, leader elections, partition skew, disk fill.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Storage (retention x RF) + network (fan-out reads) dominate. Tier old partitions to object storage; right-size RF.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: brokers + replicated logs. -> Stage 2: partitioning + consumer groups. -> Stage 3: tiered retention + schema registry. -> Stage 4: exactly-once transactions, multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: brokers replicated logs."]
  S2["Stage 2: partitioning consumer groups."]
  S3["Stage 3: tiered retention schema registry."]
  S4["Stage 4: exactly-once transactions, multi-region."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Throughput/retention vs cost. Per-partition ordering vs global order. ack=all (no loss) vs latency. Tier (cost) vs replay latency.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
A queue with delete-on-read (loses replay/multi-consumer). A DB-backed log (lower throughput). Single broker (SPOF).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify ordering scope (partition vs global), retention, delivery semantics, replay. Surface the partitioned-log + consumer-group + retention model.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/message-broker/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading

Kafka: S-KAFKA; replication: Level 3; delivery semantics: Level 4.

## 30. Practical exercises

1. Add exactly-once transactions across consume-process-produce. 2. Design partition rebalance without stalling. 3. Retain 1 year — storage and tiering. 4. Hot partition (one key) — mitigation. 5. Multi-region replication for disaster recovery.

---
Previous: (advanced start) · Next: Metrics platform

