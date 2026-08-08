# Case Study: Feature Store / Model-Serving

> **Tier:** extreme · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Provide consistent features for training and serving and serve models at low latency — the data backbone of an ML platform (expanded from the Level 10 chapter). This is a extreme-tier system design challenge because it must handle GPU-bound inference at scale while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): offline + online feature store, model registry, low-latency serving, monitoring. Out: auto-retraining (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Serve consistent features for training and online inference.
- Version models; serve at low latency.
- Monitor drift; trigger retrain.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Online feature read p99 < 50 ms.
- Train/serve consistency (no skew).
- Availability 99.9%.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 100M entities, 1k features. [assumption] 2. Models retrained hourly. [assumption] 3. Serving 100k req/s. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Online feature reads dominate serving; offline reads for training (batch).

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Feature Store / Model-Serving, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Feature values (offline history + online hot); models (artifacts).

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Feature fetch per inference; small but latency-critical.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Feature Store / Model-Serving, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET /features/:entity |
| features |
| POST |/predict | features/model | prediction |

## 10. Data model
features(entity, feature, value, ts) — online (hot) + offline (history); models(version, artifact, metrics).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Sources[Data sources] --> FS[Feature store]
  FS --> Online[Online store - hot]
  FS --> Offline[Offline store - history]
  Online --> Serve[Serving - model]
  Offline --> Train[Training]
  Train --> Reg[Model registry] --> Serve
  Serve --> Mon[Drift monitoring] -.retrain.-> Train
```

## 12. Request flow
Sources compute features into the store (online hot + offline history). Training reads offline; serving reads online (same definitions -> no skew). Models versioned, served; drift monitoring triggers retraining.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Data sources
  participant C1 as Feature store
  participant C2 as Online store hot
  participant C3 as Offline store history
  participant C4 as Serving model
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
Feature store (online + offline), model registry, serving, drift monitoring, training.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Online: low-latency KV (hot features). Offline: columnar/lake for history. Model registry: artifact store. Rejected: separate training/serving feature code (skew).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Hot entity features in memory; model in serving memory; common predictions cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Feature store by entity id; serving scaled by QPS; offline by feature/time.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Online store replicated for availability; offline durable; models versioned + replicated.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Online near-real-time; offline immutable history; train/serve use the same feature definitions (consistency by construction).

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Online store down -> serving degrades (stale/cached features or refuse). Model serving down -> fallback model. Drift undetected -> monitor freshness.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Online store down"]
  R2["serving degrades stale cached features o"]
  C1 --> R2
  C3["Model serving down"]
  R4["fallback model"]
  C3 --> R4
  C5["Drift undetected"]
  R6["monitor freshness"]
  C5 --> R6
```

## 20. Reliability strategy
SLI feature latency, model availability; SPO 99.9%. Fallback model. Chaos: kill online store, assert cached-feature fallback.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Per-entity isolation; PII in features redacted; model IP protection; audit predictions.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Feature latency, train/serve consistency checks, drift metrics, model freshness, serving p99.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Online store (memory) + offline (lake) + serving. Right-size online to hot entities; compute features once.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: features + serving. -> Stage 2: online/offline store + model registry. -> Stage 3: drift monitoring + auto-retrain. -> Stage 4: streaming features, multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: features serving."]
  S2["Stage 2: online offline store model registry."]
  S3["Stage 3: drift monitoring auto-retrain."]
  S4["Stage 4: streaming features, multi-region."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Online (latency) vs offline (history) consistency — same definitions reconcile. Caching (cost) vs freshness. Retrain frequency (freshness) vs cost.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Recompute features per query (slow, skew). No versioning (silent drift). Single store for train+serve (wrong access patterns).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify feature scale, latency, skew. Surface the dual store, consistency-by-definition, versioning, drift.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/feature-store-model-serving/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
ML/feature stores: Level 10; model serving: LLM-inference case; streams: Level 10. Sources: `S-VECTORDB` `S-RAG`.

## 30. Practical exercises

1. Guarantee train/serve consistency. 2. Online at 100k req/s < 50 ms. 3. Drift-triggered retrain. 4. Feature backfill for a new model. 5. Streaming features with low lag.

---
Previous: Internet of Things platform · Next: LLM inference platform

