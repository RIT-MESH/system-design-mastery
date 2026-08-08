# Case Study: Identity & Access-Management Platform

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Issue and verify identities, manage sessions/tokens, and authorize access across many apps — a security-critical, high-availability root of trust. This is a advanced-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): authN (password/MFA), sessions, token issuance/validation, RBAC, SCIM provisioning. Out: social IdP, adaptive auth (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Authenticate users (password/MFA).
- Issue/validate tokens/sessions.
- Enforce authorization (RBAC).
- Provision/deprovision users (SCIM).
- Audit access.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Availability 99.99% (every app depends on it).
- Token validation p99 < 20 ms.
- Strong security; revocation works.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 10M users, 100 apps. [assumption] 2. 1k logins/s, 50k token validations/s. [assumption] 3. MFA on sensitive actions. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Token validation dominates (every API call); logins fewer. Read-heavy on the validation path.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Identity & Access-Management Platform, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Users, credentials (hashed), sessions, tokens, roles, audit logs. Small but security-critical.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Small payloads; bandwidth trivial. Latency + availability + security dominate.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Identity & Access-Management Platform, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design
| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST /login | creds | token |
| POST |/validate | token | valid/claims |
| GET /users/:id/roles | | roles |

## 10. Data model
users(id, creds_hash, mfa); sessions(id, user, exp); tokens(jti, user, scopes, exp, revoked); roles; audit(id, actor, action, ts).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  App --> IdP[IdP]
  IdP --> AuthN[AuthN + MFA]
  IdP --> Token[Token issuance]
  IdP --> Store[User/session/token store]
  App --> Val[Token validation] --> Store
  IdP --> Audit[Audit log]
  SCIM[SCIM] --> Store
```

## 12. Request flow
Login: verify creds + MFA -> issue session/token -> audit. API call: app validates token with IdP (or via JWKS locally) -> enforce RBAC -> audit. Provisioning via SCIM.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as IdP
  participant C1 as AuthN MFA
  participant C2 as Token issuance
  participant C3 as User session token store
  participant C4 as Token validation
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
AuthN/MFA, token service, session store, RBAC engine, validation (JWKS), SCIM, audit.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
User/session store: strongly-consistent, durable (sync replication). Token validation: JWKS public keys cached locally (stateless validation). Audit: append-only. Rejected: per-call DB lookup for validation (latency).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
JWKS cached at apps for stateless JWT validation; session cache; revoke via short TTLs + denylist.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Users partitioned by id; validation distributed (stateless JWKS); audit partitioned by date.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
User/session store RF=3 synchronous; JWKS keys replicated to all apps; audit durable.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Strong for authN (correct login). Tokens: revocation via short TTL + denylist (eventual). Audit append-only.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
IdP down -> logins fail (high impact) so multi-AZ + read replicas; token validation via cached JWKS continues (apps stay up). Key rotation must be safe (dual-active).

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["IdP down"]
  R2["logins fail high impact so multi-AZ read"]
  C1 --> R2
```

Each failure has a documented response: which component detects it, how failover happens, what the user experiences, and how recovery is verified. The design principle is that a single failure should degrade, not cascade. Bulkheads and circuit breakers prevent one slow dependency from exhausting shared resources. Cascading failure is the most dangerous mode and is prevented by timeouts on every outbound call.

## 20. Reliability strategy
SLI login success, validation latency; SLO 99.99%. Stateless validation keeps apps up during IdP issues. Chaos: kill IdP writes, assert apps still validate tokens.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Hashed creds (slow KDF), MFA, short token TTL + rotation, JWKS rotation, audit, least privilege, SCIM deprovision.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Login rate, MFA challenge rate, validation p99, token issuance, revocation events, failed-login spikes (abuse).

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Always-on critical infra (multi-AZ) + audit storage. 99.99% costs more redundancy.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: authN + sessions + tokens. -> Stage 2: stateless JWT validation (JWKS) + RBAC. -> Stage 3: SCIM + adaptive auth. -> Stage 4: multi-region, passwordless.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: authN sessions tokens."]
  S2["Stage 2: stateless JWT validation JWKS RBAC."]
  S3["Stage 3: SCIM adaptive auth."]
  S4["Stage 4: multi-region, passwordless."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Stateless validation (scale, survives IdP issues) vs revocation difficulty (short TTL + denylist). 99.99% (cost) vs 99.9%. Centralized IdP (consistency) vs SPOF.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Per-app auth (duplicated, inconsistent, insecure). Long-lived un-revocable tokens (unsafe). Per-call DB validation (slow).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify availability target, revocation, MFA. Surface stateless JWKS validation, short TTL + denylist, 99.99% redundancy.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/iam-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Auth/OIDC/JWT: Level 7; RBAC/zero-trust: Level 7. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. JWKS rotation with zero downtime. 2. Token revocation at scale. 3. Adaptive/MFA step-up. 4. Survive IdP write outage (apps stay up). 5. SCIM deprovision race.

---
Previous: API gateway · Next: Real-time analytics platform

