# Case Study: Payment Gateway

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Accept a payment from a customer to a merchant, authorize against card networks/banks, and settle — a PCI-scoped, idempotent, strongly-durable money path. This is a advanced-tier system design challenge because it must handle strict consistency and zero data loss while ensuring every transaction is durable, atomic, and auditable. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): authorize + capture + refund, idempotent, PCI tokenization. Out: 3DS, recurring billing (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Authorize a payment (hold).
- Capture (settle the hold).
- Refund.
- Idempotent by request key.
- Tokenize card data (PCI).

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- No double-charge.
- Durability 11 nines of payment records.
- Availability 99.95% (money path).
- PCI-DSS compliant.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M payments/day, ~12/s avg, 300/s peak. [assumption] 2. Auth p99 < 3 s (network-dependent). [constraint] 3. Idempotency key per intent. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
1M payments/day; auth is the latency-critical path (network round trips to banks).

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Payment Gateway, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Payments + idempotency keys + tokens; small but must be durable and auditable.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Small payloads; latency dominated by bank/network round trips, not bandwidth.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Payment Gateway, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST /payments/authorize | amount, token, key | auth id |
| POST |/payments/:id/capture | | |
| POST /payments/:id/refund | | |

## 10. Data model
payments(id, key, amount, status, token, ts); idempotency_keys(key -> payment_id, status); tokens (PCI vault). Ledger entries per payment.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Merch --> API[Payment API]
  API --> Idem[Idempotency check]
  API --> Token[Tokenize / vault]
  API --> Netw[Card network/bank]
  API --> Ledger[Payment ledger]
  API --> Settle[Settlement]
```

## 12. Request flow
Authorize: check idempotency key -> tokenize card -> authorize via network -> record in ledger -> return auth. Capture/refund update ledger. Retries with same key return original result.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Payment API
  participant C1 as Idempotency check
  participant C2 as Tokenize vault
  participant C3 as Card network bank
  participant C4 as Payment ledger
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
API, idempotency store, token vault (PCI), network connector, ledger, settlement.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Ledger: append-only, strongly durable (synchronous replication). Idempotency: KV keyed by request key. Rejected: mutable balances, non-idempotent writes.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Idempotency key cache (fast seen-check). No caching of money state.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Ledger partitioned by payment id; idempotency by key hash. Hot merchants partitioned further.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Ledger synchronous RF=3 (no loss on one failure). Idempotency store replicated.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Strong: a payment is authorized exactly once per idempotency key. Ledger is the source of truth; capture/refund are ledger entries.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Bank timeout -> safe-fail (mark unknown, reconcile via webhook/queue) never assume success. Ledger shard down -> payment fails (better than lost/duplicate). Idempotency store down -> fail-safe.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Bank timeout"]
  R2["safe-fail mark unknown, reconcile via we"]
  C1 --> R2
  C3["Ledger shard down"]
  R4["payment fails better than lost duplicate"]
  C3 --> R4
  C5["Idempotency store down"]
  R6["fail-safe"]
  C5 --> R6
```

## 20. Reliability strategy
SLI auth success, double-charge rate (0), unknown-resolution rate; SLO 99.95%. Safe-fail + reconcile. Chaos: kill a ledger shard, assert no double-charge.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
PCI-DSS: never store PAN (tokenize); HSM key mgmt; mTLS to networks; audit every payment; fraud hooks.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Auth success/decline rates, p99 latency, unknown-resolution queue, settlement reconciliation, double-charge guards.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Bank/network fees + PCI compliance + durable storage. Idempotency prevents direct loss/duplicate cost.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: authorize/capture + idempotency. -> Stage 2: tokenization + ledger sharding. -> Stage 3: 3DS, recurring, fraud. -> Stage 4: multi-region active-active for the auth path.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: authorize capture idempotency."]
  S2["Stage 2: tokenization ledger sharding."]
  S3["Stage 3: 3DS, recurring, fraud."]
  S4["Stage 4: multi-region active-active for the auth"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Safe-fail (no double-charge) vs false declines. Synchronous durability (no loss) vs latency. Tokenization (PCI) vs vault complexity.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Assume success on timeout (double-charge risk). Mutable balances (no audit). Non-idempotent API (duplicates).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify double-charge tolerance, bank timeouts, PCI. Surface idempotency, safe-fail + reconcile, and the durable ledger.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/payment-gateway/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Ledger/payment: Level 10; idempotency: Level 4; PCI/HSM: Level 7. Sources: `S-DYNAMO` `S-RAFT` `S-SPANNER`.

## 30. Practical exercises

1. Design the unknown-resolution reconciliation. 2. Refund after a partial capture. 3. 3DS challenge flow. 4. Webhook idempotency from banks. 5. Multi-region active-active auth.

---
Previous: Inventory-management · Next: Digital wallet

