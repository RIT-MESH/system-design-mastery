# Case Study: Autonomous Support-Agent Team

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
A team of specialized AI agents (triage, research, resolution, review) that handle support tickets end to end, with a supervisor coordinating, a policy gateway approving high-risk actions, and full audit. This is a ai-systems-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): multi-agent ticket handling, RAG for knowledge, tool calling for ticketing systems, supervisor coordination, policy gateway, human approval for high-risk. Out: fully autonomous resolution without any human review (excluded for high-risk).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Triage agent classifies and routes tickets.
- Research agent retrieves relevant docs via RAG.
- Resolution agent drafts a response or action.
- Review agent checks quality and safety.
- Supervisor coordinates and approves.
- High-risk actions require human approval.
- Full audit.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Ticket-to-first-response < 30 s.
- No unauthorized high-risk action.
- Availability 99.9 percent.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 500 tickets/day, ~5 agent steps per ticket. [assumption] 2. 80 percent resolved by agents, 20 percent escalated to humans. [assumption] 3. High-risk = refunds, account changes, data access. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Bursty during business hours; each ticket triggers multiple LLM calls (triage + research + resolution + review).

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Autonomous Support-Agent Team, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Tickets + agent traces + RAG corpus + audit; moderate, must be auditable.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Agent-to-tool calls + LLM; moderate.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Autonomous Support-Agent Team, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /tickets (intake) -> agent team processes; GET /tickets/:id/trace; POST /tickets/:id/approve.

## 10. Data model
tickets(id, status, priority, assignee); agent_traces(ticket, agent, steps, tools, results); rag_corpus(chunks, embeddings, ACLs); audit(actor, action, ts, result).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Ticket --> Triage[Triage agent]
  Triage --> Sup[Supervisor]
  Sup --> Research[Research agent: RAG]
  Research --> Resolution[Resolution agent]
  Resolution --> Review[Review agent]
  Review --> Sup
  Sup -->|low risk| Close[Close ticket]
  Sup -->|high risk| Human[Human approval]
  Human --> Close
  All --> Audit[Audit log]
  Policy[Policy gateway] -.guards.-> Resolution
```

## 12. Request flow
Ticket arrives -> triage classifies -> supervisor routes to research (RAG) -> resolution drafts response or action -> review checks quality/safety -> supervisor: low-risk auto-close, high-risk human approval -> audit all steps.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Triage agent
  participant C1 as Supervisor
  participant C2 as Research agent RAG
  participant C3 as Resolution agent
  participant C4 as Review agent
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
Triage agent, research agent (RAG), resolution agent, review agent, supervisor, policy gateway, RAG, ticketing integration, audit.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Ticket store (relational); agent traces (append-only); RAG vector DB; audit (append-only, tamper-evident). Rejected: agents with direct unguarded tool execution.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
RAG results cached (permission-aware); common ticket patterns cached; agent traces not cached (audit).

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Tickets by tenant; RAG by tenant; agents stateless; supervisor per ticket.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Ticket store RF=3; audit append-only; RAG replicated; agents stateless.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Ticket status strongly tracked; agent traces append-only; RAG eventual; audit tamper-evident.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Agent fails -> supervisor retries or escalates. RAG down -> answer without grounding (disclaimer). LLM down -> queue ticket. Policy gateway down -> fail-closed (no actions).

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Agent fails"]
  R2["supervisor retries or escalates"]
  C1 --> R2
  C3["RAG down"]
  R4["answer without grounding disclaimer"]
  C3 --> R4
  C5["LLM down"]
  R6["queue ticket"]
  C5 --> R6
  C7["Policy gateway down"]
  R8["fail-closed no actions"]
  C7 --> R8
```

## 20. Reliability strategy
SLI ticket-to-response, resolution rate, zero-unauthorized-action; SLO 99.9 percent. Fail-closed policy gateway. Chaos: kill an agent, assert supervisor handles.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Policy gateway (no auto-high-risk); per-tenant RAG isolation; PII redaction; full audit; tool risk tiers; RBAC on approvals.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Ticket resolution rate, agent step count, cost per ticket, approval rate, unauthorized attempts (0), escalation rate, agent latency.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
LLM calls per ticket (5+); multi-model routing cuts cost (triage on small model, resolution on large).

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: single agent + RAG. -> Stage 2: multi-agent + supervisor + policy. -> Stage 3: review agent + evaluation + governance. -> Stage 4: enterprise agent platform, multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: single agent RAG."]
  S2["Stage 2: multi-agent supervisor policy."]
  S3["Stage 3: review agent evaluation governance."]
  S4["Stage 4: enterprise agent platform, multi-region."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Autonomy (speed) vs approval (safety). Multi-agent (specialization) vs single (simplicity). Auto-close (fast) vs review (safe).

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Single agent (no specialization). Full autonomy (unsafe). Human-only (slow).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify risk tiers, approval workflow, agent count. Surface multi-agent coordination, policy gateway, audit, and the human-approval principle.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/autonomous-support-agent-team/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Agentic systems: docs/ai-systems/08-agentic-systems; AI security: 09-ai-security; RAG: 06-basic-rag. Sources: `S-RAG` `S-VECTORDB`.

## 30. Practical exercises

1. Define agent risk tiers. 2. Supervisor escalation logic. 3. Policy gateway fail-closed design. 4. Cost per ticket with multi-model routing. 5. Audit replay for a disputed ticket.

---
Previous: Enterprise RAG platform · Next: LLM API gateway

