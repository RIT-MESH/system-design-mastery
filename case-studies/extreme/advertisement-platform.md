# Case Study: Advertisement Platform

> **Tier:** extreme · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Match advertisers' campaigns to eligible users and serve an ad in milliseconds, with budget pacing and attribution — a latency-critical auction + serving system. This is a extreme-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): campaign targeting, real-time auction/serving, budget pacing, click attribution. Out: ML creative, multi-touch attribution (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Match a request to eligible campaigns.
- Run an auction; serve the winning ad.
- Pace budgets.
- Attribute clicks/conversions.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Serve p99 < 100 ms (in the page-load path).
- Budget never overspent.
- Availability 99.9%.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M ad requests/s. [assumption] 2. Targeting by user attributes + context. [assumption] 3. Budgets paced daily. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
1M ad requests/s; each must be matched + auctioned + served in the page-load path.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Advertisement Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Campaigns (targeting, creative, budget); user attributes; events (impressions/clicks). Petabytes of event logs.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Ad creatives served (images/video) — egress significant; CDN for creatives.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Advertisement Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET /ad | user, context | ad creative |
| POST |/event | impression/click | ack

## 10. Data model
campaigns(id, targeting, creative, budget, pace); users(id, attributes); events(id, type, campaign, user, ts).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Page --> AdReq[Ad request] --> Match[Eligibility match]
  Match --> Auction[Auction] --> Serve[Serve ad]
  Serve --> Pace[Budget pacing]
  Serve --> Log[Event log]
  Log --> Attr[Attribution]
```

## 12. Request flow
Ad request -> match eligible campaigns by targeting -> auction (bid x relevance) -> serve winner -> deduct/pace budget -> log impression; clicks/conversions attribute later.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Ad request
  participant C1 as Eligibility match
  participant C2 as Auction
  participant C3 as Serve ad
  participant C4 as Budget pacing
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
Eligibility match, auction, serving, budget pacing, event log, attribution.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Campaign store + user-attribute store (fast lookup); event log (stream); creative CDN. Rejected: scanning all campaigns per request (too slow).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Eligibility index cached; hot campaigns cached; user attributes cached; creatives on CDN.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Campaigns/targeting indexed for fast eligibility; events partitioned by time; user attributes by id.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Campaigns + budget replicated (budget must not overspend); events retained for attribution; creatives on CDN.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Budget: strongly consistent spend (no overspend) via atomic deduction. Events eventually consistent; attribution batched.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Auction slow -> serve a default/house ad (latency, not error). Budget store down -> fail-safe (stop serving, never overspend). Event log lag -> attribution delayed.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Auction slow"]
  R2["serve a default house ad latency, not er"]
  C1 --> R2
  C3["Budget store down"]
  R4["fail-safe stop serving, never overspend"]
  C3 --> R4
  C5["Event log lag"]
  R6["attribution delayed"]
  C5 --> R6
```

## 20. Reliability strategy
SLI serve latency, overspend (0); SLO 99.9%. Default-ad fallback. Chaos: kill auction, assert default ad served (no broken page).

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
User-attribute privacy; anti-fraud (bot clicks); budget integrity; creative safety checks.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Serve p99, fill rate, auction latency, budget spend vs pace, click/conversion attribution, bot rate.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Serving infra (latency) + event storage (PB) + creative egress (CDN). Eligibility index cuts per-request cost.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: match + auction + serve. -> Stage 2: budget pacing + attribution. -> Stage 3: real-time bidding, ML creative. -> Stage 4: multi-touch attribution, multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: match auction serve."]
  S2["Stage 2: budget pacing attribution."]
  S3["Stage 3: real-time bidding, ML creative."]
  S4["Stage 4: multi-touch attribution, multi-region."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Latency (page-load) vs auction complexity. Budget strictness (no overspend) vs throughput. Attribution accuracy vs latency.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Scan all campaigns (too slow). Loose budget (overspend). Synchronous attribution (latency).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify latency, targeting, budget strictness. Surface eligibility index, auction, budget pacing, CDN creatives.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/advertisement-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Real-time/streams: Level 10; CDN: Level 2; consistency: Level 4. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Budget pacing without overspend. 2. Bot-click detection. 3. Serve at 1M req/s < 100 ms. 4. Multi-touch attribution. 5. ML creative selection.

---
Previous: Fraud-detection system · Next: Data lake

