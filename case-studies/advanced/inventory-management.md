# Case Study: Inventory-Management Platform

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Track stock across many warehouses in real time, with atomic reservations and reconciliation — a strongly-consistent, write-critical system. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): per-warehouse stock, reservations, transfers, reconciliation. Out: demand forecasting (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Track stock per warehouse/SKU.
- Atomically reserve/release on order.
- Transfer between warehouses.
- Reconcile to physical counts.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- No oversell.
- Reserve latency < 50 ms.
- Availability 99.9%.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M SKUs, 100 warehouses. [assumption] 2. Reserves 1k/s avg, 10k/s peak. [assumption] 3. Stock must not go negative. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Reserve/release ~1k/s; reads higher (availability checks). Write-critical correctness path.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Inventory-Management Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Stock per (warehouse, SKU) — small but high-write; reservation log; transfer history.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Small messages; bandwidth trivial; correctness is the concern.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Inventory-Management Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST /reserve | wh, sku, qty | reserved/rejected |
| POST |/release | reserve id | ack |
| POST /transfer | from,to,sku,qty | ack |

## 10. Data model
stock(warehouse, sku, available, reserved); reservations(id, wh, sku, qty, status); transfers(id, from, to, sku, qty).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Order --> Reserve[Reserve svc]
  Reserve --> Stock[Stock store, atomic]
  Reserve -->|rejected| Order
  Transfer[Transfer svc] --> Stock
  Stock --> Reconcile[Reconcile vs physical]
  Reconcile --> Stock
```

## 12. Request flow
Reserve: atomic decrement of available + increment reserved; reject if insufficient. Release reverses. Transfer moves stock between warehouses atomically. Reconcile adjusts to physical counts with audit.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Reserve svc
  participant C1 as Stock store, atomic
  participant C2 as Transfer svc
  participant C3 as Reconcile vs physical
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
Reserve svc, stock store (atomic), transfer svc, reconcile job.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Transactional RDBMS or a strongly-consistent KV with atomic compare-and-set per (wh,sku). Rejected: cache as authoritative (oversell).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Read cache for availability; reservations always on the authoritative store.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Partition by warehouse (co-locates a warehouse's SKUs; transfers cross-partition but are rare). Hot SKUs partitioned further.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Stock RF=3, synchronous replication on the reserve path for no-oversell after failover.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Strong per (warehouse, SKU): atomic reserve; no oversell even under failover. Cross-warehouse transfers are transactions.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Stock shard down -> reserves for those SKUs fail (no oversell); reads return last-known or unavailable. Reconcile corrects drift.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Stock shard down"]
  R2["reserves for those SKUs fail no oversell"]
  C1 --> R2
```

Each failure has a documented response: which component detects it, how failover happens, what the user experiences, and how recovery is verified. The design principle is that a single failure should degrade, not cascade. Bulkheads and circuit breakers prevent one slow dependency from exhausting shared resources. Cascading failure is the most dangerous mode and is prevented by timeouts on every outbound call.

## 20. Reliability strategy
SLI reserve latency, oversell rate (must be 0); SLO 99.9%. Idempotent reserves. Chaos: kill a stock shard, assert rejects not oversell.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Per-warehouse auth; audit all stock changes; tamper-evident reconciliation.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Reserve latency, reject rate, stock drift, reconcile adjustments, transfer backlog.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Transactional DB; correctness-first. Hot-SKU contention (not cost) is the operational challenge.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: stock + reserve. -> Stage 2: per-warehouse sharding + transfers. -> Stage 3: reconcile automation + demand forecasting. -> Stage 4: multi-region with regional stock.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: stock reserve."]
  S2["Stage 2: per-warehouse sharding transfers."]
  S3["Stage 3: reconcile automation demand forecasting."]
  S4["Stage 4: multi-region with regional stock."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Strong consistency (no oversell) vs throughput. Per-warehouse partitioning (locality) vs cross-wh transfers. Cache reads (fast) vs authoritative reserve (correct).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Eventual stock (oversell). Cache as source (oversell). Denormalized stock per region (reconciliation pain).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify oversell tolerance, warehouse model, transfers. Surface atomic reservation and reconciliation.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/inventory-management/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Transactions: Level 4; sharding: Level 3; consistency: Level 4. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Hot SKU contention mitigation. 2. Transfer atomicity across warehouses. 3. Reconcile after a shard failure. 4. Multi-region regional stock. 5. Demand forecasting inputs.

---
Previous: E-commerce · Next: Payment gateway

