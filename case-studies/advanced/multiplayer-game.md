# Case Study: Online Multiplayer Game

> **Tier:** advanced · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
Real-time authoritative game state, low-latency input replication, and matchmaking — latency-critical, stateful-server, large-fan-out state. This is a advanced-tier system design challenge because it must handle real-time latency under load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In (v1): real-time match, authoritative server, state sync, matchmaking. Out: persistence, anti-cheat (noted).

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Match players.
- Run authoritative game state on a server.
- Replicate state to players at ~tick rate.
- Persist match results.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- Tick-to-player latency < 100 ms. - 60 ticks/s authoritative loop.
- Availability 99.9% per match.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1M concurrent players, 100k matches. [assumption] 2. 64 players/match, 60 ticks/s. [assumption] 3. State delta ~1 KB/tick. [assumption]

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
1M players x 60/s inputs + state deltas — very high small-message rate; UDP for latency.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For Online Multiplayer Game, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Match state ephemeral; results + player profiles persisted.

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
State deltas: 100k matches x 64 x 60/s x ~small — significant aggregate; per-match modest.

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For Online Multiplayer Game, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

UDP game protocol for state; REST for matchmaking/profile; WebSocket optional.

## 10. Data model
match_state(match, authoritative); player profile; match results. State in-memory on the game server.

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% created-for: system-design-mastery
flowchart LR
  P1 & P2 & P3 --> GS[Game server - authoritative, 60 tps]
  GS -->|state delta (UDP)| P1 & P2 & P3
  MM[Matchmaker] --> GS
  GS --> Persist[Persist results]
  GS --> AntiCheat[Anti-cheat]
```

## 12. Request flow
Matchmaker forms a match -> allocates a game server -> players send inputs (UDP) -> authoritative server advances state 60 tps -> replicates deltas to all -> on end, persist results.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Game server authoritativ
  participant C1 as Matchmaker
  participant C2 as Persist results
  participant C3 as Anti-cheat
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
Matchmaker, game servers (authoritative), state replicator, persistence, anti-cheat.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
In-memory authoritative state; profiles/results in a durable store. Rejected: client-authoritative (cheating).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Profiles cached; match state is the in-memory authoritative cache.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Per-match server (one match per server instance); matchmaking sharded by region/skill.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Game server is the authority; no replication needed for correctness (a crash ends the match — migrate/handoff is advanced). Region-based for latency.

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Authoritative: the server is the single source of truth; clients see lagging projections. Strong within a match.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Game server crash -> match ends (or handoff to a standby for high-tier). Player disconnect -> timeout -> forfeit/stand-in. Matchmaker down -> no new matches.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Game server crash"]
  R2["match ends or handoff to a standby for h"]
  C1 --> R2
  C3["Player disconnect"]
  R4["timeout -> forfeit stand-in"]
  C3 --> R4
  C5["Matchmaker down"]
  R6["no new matches"]
  C5 --> R6
```

## 20. Reliability strategy
SLI tick latency, match completion; SLO 99.9% per match. Region placement for latency. Chaos: kill a game server, assert graceful match end.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Client-authoritative forbidden (cheat); input validation; anti-cheat on server; rate-limit inputs.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
Tick rate stability, p99 tick-to-player latency, match completion, disconnect rate, server CPU.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
Compute (one server per match) dominates; autoscale game servers by match demand; region placement.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: authoritative servers + matchmaker. -> Stage 2: region placement + UDP state sync. -> Stage 3: server handoff on crash, anti-cheat. -> Stage 4: large-world sharding, persistence.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: authoritative servers matchmaker."]
  S2["Stage 2: region placement UDP state sync."]
  S3["Stage 3: server handoff on crash, anti-cheat."]
  S4["Stage 4: large-world sharding, persistence."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Authoritative (anti-cheat) vs server cost. UDP (latency) vs TCP (reliability). 60 tps (smooth) vs CPU. Region (latency) vs matchmaking breadth.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
Client-authoritative (cheating). TCP state (latency). Single global server (latency).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify tick rate, latency, anti-cheat, region. Surface authoritative server, UDP state sync, region placement.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/multiplayer-game/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
Real-time/edge: Level 10; UDP: Level 0; autoscaling: Level 9. Sources: `S-CHASH` `S-DYNAMO`.

## 30. Practical exercises

1. Server handoff on crash mid-match. 2. Lag compensation. 3. 1000-player large-world sharding. 4. Matchmaking by skill across regions. 5. Anti-cheat design.

---
Previous: Airline-reservation · Next: Collaborative document editor

