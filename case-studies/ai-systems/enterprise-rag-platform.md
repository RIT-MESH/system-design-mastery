# Case Study: Enterprise RAG Platform

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
An enterprise RAG platform serving thousands of tenants, each with private corpora, permission-aware retrieval, per-tenant token budgets, semantic caching, multi-model routing, and AI governance. This is a ai-systems-tier system design challenge because it must handle GPU-bound inference at scale while ensuring grounded, cited, and permission-aware answers. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): multi-tenant ingestion, permission-aware hybrid retrieval, reranking, grounded generation with citations, semantic caching, multi-model routing, per-tenant quotas, audit. Out: autonomous action (excluded).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Ingest per-tenant corpora with ACLs.
- Retrieve with permission filtering.
- Generate grounded answers with citations.
- Cache semantically equivalent queries (safe ones only).
- Route by task complexity to the cheapest capable model.
- Enforce per-tenant token budgets.
- Full audit.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Answer p99 < 3 s.
- No cross-tenant retrieval leakage.
- Availability 99.9 percent.
- Cost capped per tenant.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1k tenants, 10M chunks total, 100 queries/s peak. [assumption] 2. 20 percent cache hit rate. [assumption] 3. Permission filtering before generation. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
100 queries/s peak; bursts during business hours; cache hits skip LLM.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Enterprise RAG Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
10M chunks x embeddings x metadata = ~30 TB vectors + index; per-tenant namespace isolation.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Queries small; retrieval results small; generation streamed.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Enterprise RAG Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /ask (tenant, question) -> streamed answer + citations; POST /ingest (tenant, docs).

## 10. Data model
chunks(tenant, id, text, embedding, acl, metadata); cache(query_hash, tenant, answer, ttl); usage(tenant, tokens, cost, budget).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> GW[AI gateway: auth + budget]
  GW --> Cache[Semantic cache]
  Cache -.hit.-> Resp[Answer]
  Cache -.miss.-> Ret[Permission-aware hybrid retrieve]
  Ret --> Rerank[Reranker]
  Rerank --> LLM[Generate + cite]
  LLM --> Store[Cache answer]
  LLM --> Resp
  Ingest[Ingest] --> Chunk[Chunk + embed + ACL] --> VDB[Vector DB]
```

## 12. Request flow
Client asks -> gateway auth + budget check -> semantic cache lookup (safe + same tenant) -> hit returns; miss -> permission-aware hybrid retrieve + rerank -> generate with citations -> cache safe answer -> return; audit all.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as AI gateway auth budget
  participant C1 as Semantic cache
  participant C2 as Answer
  participant C3 as Permission-aware hybrid
  participant C4 as Reranker
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
AI gateway, semantic cache, permission-aware retrieval, reranker, LLM serving, ingestion pipeline, usage/budget tracker, audit.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Vector DB (per-tenant namespaces); semantic cache (embedding index + KV); usage store (relational); audit (append-only). Rejected: shared cache across tenants (leakage).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Semantic cache namespaced by tenant + model + prompt version; unsafe for time-sensitive or user-specific queries; TTL for freshness.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Vector index sharded by tenant; cache by tenant; gateway stateless; usage by tenant.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Vector DB RF=3; cache replicated; gateway stateless + provider failover.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Retrieval eventually consistent with ingest; cache versioned to model/corpus; budget strongly tracked.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Cache miss -> full LLM call (slower, no failure). Provider down -> failover. Budget exceeded -> 429. Vector DB shard down -> partial results.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Cache miss"]
  R2["full LLM call slower, no failure"]
  C1 --> R2
  C3["Provider down"]
  R4["failover"]
  C3 --> R4
  C5["Budget exceeded"]
  R6["429"]
  C5 --> R6
  C7["Vector DB shard down"]
  R8["partial results"]
  C7 --> R8
```

## 20. Reliability strategy
SLI answer latency, groundedness, zero-cross-tenant-leak; SLO 99.9 percent. Failover + budget enforcement. Chaos: kill a provider, assert failover.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Permission-aware retrieval (filter before generation); per-tenant isolation; PII redaction; no confidential data to unapproved external models; full audit; AI safety gateway.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Answer p99, cache hit ratio, cost per tenant, cross-tenant leakage attempts (0), groundedness score, provider failover rate.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
LLM calls dominate; cache + routing cut cost. Per-tenant budgets cap spend; small models for simple queries.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: basic RAG + per-tenant isolation. -> Stage 2: semantic cache + multi-model routing. -> Stage 3: governance + evaluation + billion-chunk. -> Stage 4: multi-region + multi-LoRA.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: basic RAG per-tenant isolation."]
  S2["Stage 2: semantic cache multi-model routing."]
  S3["Stage 3: governance evaluation billion-chunk."]
  S4["Stage 4: multi-region multi-LoRA."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Cache (cost) vs freshness/safety. Routing (cost) vs quality. Permission pre-filter (safe) vs post-filter (fast). Multi-tenant shared (efficient) vs isolated (safe).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Single model (cost). Shared cache (leakage). No permission filter (unauthorized access). Post-filter (leaks to model).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify tenant count, permission model, cache safety, budget enforcement. Surface permission-aware retrieval, semantic caching, multi-model routing, and governance.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/enterprise-rag-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
RAG: docs/ai-systems/06-basic-rag and 07-advanced-rag; semantic caching: 14-semantic-caching; LLM gateway: 13-llm-gateway; security: 09-ai-security. Sources: `S-VECTORDB` `S-RAG`.

## 30. Practical exercises

1. Design permission-aware retrieval with ACLs. 2. Safe vs unsafe cache categories. 3. Multi-model routing policy. 4. Per-tenant budget enforcement. 5. Cross-tenant leak test.

---
Previous: (AI case studies start) · Next: Autonomous support-agent team

