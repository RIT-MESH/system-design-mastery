# Case Study: Food-Delivery Platform

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Customers order from restaurants; a courier delivers. Three-sided marketplace with real-time courier dispatch and order tracking. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): browse/order, restaurant accept, courier dispatch, live tracking, payment. Out: scheduled/group orders.

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Customer orders from a restaurant.
- Restaurant accepts/prepares.
- Dispatch a courier; track delivery.
- Pay all parties.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Dispatch latency < 30 s.
- Tracking freshness < 5 s.
- Availability 99.9%.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 500k orders/day, ~30 min each. [assumption] 2. Couriers 50k. [assumption] 3. Peak 10x at meal times. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
500k orders/day; dispatch bursts at meal times; live tracking for every active order+courier.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Food-Delivery Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Restaurants/menu, orders, courier location; orders ~500k/day x KB; courier geo index live.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Live location updates from active couriers + order status pushes; small messages at scale.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Food-Delivery Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST /orders | items, restaurant | order id |
| WS |/orders/:id | | live status |
| POST /couriers/location | loc | ack |

## 10. Data model
restaurant(id, menu, loc); order(id, customer, restaurant, items, status, courier); courier(id, loc, status). Geo index of available couriers.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Cust --> Order[Order svc] --> Rest[Restaurant accept]
  Rest --> Dispatch[Dispatch svc] --> Geo[Courier geo index]
  Dispatch --> Courier[Courier]
  Courier & Cust --> Track[Live tracking WS]
  Order --> Pay[Payment split]
```

## 12. Request flow
Order -> restaurant accepts -> dispatch finds a nearby available courier -> courier accepts -> live tracking -> on delivery, payment split to restaurant+courier.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Order svc
  participant C1 as Restaurant accept
  participant C2 as Dispatch svc
  participant C3 as Courier geo index
  participant C4 as Courier
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
Order svc, restaurant svc, dispatch + geo index, courier location, tracking gateway, payment.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Order store (relational, transactional); geo index (in-memory); menu/restaurant KV. Payment needs ACID.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Menu/restaurant cached; courier geo index in memory; order hot state cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Geo index by region; orders by id; couriers sharded to location gateways.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Order store RF=3; geo index replicated per region; courier location ephemeral.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Order status strongly tracked per order. Geo/dispatch eventually consistent across regions.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
No courier nearby -> expand radius + queue + notify customer of delay. Tracking gateway down -> reconnect. Payment fail -> retry; order still tracked.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["No courier nearby"]
  R2["expand radius queue notify customer of d"]
  C1 --> R2
  C3["Tracking gateway down"]
  R4["reconnect"]
  C3 --> R4
  C5["Payment fail"]
  R6["retry"]
  C5 --> R6
```

## 20. Reliability strategy
SLI dispatch latency, tracking freshness; SLO 99.9%. Expand-radius fallback; idempotent payment. Chaos: kill dispatch shard, assert degraded dispatch.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Customer/courier/restaurant auth; location privacy post-delivery; payment integrity; menu tamper protection.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Dispatch latency, no-courier rate, tracking freshness, order lifecycle, payment success.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Real-time infra + maps/routing + payment fees dominate. Couriers idle time is the marketplace economics, not infra.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: order + dispatch. -> Stage 2: geo-partitioned dispatch + tracking. -> Stage 3: batching, predicted ETAs. -> Stage 4: multi-region, marketplace balancing.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: order dispatch."]
  S2["Stage 2: geo-partitioned dispatch tracking."]
  S3["Stage 3: batching, predicted ETAs."]
  S4["Stage 4: multi-region, marketplace balancing."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Dispatch latency vs courier utilization. Live WS vs polling. Expand radius (match) vs wait (utilization).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Polling tracking (latency/battery). Manual dispatch (doesn't scale). Central matcher (SPOF).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify three-sided timing, dispatch radius, ETA. Surface geo dispatch, real-time tracking, payment split.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/food-delivery/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Geo: Level 3; real-time: Level 10; payment: Level 10 ledger. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Add batching of nearby orders. 2. Predicted courier ETAs. 3. No-courier surge pricing. 4. Reconnect storm mitigation. 5. Multi-tenant restaurant onboarding.

---
Previous: Ride-hailing · Next: E-commerce

