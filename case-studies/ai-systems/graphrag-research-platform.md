# Case Study: GraphRAG Research Platform

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  Docs --> Extract[Entity and relation extraction]
  Extract --> Graph[(Knowledge graph)]
  Query --> Plan[Multi-hop plan]
  Plan --> Graph
  Graph --> Context[Subgraph + text]
  Context --> LLM[Generate with citations]
```


## 28. Original Mermaid diagrams

Standalone sources under `diagrams/case-studies/graphrag-research-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. Request sequence and failure flow:

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant P0 as Client
  participant P1 as GraphRAG Research Platfo
  participant P2 as Store
  P0 ->> P1: query
  P1 ->> P2: look up or fetch
  P2 -->> P1: response
  P1 -->> P0: response
  alt success
    P0 -->> P0: done
  else failure
    P0 -->> P0: retry or fallback
  end
```

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Graph down"]
  R2["degrade to vector-only RAG"]
  C1 --> R2
  C3["NLP lag"]
  R4["graph stale"]
  C3 --> R4
  C5["Query timeout"]
  R6["partial"]
  C5 --> R6
```

## 1. Problem statement

A RAG platform that retrieves from a knowledge graph for multi-hop reasoning, enabling answers that require traversing relationships.

This system sits at the intersection of distributed systems and operational reliability. The design must balance latency versus durability while ensuring no single component failure cascades. The target audience includes engineers and operators, so the design must be observable, debuggable, and reversible.
## 2. Scope

In: graph ingestion, entity extraction, relationship indexing, multi-hop retrieval, grounded generation. Out: real-time graph updates.

The scope boundary is deliberate: including too much in v1 risks a system that is broad but shallow. Each excluded feature is a candidate for a later iteration once the core loop is proven.
## 3. Functional requirements

- Ingest documents and extract entities and relationships. - Build a knowledge graph. - Multi-hop retrieval. - Generate answers with graph context and citations.

These requirements drive the architecture: the read-heavy pattern pushes toward caching; the durability requirement forces synchronous writes; the idempotency requirement means every write path handles redelivery without double-application.
## 4. Non-functional requirements

- Multi-hop query p99 < 5 s. - Graph freshness < 1 hour. - Availability 99.9 percent.

The non-functional targets shape every component choice: the latency SLO forces edge caching and limits synchronous cross-region calls; the availability target drives redundancy (RF=3, multi-AZ); the cost target constrains the model size.
## 5. Explicit assumptions

1. 1M entities, 10M relationships, 100k docs. 2. Avg 2-3 hops. 3. NLP extraction pipeline.

These assumptions are the load-bearing facts of the design. If any is wrong by an order of magnitude, the architecture must adapt: 10x more traffic may require sharding earlier; a different read-write ratio changes the caching strategy entirely.
## 6. Traffic estimation

10 q/s; multi-hop queries are more complex.

The traffic estimate reveals the binding constraint. Peak is modeled at 10x average. The read-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy), which changes the storage and replication strategy.
## 7. Storage estimation

1M entities + 10M edges + 100k docs = ~50 GB graph + text + embeddings.

Storage growth is linear with time and must be planned with retention. The estimate includes metadata and index overhead (20-30 percent above raw). Without a retention policy, storage grows unboundedly.
## 8. Bandwidth estimation

Query results moderate (subgraphs); generation streamed.

Bandwidth is often not the binding constraint but becomes significant at the edge during viral spikes. CDN and edge caching cut origin egress; compression cuts bandwidth by 50-80 percent where applicable.
## 9. API design

POST /ask -> answer + graph path citations; POST /ingest (docs) -> extract + index.

The API follows REST for external clients and gRPC for internal calls. Every write endpoint accepts an idempotency key. Rate limiting is enforced at the gateway before the service tier.
## 10. Data model

entities(id, type, attrs); relationships(src, dst, type, weight); documents(id, text, entities[]).

The data model is designed around the access pattern, not the entity shape. The primary access path determines the partition key; secondary paths determine indexes. Denormalization is applied selectively where the hot read path would otherwise require expensive joins.
## 12. Request flow

Documents -> NLP extracts entities and relationships -> knowledge graph built -> query plans multi-hop -> retrieves subgraph + text -> LLM generates with graph-path citations.

The request flow reveals the critical path: any component on the hot path that fails or slows degrades the user experience. The design applies timeouts, circuit breakers, and bulkheads to each hop. The write path includes an idempotency check before any state mutation.
## 13. Component responsibilities

NLP extraction, graph store, query planner, multi-hop retriever, LLM, citation builder.

