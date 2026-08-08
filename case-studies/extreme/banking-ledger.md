# Case Study: Banking Ledger

> **Tier:** extreme · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
The core ledger of a bank: immutable, double-entry, strongly-durable, auditable, reconcilable — money never lost or duplicated. This is a extreme-tier system design challenge because it must handle strict consistency and zero data loss while ensuring every transaction is durable, atomic, and auditable. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): accounts, transfers, double-entry, balances, reconciliation, immutable history. Out: lending, interest (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Move money double-entry (balanced debit/credit).
- Never lose/duplicate a committed entry.
- Derive balances from entries.
- Reconcile vs banks.
- Full audit trail.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Zero data loss; committed entries survive any failure.
- Strong consistency (no double-spend).
- Auditability for years.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 10M accounts, 50M tx/day. [assumption] 2. Tx ~200 B; retain 7+ years (regulatory). [constraint] 3. Synchronous replication. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
50M tx/day ~580/s avg, ~3k/s peak (batch/payroll).

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Banking Ledger, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
50M x 200 B = 10 GB/day; 7 years ~25 TB compressed; immutable.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Small payloads; correctness/durability dominate, not bandwidth.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Banking Ledger, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST /transfer | from,to,amount | tx id |
| GET |/accounts/:id/balance | | amount |

## 10. Data model
accounts(id); entries(id, account, delta, tx_id, ts) append-only; tx(id, debits[], credits[], status). Balance = fold of entries.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Tx[Transfer tx] --> Valid[Validate + double-entry]
  Valid --> Ledger[Append-only ledger, sync RF=3]
  Ledger --> Bal[Balance - derived]
  Ledger --> Recon[Reconcile vs banks]
  Ledger --> Audit[Audit store]
```

## 12. Request flow
Transfer validates (no negative), writes a balanced debit+credit transaction atomically to the append-only ledger (synchronous RF=3), derives balance, emits for reconciliation and audit.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Transfer tx
  participant C1 as Validate double-entry
  participant C2 as Append-only ledger, sync
  participant C3 as Balance derived
  participant C4 as Reconcile vs banks
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
Transaction service, ledger store, balance derivation, reconciliation, audit.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Append-only, strongly-durable ledger (synchronous RF=3, Raft-replicated or globally-consistent DB). Rejected: mutable balances (no audit), async replication (loss risk).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Balance cache (read); writes always on the ledger. Audit immutable.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Ledger partitioned by account id (co-locate an account's entries); cross-partition transfers as distributed transactions.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Synchronous RF=3 (a committed entry survives one failure). Cross-region async for DR with RPO target.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Strong: a transfer commits atomically (both entries or neither). Linearizable per account. No double-spend.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Mid-transfer failure -> atomic rollback (no partial). Ledger shard down -> those transfers fail (no loss/duplicate). Sync replica loss -> still quorum-safe. Reconciliation finds drift.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Mid-transfer failure"]
  R2["atomic rollback no partial"]
  C1 --> R2
  C3["Ledger shard down"]
  R4["those transfers fail no loss duplicate"]
  C3 --> R4
  C5["Sync replica loss"]
  R6["still quorum-safe"]
  C5 --> R6
```

## 20. Reliability strategy
SLI: data loss (0), double-spend (0); SLO 99.99%. Idempotent transfers. Chaos: kill a ledger replica mid-write, assert no loss/duplicate.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Strong auth; per-tx authorization; encryption at rest; full audit; regulatory access controls; tamper-evident.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Tx latency, commit success, reconciliation drift (0), data-loss guards, audit completeness.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Synchronous replication + retention (7y) + audit storage. Correctness non-negotiable; cost follows.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: double-entry ledger + sync replication. -> Stage 2: sharded by account + reconciliation. -> Stage 3: cross-region DR, regulatory retention. -> Stage 4: globally-consistent multi-region, real-time reconciliation.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: double-entry ledger sync replication."]
  S2["Stage 2: sharded by account reconciliation."]
  S3["Stage 3: cross-region DR, regulatory retention."]
  S4["Stage 4: globally-consistent multi-region, real-t"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Synchronous durability (no loss) vs latency. Append-only (audit) vs in-place edits. Sharding (scale) vs cross-shard tx. Retention (compliance) vs cost.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Mutable balances (no audit). Async replication (loss risk). Eventual consistency (double-spend). Single region (DR risk).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify loss tolerance (zero), audit, retention, regulation. Surface double-entry, append-only, sync replication, reconciliation.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/banking-ledger/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Ledger/payment: Level 10; transactions: Level 4; consensus: Level 4. Sources: `S-DYNAMO` `S-RAFT` `S-SPANNER`.

## 30. Practical exercises

1. Cross-shard transfer atomicity. 2. Reconcile after partial failure. 3. 7-year retention cost/tiering. 4. Zero-RPO multi-region. 5. Audit a disputed transaction.

---
Previous: Recommendation engine · Next: Stock-trading platform

