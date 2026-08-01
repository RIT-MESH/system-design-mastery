# Case Study: Real-Time Voice-Agent Platform

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  User --> STT[Speech to text]
  STT --> LLM[LLM + RAG]
  LLM --> Policy[Policy gateway]
  Policy --> Tools[Read tools]
  Policy --> Draft[Draft high-risk]
  Draft --> Approve[Human approval]
  LLM --> TTS[Text to speech]
  TTS --> User
  All --> Audit[Audit log]
```


## 28. Original Mermaid diagrams

Standalone sources under `diagrams/case-studies/real-time-voice-agent-platform/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. Request sequence and failure flow:

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant P0 as Client
  participant P1 as Real-Time Voice-Agent Pl
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
  C1["STT error"]
  R2["ask to repeat"]
  C1 --> R2
  C3["LLM down"]
  R4["canned responses"]
  C3 --> R4
  C5["TTS down"]
  R6["text-only"]
  C5 --> R6
  C7["Policy down"]
  R8["fail-closed"]
  C7 --> R8
```

## 1. Problem statement

A voice-operated assistant that transcribes speech, reasons with an LLM, and responds with synthesized speech in real time, with high-risk action guardrails.

This system sits at the intersection of distributed systems and operational reliability. The design must balance latency versus durability while ensuring no single component failure cascades. The target audience includes engineers and operators, so the design must be observable, debuggable, and reversible.
## 2. Scope

In: speech-to-text, LLM reasoning with RAG, text-to-speech, tool calling, policy gateway. Out: autonomous high-risk execution.

The scope boundary is deliberate: including too much in v1 risks a system that is broad but shallow. Each excluded feature is a candidate for a later iteration once the core loop is proven.
## 3. Functional requirements

- Transcribe user speech in real time. - Reason with LLM + RAG. - Respond with synthesized speech. - Call read-only tools. - Draft (not execute) high-risk actions. - Enforce policy gateway. - Full audit.

These requirements drive the architecture: the read-heavy pattern pushes toward caching; the durability requirement forces synchronous writes; the idempotency requirement means every write path handles redelivery without double-application.
## 4. Non-functional requirements

- Turn latency < 1.5 s. - Availability 99.9 percent. - No autonomous high-risk execution.

The non-functional targets shape every component choice: the latency SLO forces edge caching and limits synchronous cross-region calls; the availability target drives redundancy (RF=3, multi-AZ); the cost target constrains the model size.
## 5. Explicit assumptions

1. 100 concurrent sessions. 2. Avg 5 turns. 3. High-risk requires approval.

These assumptions are the load-bearing facts of the design. If any is wrong by an order of magnitude, the architecture must adapt: 10x more traffic may require sharding earlier; a different read-write ratio changes the caching strategy entirely.
## 6. Traffic estimation

100 concurrent sessions; each turn = STT + LLM + TTS (3 inference calls).

The traffic estimate reveals the binding constraint. Peak is modeled at 10x average. The read-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy), which changes the storage and replication strategy.
## 7. Storage estimation

Session state + transcripts + RAG + audit; moderate, must be auditable.

Storage growth is linear with time and must be planned with retention. The estimate includes metadata and index overhead (20-30 percent above raw). Without a retention policy, storage grows unboundedly.
## 8. Bandwidth estimation

Audio streams (real-time); text small; moderate aggregate.

Bandwidth is often not the binding constraint but becomes significant at the edge during viral spikes. CDN and edge caching cut origin egress; compression cuts bandwidth by 50-80 percent where applicable.
## 9. API design

WS /voice (bidirectional audio) -> text + audio responses.

The API follows REST for external clients and gRPC for internal calls. Every write endpoint accepts an idempotency key. Rate limiting is enforced at the gateway before the service tier.
## 10. Data model

sessions(id, user, state, turns[]); transcripts(session, turn, text); audit(actor, action, ts).

The data model is designed around the access pattern, not the entity shape. The primary access path determines the partition key; secondary paths determine indexes. Denormalization is applied selectively where the hot read path would otherwise require expensive joins.
## 12. Request flow

User speaks -> STT transcribes -> LLM reasons with RAG -> policy: read-only tools allowed, high-risk drafted for approval -> LLM generates response -> TTS synthesizes -> user hears; all audited.

The request flow reveals the critical path: any component on the hot path that fails or slows degrades the user experience. The design applies timeouts, circuit breakers, and bulkheads to each hop. The write path includes an idempotency check before any state mutation.
## 13. Component responsibilities

STT engine, LLM + RAG, policy gateway, TTS engine, tool registry, approval workflow, audit.

Each component has a single, well-defined responsibility. The gateway handles auth and routing; the service tier is stateless and horizontally scalable; the data tier is the stateful core, carefully partitioned and replicated. The separation allows each tier to scale independently.
## 14. Database selection

Session store (in-memory + persistent); RAG vector DB; transcripts (object storage); audit (append-only).

The database choice is driven by the access pattern. The rejected alternatives were rejected for specific reasons: a relational DB was rejected if the workload is a single key lookup at massive scale; a KV store was rejected if joins and transactions are needed.
## 15. Caching strategy

RAG results cached (permission-aware); common voice patterns cached; TTS output cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default; write-through is used where read-after-write consistency is required. Stampede protection is applied to any key that can go viral. Cache entries are namespaced by tenant.
## 16. Partitioning strategy

Sessions by user; RAG by namespace; gateway stateless; STT/TTS by concurrency.

The partition key co-locates related data while distributing load evenly. Consistent hashing with virtual nodes minimizes data movement when nodes change. A hot key is mitigated by caching, extra replication, or key splitting.
## 17. Replication strategy

Session RF=3; RAG replicated; STT/TTS stateless; gateway stateless.

Replication is synchronous on the write-confirmation path where durability is critical and asynchronous elsewhere. RF=3 tolerates one failure. Failover is tested, not just configured. Cross-region replication is asynchronous with a documented RPO.
## 18. Consistency model

Session strongly tracked; RAG eventual; audit append-only; policy fail-closed.

The consistency model is the weakest that users can tolerate. Read-your-writes is provided where the user expects to see their own write. Eventual consistency is bounded (seconds) and monitored. The system documents what eventual means to users.
## 19. Failure scenarios

STT error -> ask to repeat. LLM down -> canned responses. TTS down -> text-only. Policy down -> fail-closed.

Each failure scenario has a documented response: which component detects it, how failover happens, what the user experiences, and how recovery is verified. Bulkheads and circuit breakers prevent one slow dependency from cascading.
## 20. Reliability strategy

SLI turn latency, zero-unauthorized-action; SLO 99.9 percent. Fail-closed policy.

The SLO defines what good means measurably; the error budget is the allowed unavailability spent on deploys and feature risk. The system is tested with chaos engineering to verify resilience. An untested failover is not a failover.
## 21. Security considerations

Policy gateway (no auto-high-risk); PII redaction in transcripts; voice biometrics; RBAC; audit.

Security is defense in depth: TLS, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed: on any error, the system refuses to act.
## 22. Observability strategy

Turn latency, STT accuracy, LLM latency, TTS latency, policy denials, unauthorized (0), cost per session.

Observability uses logs, metrics, and traces with correlation IDs. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not raw thresholds. The on-call runbook for each alert is tested.
## 23. Cost considerations

STT + LLM + TTS = 3 inference calls per turn; route to small model when possible; cache RAG.

Cost is dominated by the binding resource. Primary levers: caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing. Cost is tracked as a first-class metric and alerted on when unit cost spikes.
## 24. Scaling stages

Stage 1: STT + LLM + TTS. -> Stage 2: policy + RAG + tools. -> Stage 3: multi-agent + biometrics. -> Stage 4: multi-region + edge.

The scaling stages are triggered by specific thresholds, not by calendar. Each stage is a deliberate architectural change: Stage 1 handles initial load; Stage 2 when a single node saturates; Stage 3 when latency exceeds the SLO; Stage 4 when hot keys threaten the origin.
## 25. Trade-offs

Voice (hands-free) vs text (precise). Autonomy (speed) vs approval (safety). Cloud (quality) vs local (privacy). Turn latency vs model size.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct; it presents the chosen option, the rejected alternative, and the workload-specific reason.
## 26. Alternative designs

Text-only (no hands-free). Full autonomy (unsafe). No policy (no guardrails). Batch STT (too slow).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements that make them inferior here but not universally inferior.
## 27. Interview discussion points

Clarify latency, concurrency, risk tiers, approval. Surface STT-LLM-TTS pipeline, policy gateway, RAG, audit.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply, discuss failure modes explicitly, and offer an alternative with a reason.
## 29. Further reading

Voice agent refs; docs/ai-systems/08-agentic-systems; security: 09-ai-security; RAG: 06-basic-rag; video-conferencing case.

The further reading cites primary sources (RFCs, papers, official documentation) via stable IDs in SOURCES.md, not secondary blog posts. Each citation is chosen because it is the authoritative source for a specific technical claim.
## 30. Practical exercises

1. Turn-latency budget. 2. Policy gateway for voice. 3. PII in transcripts. 4. Fail-closed design. 5. Edge deployment.


---
Previous: Multimodal document · Next: GPU workload scheduler

The exercises push the reader beyond v1: re-estimating at 10x reveals capacity limits; adding a new requirement forces an architectural change; designing the failover test reveals whether resilience claims are real.
