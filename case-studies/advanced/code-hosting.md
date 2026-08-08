# Case Study: Code-Hosting Platform

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Host git repositories at scale: clone/push/pull, branch/merge, PRs, and notifications — a metadata-heavy, read-heavy, large-blob system. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): repos, push/pull/clone, PRs, reviews, webhooks. Out: CI (separate case), packages (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Host git repos (push/pull/clone).
- Branches, merges, PRs.
- Reviews + comments.
- Webhooks/notifications.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Clone latency reasonable for large repos.
- Availability 99.9%.
- Read-heavy (clones/fetches >> pushes).

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 10M repos, avg 1 GB, many small. [assumption] 2. Clones 100x pushes. [assumption] 3. Large repos need special handling. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Clones/fetches dominate; pushes fewer but write-critical.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Code-Hosting Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Repo objects (git objects) — PB at scale; metadata (PRs, issues, users) relational.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Clone egress is the dominant cost — large objects over the network.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Code-Hosting Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

git smart-http/ssh for transport; REST for PRs/issues/webhooks.

## 10. Data model
repos(id, objects, refs); metadata: users, PRs, issues, comments, webhooks. Git objects are content-addressed.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Dev --> Trans[Git transport - ssh/http]
  Trans --> Repo[Repo storage - objects, refs]
  Dev --> API[API: PRs/issues]
  API --> Meta[Metadata DB]
  Repo --> CDN/Cache
  Events[PR events] --> Webhook[Webhooks]
```

## 12. Request flow
Push/fetch via git transport -> objects stored content-addressed -> refs updated. PR/review via API -> metadata DB -> events emit webhooks. Clones served from cached objects.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Git transport ssh http
  participant C1 as Repo storage objects, re
  participant C2 as API PRs issues
  participant C3 as Metadata DB
  participant C4 as PR events
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
Git transport, repo storage (objects + refs), metadata DB, API, webhook bus.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Repo objects: content-addressed object store (often on object storage + a cache). Metadata: relational. Rejected: a DB for git objects (wrong model).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Object cache for hot repos/clones; metadata cache. CDN for large clones.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Repos partitioned by id; objects content-addressed (dedup). Hot repos replicated for clone bandwidth.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Objects immutable + content-addressed -> replicate widely for clone bandwidth. Metadata RF.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Git's own model: refs are the mutable pointers; objects immutable. Strong per-repo via git semantics.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Object store down -> clone fails for those repos (cache may serve). Metadata DB down -> PRs unavailable but clones work. Webhook backlog -> events lag.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Object store down"]
  R2["clone fails for those repos cache may se"]
  C1 --> R2
  C3["Metadata DB down"]
  R4["PRs unavailable but clones work"]
  C3 --> R4
  C5["Webhook backlog"]
  R6["events lag"]
  C5 --> R6
```

## 20. Reliability strategy
SLI clone latency, push success; SLO 99.9%. Object cache absorbs origin failures. Chaos: kill an object store node, assert clones from cache.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Auth (ssh keys/tokens); branch protection; secret scanning; webhook signing; repo ACLs.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Clone latency/throughput, push success, object cache hit, metadata DB latency, webhook delivery.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Object storage + clone egress dominate. Object cache + CDN cut egress; dedup cuts storage.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: git transport + objects + metadata. -> Stage 2: object cache/CDN + sharding. -> Stage 3: large-repo handling (partial clone). -> Stage 4: multi-region clone mirrors.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: git transport objects metadata."]
  S2["Stage 2: object cache CDN sharding."]
  S3["Stage 3: large-repo handling partial clone ."]
  S4["Stage 4: multi-region clone mirrors."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Object storage (cost/scale) vs a single file server. Cache hot repos (egress) vs cache size. Partial clone (latency) vs completeness.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
File-server for repos (won't scale, no dedup). Metadata and objects in one store (wrong model). No clone cache (egress cost).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify scale, large repos, clone volume. Surface content-addressed objects, metadata separation, egress cost.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/code-hosting/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Object storage: Level 2; content-addressing: Level 4; webhooks: Level 2. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Partial clone / sparse checkout. 2. Hot-repo clone bandwidth. 3. Large monorepo (GBs). 4. Webhook delivery guarantees. 5. Multi-region clone mirrors.

---
Previous: Collaborative document editor · Next: Continuous integration platform

