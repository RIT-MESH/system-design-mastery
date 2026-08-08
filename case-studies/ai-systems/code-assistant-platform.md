# Case Study: Code-Assistant Platform

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
A platform providing code completion, explanation, refactoring, and security review using LLMs with codebase indexing and security controls. This is a ai-systems-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In: codebase indexing, code completion, explanation, refactoring suggestions, security review. Out: autonomous code execution.

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Index codebase (functions, classes, imports).
- Suggest completions in context.
- Explain code.
- Suggest refactors.
- Flag security issues.
- Never execute code.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Completion latency < 500 ms.
- Context uses relevant code.
- Availability 99.9 percent.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1000 repos, avg 100k LOC. 2. 10k completions/s. 3. Confidential repos use local model.

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
10k completions/s; bursty during dev hours.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Code-Assistant Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
1000 repos x 100k LOC x ~50 bytes = ~5 GB code + index + embeddings.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Code context small (KBs); completions streamed.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Code-Assistant Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /complete (repo, file, cursor) -> completion; POST /review (PR diff) -> review.

## 10. Data model
repos(id, url, lang); functions(id, repo, signature, body, embedding); reviews(id, pr, findings).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  IDE --> GW[Code gateway]
  GW --> Index[Codebase index]
  Index --> Context[Relevant code]
  Context --> LLM[Code model]
  LLM --> Complete[Completion]
  PR --> Review[Security review]
  Review --> Findings
```

## 12. Request flow
IDE requests completion -> gateway auth -> retrieve relevant code from index -> send to code model -> stream completion; PR review: diff -> security model -> findings.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Code gateway
  participant C1 as Codebase index
  participant C2 as Relevant code
  participant C3 as Code model
  participant C4 as Completion
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
Code gateway, codebase indexer, context retriever, code LLM, security reviewer, IDE plugin.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Codebase index (vector + AST); function store; review findings; audit.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Common completions cached; repo index cached; signatures cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Index by repo; completions by repo; reviews by PR.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Index RF=3; gateway stateless; reviews durable.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Index eventual with commits; completions deterministic on snapshot; reviews advisory.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Index stale -> old code completions. LLM down -> keyword fallback. Confidential repo -> local model.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Index stale"]
  R2["old code completions"]
  C1 --> R2
  C3["LLM down"]
  R4["keyword fallback"]
  C3 --> R4
  C5["Confidential repo"]
  R6["local model"]
  C5 --> R6
```

Each failure has a documented response: which component detects it, how failover happens, what the user experiences, and how recovery is verified. The design principle is that a single failure should degrade, not cascade. Bulkheads and circuit breakers prevent one slow dependency from exhausting shared resources. Cascading failure is the most dangerous mode and is prevented by timeouts on every outbound call.

## 20. Reliability strategy
SLI completion latency, accuracy; SLO 99.9 percent. Fallback to keyword.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Confidential repos use local model only; code never to unapproved external APIs; PII redacted; audit; no auto-execution.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Completion latency, accuracy, index freshness, local-vs-external routing, security findings rate.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
LLM inference dominates; cache completions; route confidential to local (cheaper + safer).

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: index + completion. -> Stage 2: explanation + refactor + security. -> Stage 3: multi-language + local. -> Stage 4: enterprise fleet.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: index completion."]
  S2["Stage 2: explanation refactor security."]
  S3["Stage 3: multi-language local."]
  S4["Stage 4: enterprise fleet."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Local (privacy, cost) vs external (quality). Full-context (accuracy) vs latency. Auto-complete (fast) vs review (thorough).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Blind LLM (hallucinated APIs). External-only (security risk). Keyword-only (no understanding).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify repo count, confidentiality, languages, latency. Surface codebase indexing, context retrieval, local routing, security review.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/code-assistant-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Code LLM refs; docs/ai-systems/08-agentic-systems; security: 09-ai-security; local: 12-ai-extreme-scale. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Index a repo for context-aware completion. 2. Route confidential to local. 3. Security review pipeline. 4. Multi-language. 5. Eval completion accuracy.

---
Previous: GraphRAG research · Next: AI search engine

