# Case Study: Video-Conferencing System

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Real-time multiparty audio/video calls: low-latency media transport, selective forwarding, and presence — a stateful, real-time media system. This is a advanced-tier system design challenge because it must handle real-time latency under load while ensuring low-latency bidirectional communication. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): 1:1 and small-group calls, audio/video, screen share, presence. Out: large webinars, recording/transcription (stage).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Start/join a call.
- Send/receive audio/video with low latency.
- Selectively forward each participant media.
- Show presence; mute/leave.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- One-way media latency < 200 ms. - 30 fps video; audio priority.
- Availability 99.9 percent (calls are real-time, no retries).

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M concurrent calls, ~4 participants avg. [assumption] 2. Video ~1.5 Mbps/participant. [assumption] 3. UDP/SRTP transport. [constraint]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Real-time media flows; high aggregate bandwidth; small control messages.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Video-Conferencing System, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Call metadata; recordings (if enabled) to object storage. Live media is in-flight, not stored.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
N x N media forwarding — dominant; selective forwarding (SFU) cuts it from mesh to star.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Video-Conferencing System, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

signaling over WS; media over UDP/SRTP; REST for room/presence.

## 10. Data model
rooms(id, participants, sfu); presence(user, room); signaling state per room. Media is live streams, not persisted.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  P1 & P2 & P3 --> SFU[Selective forwarding unit]
  SFU -->|forward per layer| P1 & P2 & P3
  P1 & P2 & P3 --> Sig[Signaling] --> Room[Room svc]
  Room --> Pres[Presence]
```

## 12. Request flow
Participants signal to a room -> media sent to an SFU (not a mesh) -> SFU selectively forwards each participant media to others (per-layer/bandwidth) -> presence updates. On leave, teardown.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Selective forwarding uni
  participant C1 as Signaling
  participant C2 as Room svc
  participant C3 as Presence
  C0 ->> C1: send request
  C1 ->> C2: validate and process
  C2 ->> C3: query or persist
  C3 -->> C2: result
  C2 -->> C1: response
  C1 -->> C0: response
  alt operation succeeds
    C0 -->> C0: confirm
  else operation fails
    C3 -->> C3: log error
    C0 -->> C0: retry with backoff
  end
```

## 13. Component responsibilities
Signaling, room service, presence, SFU (media), recording (optional).

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Room/presence: in-memory + a fast store; recordings to object storage. Rejected: mesh (N^2 bandwidth); recording live media to a DB.

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Room/presence in memory; hot room metadata cached.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
SFU instances per call (one call's media on one SFU); rooms sharded by id; signaling by room.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Presence/rooms replicated for availability; an SFU loss ends/migrates a call (real-time, can't replay). Region-based for latency.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Call state strongly tracked per room (who's in). Media is real-time (no consistency, just latency). Presence eventual.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
SFU down -> call drops or migrates to another SFU (best-effort). Participant network loss -> jitter buffer; degrade quality. Signaling down -> can't start calls.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["SFU down"]
  R2["call drops or migrates to another SFU be"]
  C1 --> R2
  C3["Participant network loss"]
  R4["jitter buffer"]
  C3 --> R4
  C5["Signaling down"]
  R6["can't start calls"]
  C5 --> R6
```

## 20. Reliability strategy
SLI media latency, call setup time, drop rate; SLO 99.9 percent. Region placement + graceful degradation. Chaos: kill an SFU, assert graceful call migration/drop.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
E2E/SRTP encryption; per-room auth; media isolation; rate-limit signaling; no recording without consent.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
One-way latency, jitter, packet loss, call setup time, drop rate, SFU load, concurrent calls.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Media egress + SFU compute (always-on, real-time) dominate. SFU per-call sizing; region placement for egress.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: signaling + SFU. -> Stage 2: per-call SFU + presence. -> Stage 3: simulcast/multilayer + recording. -> Stage 4: large webinars (one-to-many), multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: signaling SFU."]
  S2["Stage 2: per-call SFU presence."]
  S3["Stage 3: simulcast multilayer recording."]
  S4["Stage 4: large webinars one-to-many , multi-regio"]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
SFU (scales bandwidth vs mesh) vs extra hop. UDP (latency) vs reliability (jitter buffer). E2E encryption (privacy) vs server processing (SFU needs media). Region (latency) vs cross-region signaling.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Mesh (N^2 bandwidth, doesn't scale). TCP media (latency). Record everything (cost/privacy).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify participants, latency, E2E, recording. Surface SFU, UDP/SRTP, signaling vs media split, degradation.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/video-conferencing/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Real-time/edge: Level 10; UDP: Level 0; presence/real-time: chat case. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Simulcast/multilayer bitrate adaptation. 2. SFU failover mid-call. 3. Large webinar (one-to-many) fanout. 4. E2E encryption with an SFU. 5. Reconnect after a network drop.

---
Previous: Real-time analytics platform · Next: Online multiplayer game