Each component has a single, well-defined responsibility. The gateway handles auth and routing; the service tier is stateless and horizontally scalable; the data tier is the stateful core, carefully partitioned and replicated. The separation allows each tier to scale independently.
## 14. Database selection

Graph store for entities and relationships; vector DB for entity embeddings; doc store for text.

The database choice is driven by the access pattern. The rejected alternatives were rejected for specific reasons: a relational DB was rejected if the workload is a single key lookup at massive scale; a KV store was rejected if joins and transactions are needed.
## 15. Caching strategy

Common query plans cached; graph subgraphs cached; entity lookups cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default; write-through is used where read-after-write consistency is required. Stampede protection is applied to any key that can go viral. Cache entries are namespaced by tenant.
## 16. Partitioning strategy

Graph sharded by entity community; queries fan out.

The partition key co-locates related data while distributing load evenly. Consistent hashing with virtual nodes minimizes data movement when nodes change. A hot key is mitigated by caching, extra replication, or key splitting.
## 17. Replication strategy

Graph store RF=3; doc store replicated; extraction stateless.

Replication is synchronous on the write-confirmation path where durability is critical and asynchronous elsewhere. RF=3 tolerates one failure. Failover is tested, not just configured. Cross-region replication is asynchronous with a documented RPO.
## 18. Consistency model

Graph eventual with ingestion; queries deterministic on snapshot.

The consistency model is the weakest that users can tolerate. Read-your-writes is provided where the user expects to see their own write. Eventual consistency is bounded (seconds) and monitored. The system documents what eventual means to users.
## 19. Failure scenarios

Graph down -> degrade to vector-only RAG. NLP lag -> graph stale. Query timeout -> partial.

Each failure scenario has a documented response: which component detects it, how failover happens, what the user experiences, and how recovery is verified. Bulkheads and circuit breakers prevent one slow dependency from cascading.
## 20. Reliability strategy

SLI multi-hop accuracy, query latency; SLO 99.9 percent. Fallback to vector RAG.

The SLO defines what good means measurably; the error budget is the allowed unavailability spent on deploys and feature risk. The system is tested with chaos engineering to verify resilience. An untested failover is not a failover.
## 21. Security considerations

Graph may contain PII -> RBAC; per-tenant isolation; PII redaction; audit.

Security is defense in depth: TLS, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed: on any error, the system refuses to act.
## 22. Observability strategy

Extraction lag, query latency, multi-hop accuracy, graph freshness.

Observability uses logs, metrics, and traces with correlation IDs. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not raw thresholds. The on-call runbook for each alert is tested.
## 23. Cost considerations

Graph store (memory) + NLP (compute) + LLM (tokens). Cache common queries.

Cost is dominated by the binding resource. Primary levers: caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing. Cost is tracked as a first-class metric and alerted on when unit cost spikes.
## 24. Scaling stages

Stage 1: extract + graph + multi-hop. -> Stage 2: query planning + caching. -> Stage 3: real-time updates. -> Stage 4: billion-entity graph.

The scaling stages are triggered by specific thresholds, not by calendar. Each stage is a deliberate architectural change: Stage 1 handles initial load; Stage 2 when a single node saturates; Stage 3 when latency exceeds the SLO; Stage 4 when hot keys threaten the origin.
## 25. Trade-offs

Graph (multi-hop) vs vector (semantic, fast). Real-time (fresh) vs batch (cost). Deep traversal vs latency.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct; it presents the chosen option, the rejected alternative, and the workload-specific reason.
## 26. Alternative designs

Vector-only (misses multi-hop). Manual graph (no scale). Full graph DB (wrong access pattern).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements that make them inferior here but not universally inferior.
## 27. Interview discussion points

Clarify entity count, hop depth, freshness, latency. Surface extraction, graph, multi-hop retrieval, citations.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply, discuss failure modes explicitly, and offer an alternative with a reason.
## 29. Further reading

GraphRAG papers; knowledge graph refs; docs/ai-systems/07-advanced-rag; graph: Level 10.

The further reading cites primary sources (RFCs, papers, official documentation) via stable IDs in SOURCES.md, not secondary blog posts. Each citation is chosen because it is the authoritative source for a specific technical claim.
## 30. Practical exercises

1. 3-hop query plan. 2. Entity resolution. 3. Graph staleness budget. 4. Fallback to vector. 5. Multi-hop accuracy eval.


---
Previous: Multi-tenant RAG service · Next: Code-assistant platform

The exercises push the reader beyond v1: re-estimating at 10x reveals capacity limits; adding a new requirement forces an architectural change; designing the failover test reveals whether resilience claims are real.
