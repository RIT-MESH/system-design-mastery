# Case Study: LLM API Gateway

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
An enterprise LLM API gateway that provides a unified model API across providers (external and self-hosted), with complexity/cost/latency routing, per-tenant token budgets, failover, semantic caching, content filtering, PII redaction, and full audit. This is a ai-systems-tier system design challenge because it must handle GPU-bound inference at scale while ensuring grounded, cited, and permission-aware answers. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): unified API, provider abstraction, multi-model routing (complexity, cost, latency, capability), token-based rate limiting and budgets, provider failover, semantic caching, content filtering, PII redaction, logging, audit. Out: model hosting (uses providers).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements

- Accept a unified API call.
- Authenticate and check token budget.
- Route to the best model for the task.
- Fail over on provider failure.
- Cache semantically equivalent safe queries.
- Filter content and redact PII.
- Log and audit all calls.
- Enforce per-tenant token budgets.

## 4. Non-functional requirements
- Gateway overhead p99 < 20 ms.
- Availability 99.95 percent.
- No PII in logs.
- No cost overrun (budgets enforced).

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 100 tenants, 10k requests/s peak. [assumption] 2. Token distribution: 80 percent short, 20 percent long-context. [assumption] 3. 3 providers + 1 self-hosted. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
10k req/s peak; each request carries input tokens (budget by tokens, not RPS).

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For LLM API Gateway, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Usage logs + audit + cache; moderate, must be auditable.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Pass-through (input + output tokens); gateway adds minimal.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For LLM API Gateway, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /v1/completions (unified) -> streamed response; GET /v1/usage/:tenant.

## 10. Data model
usage(tenant, req_id, model, input_tokens, output_tokens, cost, ts); cache(query_hash, tenant, answer, ttl); providers(name, endpoint, key_ref, models, cost_per_1M).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Client --> Auth[Auth + token budget]
  Auth --> Cache[Semantic cache]
  Cache -.hit.-> Resp[Response]
  Cache -.miss.-> Route[Router: complexity or cost or latency or capability]
  Route --> P1[Provider 1]
  Route --> P2[Provider 2]
  Route --> Self[Self-hosted]
  P1 -.fail.-> Fail[Fallback]
  P1 & P2 & Self & Fail --> Filter[Content filter + PII redaction]
  Filter --> Log[Log + audit + cost]
  Log --> Resp
```

## 12. Request flow
Client calls unified API -> auth + token budget check -> semantic cache (safe + same tenant) -> hit returns; miss -> router picks best model (complexity/cost/latency/capability) -> provider call -> on fail, failover -> content filter + PII redaction -> log + audit + cost -> return.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Auth token budget
  participant C1 as Semantic cache
  participant C2 as Response
  participant C3 as Router complexity or cos
  participant C4 as Provider 1
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
Auth, token budget store, semantic cache, router, provider connectors, failover, content filter, PII redaction, logger/auditor, cost tracker.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Usage/audit (relational, append-only); semantic cache (embedding index + KV); provider registry (secret manager). Rejected: RPS-based rate limiting (insufficient for LLMs).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Semantic cache namespaced by tenant + model + prompt version; unsafe for time-sensitive or user-specific; TTL.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Usage by tenant; cache by tenant; gateway stateless; router stateless.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Gateway stateless RF=many; usage store RF=3; cache replicated; provider credentials in secret manager.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Usage/cost strongly tracked; cache versioned; budget strongly enforced.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Provider down -> failover. Budget store down -> fail-open with cap + reconcile (or fail-closed). Cache stale -> TTL. Router down -> default model.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Provider down"]
  R2["failover"]
  C1 --> R2
  C3["Budget store down"]
  R4["fail-open with cap reconcile or fail-clo"]
  C3 --> R4
  C5["Cache stale"]
  R6["TTL"]
  C5 --> R6
  C7["Router down"]
  R8["default model"]
  C7 --> R8
```

## 20. Reliability strategy
SLI overhead latency, availability; SLO 99.95 percent. Failover + budget enforcement. Chaos: kill a provider, assert failover.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
API key management + rotation; PII redaction before logging; content filtering; no confidential data to unapproved external models; per-tenant isolation; full audit; mTLS to providers.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Requests/s, tokens/s, routing distribution, cache hit ratio, cost per tenant, failover rate, content-filter blocks, PII redaction count, p99 overhead.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Gateway compute (stateless, cheap) + cache (saves LLM cost). Routing to cheaper models cuts cost; budgets cap spend.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: unified API + routing + budgets. -> Stage 2: semantic cache + failover + PII redaction. -> Stage 3: multi-region + governance + evaluation. -> Stage 4: enterprise AI gateway at scale.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: unified API routing budgets."]
  S2["Stage 2: semantic cache failover PII redaction."]
  S3["Stage 3: multi-region governance evaluation."]
  S4["Stage 4: enterprise AI gateway at scale."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Centralized (policy consistency) vs SPOF. Routing (cost) vs latency overhead. Token budgets (fairness) vs flexibility. Cache (cost) vs freshness/safety.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Direct provider calls (no control, no budget, no audit). RPS limits (wrong unit). Single provider (SPOF). No cache (full cost).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify provider count, token distribution, budget enforcement, cache safety. Surface routing, token-based budgets, failover, PII redaction, audit.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/llm-api-gateway/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
LLM gateways: docs/ai-systems/13-llm-gateway; semantic caching: 14-semantic-caching; AI security: 09-ai-security; API gateway: Level 2. Sources: `S-VECTORDB` `S-RAG`.

## 30. Practical exercises

1. Routing policy for 4 models. 2. Token budget enforcement with concurrency. 3. Safe vs unsafe cache categories. 4. Failover with 3 providers. 5. PII redaction pipeline.

---
Previous: Autonomous support-agent team · Next: (end of AI case studies)

