# Case Study: Secure Network Agent

> **Tier:** network-ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
An enterprise agent that performs allowed network operations (read status, run diagnostics, draft changes, generate reports) under strict policies, approvals, RBAC, and an AI safety gateway, never executing high-risk or destructive actions autonomously. This is a network-ai-systems-tier system design challenge because it must handle multi-vendor device management while ensuring human approval for all high-risk changes. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): tool-calling agent for network ops, policy gateway, approval workflow, full audit, RBAC, local-model option for confidential configs. Out: autonomous high-risk execution (excluded by design).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Run allowed read and diagnostic tools.
- Draft (not execute) changes.
- Generate reports.
- Request approval for write actions.
- Enforce policies (no password or key exposure, no unapproved changes, no firewall or routing or VPN changes without approval).
- Full audit.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Never execute high-risk action without approval.
- Tool latency bounded.
- Availability 99.9 percent.
- Confidential configs stay local or air-gapped.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. ~50 tool calls per incident. 2. Most actions read or draft. 3. Air-gapped option for configs.

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
On-demand agent sessions (bursts during incidents); mostly tool calls and LLM inference.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Secure Network Agent, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Agent session state, tool results, approvals, audit; modest, must be tamper-evident.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Tool calls to devices plus LLM; moderate.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Secure Network Agent, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /agent/sessions; POST /agent/sessions/:id/messages; POST /approvals; GET /audit.

## 10. Data model
sessions(id, user, goal, state, steps); tools(name, spec, risk_level); approvals(id, action, status, approver); audit(actor, action, ts, result).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  Eng --> Agent[Agent planner-executor]
  Agent --> Policy[AI safety policy gateway]
  Policy --> Tools[Read and diagnostic tools]
  Policy --> Draft[Draft change]
  Policy --> Approve[Approval workflow]
  Approve --> Exec[Change management]
  Agent --> LLM[LLM local for configs]
  Tools --> Audit[Audit log]
  Draft --> Audit
  Exec --> Audit
```

## 12. Request flow
Engineer goals the agent -> planner-executor picks tools -> every action passes the policy gateway -> read and diagnostic allowed; write actions only draft; high-risk routed to approval workflow -> approved actions go to change management; confidential configs use local LLM; everything audited.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Agent planner-executor
  participant C1 as AI safety policy gateway
  participant C2 as Read and diagnostic tool
  participant C3 as Draft change
  participant C4 as Approval workflow
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
Planner-executor agent, tool registry (with risk levels), policy gateway, approval workflow, change management, local or external LLM, audit.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Session and state store; tool registry; approvals (relational, audited); audit (append-only, tamper-evident). Rejected: agent with direct unguarded tool execution.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Session state cached; common tool results cached (permission-aware).

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Sessions by user; audit by date; tools central registry.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Session store RF=3; audit append-only replicated; agent stateless-ish (state externalized).

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Approvals strongly consistent (audit). Agent state per session. Tool results advisory except committed changes.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
LLM down -> degrade to deterministic tools or queue. Policy gateway down -> fail-closed (no actions). Tool fails -> report and retry. Approval timeout -> no action.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["LLM down"]
  R2["degrade to deterministic tools or queue"]
  C1 --> R2
  C3["Policy gateway down"]
  R4["fail-closed no actions"]
  C3 --> R4
  C5["Tool fails"]
  R6["report and retry"]
  C5 --> R6
  C7["Approval timeout"]
  R8["no action"]
  C7 --> R8
```

## 20. Reliability strategy
SLI tool success, approval correctness, zero-unauthorized-action; SLO 99.9 percent. Fail-closed policy gateway. Chaos: kill policy gateway, assert no actions executed.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations

RBAC; policy gateway (never passwords or keys, never unapproved changes, never firewall or routing or VPN changes, never outside maintenance windows, never configs to unauthorized users or models); audit; local model for confidential configs; air-gapped option.

## 22. Observability strategy
Tool call rate, approval rate, policy denials, unauthorized-action attempts (0), agent latency, cost, audit completeness.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
LLM inference (tokens) plus tool execution. Multi-model routing plus local model for configs cut cost and risk.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: single agent + policy gateway + audit. -> Stage 2: approval workflow + RBAC + local model. -> Stage 3: multi-agent + supervisor agent + memory. -> Stage 4: enterprise agent platform, air-gapped, governance.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: single agent policy gateway audit."]
  S2["Stage 2: approval workflow RBAC local model."]
  S3["Stage 3: multi-agent supervisor agent memory."]
  S4["Stage 4: enterprise agent platform, air-gapped, g"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Autonomy (speed) vs approval (safety) -> approval for risk. Local model (privacy and air-gap) vs external (quality). Draft (safe) vs execute (fast).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Full autonomy (unsafe). No policy gateway (no guardrails). No audit (no accountability).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify allowed tools, risk tiers, approval workflow, air-gap need. Surface planner-executor, policy gateway, approval, audit, and the no-autonomous-high-risk principle.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/secure-network-agent/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Agentic systems: docs/ai-systems; AI safety gateway; change management: Level 6; RBAC: Level 7. Sources: `S-RAG` `S-VECTORDB`.

## 30. Practical exercises

1. Define tool risk tiers. 2. Policy gateway fail-closed design. 3. Local-model-only mode for configs. 4. Approval workflow with quorum. 5. Audit replay for an incident.

---
Previous: Network digital twin · Next: Enterprise RAG platform

