# Case Study: GPU Workload Scheduler

> **Tier:** ai-systems · **Status:** complete · Original numbers and diagrams.

## 1. Problem statement
A scheduler managing a GPU cluster for mixed workloads (serving, training, batch) with gang scheduling, priorities, preemption, and utilization optimization. This is a ai-systems-tier system design challenge because it must handle high availability under peak load while ensuring no single point of failure. The design must be production-grade: observable, debuggable, reversible, and able to survive component failures without data loss or cascading outages.

## 2. Scope
In: GPU pool, workload queues, gang scheduling, priorities, preemption, utilization. Out: multi-cluster federation.

These boundaries are deliberate. Including more in the first version would spread effort thin and delay shipping a working core. Each excluded feature — noted as a scaling stage — is a candidate for the next iteration once the core loop is proven in production and the team has operational confidence in the baseline architecture.

## 3. Functional requirements
- Queue workloads by type.
- Allocate GPUs with gang scheduling for distributed training.
- Prioritize serving over batch.
- Preempt and checkpoint long jobs.
- Report utilization.
- Backfill spare capacity.

Each requirement has a direct architectural consequence. The read-heavy or write-heavy pattern determines the caching strategy. The durability requirement determines whether replication is synchronous or asynchronous. The idempotency requirement means every write path must handle redelivery without double-application — a design constraint that shapes the entire API and data model.

## 4. Non-functional requirements
- GPU utilization > 70 percent.
- Serving not impacted by batch.
- No deadlock from partial gang.

These targets are not aspirational — they are design constraints that shape every component choice. The latency SLO forces edge caching and limits synchronous cross-region calls on the hot path. The availability target drives a replication factor of 3 and multi-AZ deployment. The cost target constrains the model size, storage tier, and over-provisioning margin. Every architectural decision in this case study traces back to one of these targets.

## 5. Explicit assumptions
1. 1000 GPUs, 50 percent serving, 30 percent training, 20 percent batch. 2. Training 1-24h. 3. Serving autoscaled.

These assumptions are load-bearing: if any is wrong by an order of magnitude, the architecture must adapt. Ten times more traffic may require sharding earlier. A different read-write ratio changes the caching strategy entirely. The peak multiplier affects headroom sizing. State them explicitly, revisit them after launch, and parameterize the design by these numbers rather than locking to them.

## 6. Traffic estimation
Serving continuous; training/batch queued; scheduler low-QPS.

To derive the request rate: divide the daily volume by 86,400 seconds to get the average rate, then multiply by 5-10x for peak. The read-to-write ratio determines whether the system is cache-dominated (read-heavy) or write-path-dominated (write-heavy). For GPU Workload Scheduler, this ratio shapes the entire storage and replication strategy.

## 7. Storage estimation
Job state + checkpoints + metrics; checkpoints large (GBs per model).

Storage grows linearly with time. Daily growth multiplied by the retention period gives total storage. Add 20-30 percent for index overhead. Compression can reduce effective storage by 50-80 percent. The replication factor multiplies the total. Without a retention policy, storage grows without bound and cost becomes unsustainable.

## 8. Bandwidth estimation
Model loading (GBs); checkpoint save/restore (GBs).

Bandwidth is request rate multiplied by average payload size for ingress, and response rate multiplied by response size for egress. CDN and edge caching reduce origin egress. Compression reduces bandwidth by 50-80 percent where applicable. For GPU Workload Scheduler, bandwidth may or may not be the binding constraint — compare it against compute and storage to find out.

## 9. API design

POST /jobs (type, gpu_req, priority) -> job id; GET /jobs/:id/status; POST /jobs/:id/preempt.

## 10. Data model
jobs(id, type, gpu_count, status, priority, checkpoint_ref); gpus(id, node, memory, status); allocations(job, gpus[]).

The data model is designed around the access pattern, not the entity shape. The primary lookup path determines the partition key. Secondary access paths determine which indexes to build. Denormalization is applied selectively where the hot read path would otherwise require expensive joins — with CDC or the outbox pattern keeping the denormalized view consistent with the source of truth.

## 11. High-level architecture

```mermaid
%% origin: original to system-design-mastery
flowchart LR
  Train[Training] & Batch[Batch] --> Q[Priority queue]
  Serve[Serving reservations] --> Alloc[GPU allocation]
  Q --> Sched[Scheduler: gang, backfill, preempt]
  Sched --> Alloc
  Alloc --> GPUs[GPU cluster]
  GPUs -.utilization.-> Sched
```

## 12. Request flow
Training and batch queued -> scheduler gang-schedules (all GPUs or none) -> serving reserved -> batch backfills spare -> long jobs preempted for priority -> checkpoints saved -> utilization reported.

```mermaid
%% created-for: system-design-mastery
sequenceDiagram
  participant C0 as Training
  participant C1 as Batch
  participant C2 as Priority queue
  participant C3 as Serving reservations
  participant C4 as GPU allocation
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
Job queue, gang scheduler, GPU allocator, preemption manager, checkpoint manager, utilization monitor.

Each component has a single, well-defined responsibility. The gateway handles authentication and routing. The service tier is stateless and horizontally scalable. The data tier is the stateful core, carefully partitioned and replicated. This separation allows each tier to scale independently: stateless tiers add replicas with demand; the stateful tier scales by sharding or read replicas.

## 14. Database selection
Job state (transactional); GPU registry; checkpoints (object storage).

The database choice is driven by the access pattern, not by familiarity. A relational database was chosen or rejected based on whether the workload needs joins and transactions. A key-value store was chosen or rejected based on whether the workload is a single-key lookup at massive scale. The rejected alternatives were rejected for specific, workload-dependent reasons — not because they are bad databases, but because they are the wrong fit for this system.

## 15. Caching strategy
Hot job metadata cached; GPU status cached; model weights cached on GPU.

The caching strategy is designed around the staleness tolerance of the workload. Cache-aside is the default — simple and lazy. Write-through is used where read-after-write consistency matters. Stampede protection (request coalescing or stale-while-revalidate) is applied to any key that can go viral. Cache entries are namespaced by tenant where multi-tenancy applies, preventing cross-tenant leakage.

## 16. Partitioning strategy
Scheduler per cluster; jobs by priority; GPUs by node.

The partition key co-locates related data so queries do not fan out across shards, while distributing load evenly so no single shard is hot. Consistent hashing with virtual nodes minimizes data movement when nodes are added or removed. A hot key — a viral entity or a giant tenant — is mitigated by caching, extra replication, or key splitting, not by adding more shards.

## 17. Replication strategy
Job state RF=3; checkpoints durable; scheduler HA (leader-elected).

Replication is synchronous on the write-confirmation path where durability is critical — the commit waits for at least one follower before acknowledging. Elsewhere it is asynchronous for throughput. A replication factor of 3 tolerates one failure while maintaining quorum. Failover is tested, not just configured: a follower that was never promoted will fail when you need it most.

## 18. Consistency model
Job state strongly consistent; GPU allocation atomic; checkpoints versioned.

The consistency model is chosen as the weakest that users can tolerate, because stronger consistency costs latency and availability. Read-your-writes is provided where the user expects to see their own write immediately. Eventual consistency is bounded — seconds, not unbounded — and monitored. The system documents what 'eventual' means to users rather than hiding it.

## 19. Failure scenarios
Scheduler down -> jobs continue (allocations persist). Gang deadlock -> timeout + release. GPU failure -> reallocate. Checkpoint corrupt -> restart.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  C1["Scheduler down"]
  R2["jobs continue allocations persist"]
  C1 --> R2
  C3["Gang deadlock"]
  R4["timeout release"]
  C3 --> R4
  C5["GPU failure"]
  R6["reallocate"]
  C5 --> R6
  C7["Checkpoint corrupt"]
  R8["restart"]
  C7 --> R8
```

## 20. Reliability strategy
SLI utilization, serving latency, no-deadlock; SLO 99.9 percent. Checkpoint recovery.

The SLO defines what 'good' means measurably. The error budget — the difference between 100 percent and the SLO — is the allowed unavailability that can be spent on deploys and feature risk. When the budget is nearly exhausted, risky changes are frozen. The system is tested with chaos engineering to verify that resilience assumptions hold. An untested failover is not a failover.

## 21. Security considerations
Per-team GPU quotas; job isolation (container); no cross-team access; audit.

Security is defense in depth: TLS in transit, encryption at rest, RBAC with default-deny, PII redaction in logs, audit trails for every state-changing operation, and per-tenant isolation. For AI-augmented systems, the policy gateway is fail-closed — on any error, the system refuses to act rather than allowing an unguarded action.

## 22. Observability strategy
GPU utilization, job latency, queue depth, preemption rate, gang success rate, checkpoint time.

Observability uses the three signals — logs, metrics, and traces — with correlation IDs to stitch a single request across services. The golden signals (latency, traffic, errors, saturation) are the first dashboard. Alerts fire on SLO burn rate, not on raw thresholds, to avoid noise. The on-call runbook for each alert is tested, not theoretical.

## 23. Cost considerations
GPU-seconds dominate; utilization is the lever. Backfill + gang + priority maximize utilization.

Cost is dominated by the binding resource identified in the traffic estimate. The primary levers are caching (cuts read cost), tiering (cuts storage cost), batching (cuts per-request overhead), and right-sizing (no over-provisioned idle capacity). Cost is tracked as a first-class metric — cost per request, cost per tenant, cost per outcome — and alerted on when unit cost spikes.

## 24. Scaling stages
Stage 1: queue + allocate. -> Stage 2: gang + preempt + backfill. -> Stage 3: multi-cluster + spot. -> Stage 4: multi-region.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  S1["Stage 1: queue allocate."]
  S2["Stage 2: gang preempt backfill."]
  S3["Stage 3: multi-cluster spot."]
  S4["Stage 4: multi-region."]
  S1 --> S2
  S2 --> S3
  S3 --> S4
```

## 25. Trade-offs
Serving (latency) vs batch (throughput). Gang (no deadlock) vs packing (utilization). Preempt (utilization) vs wasted compute.

Every trade-off has a rejected alternative with a reason. The design does not present one option as universally correct — it presents the chosen option, the rejected alternative, and the workload-specific reason for the choice. This is what makes the design defensible in a review: the reviewer can challenge any decision and find the reasoning documented.

## 26. Alternative designs
No gang (deadlock). No preempt (low utilization). No backfill (idle). Static (inflexible).

The alternative designs are genuine architectures that would work under different constraints. They were rejected for this workload because of specific requirements — latency SLO, cost budget, consistency need — that make them inferior here but not universally inferior. Understanding why an alternative was rejected is as important as understanding why the chosen design was selected.

## 27. Interview discussion points
Clarify GPU count, workload mix, serving SLA, training duration. Surface gang, preemption, backfill, utilization.

In an interview, the strongest candidates clarify ambiguity before designing, surface the read-write ratio and the binding resource, design the hot path deeply rather than just drawing boxes, discuss failure modes explicitly, and offer an alternative with a reason. The weakest candidates draw boxes before clarifying scope, name a vendor product as the architecture, and skip failure modes entirely.

## 28. Original Mermaid diagrams
Standalone sources under `diagrams/case-studies/gpu-workload-scheduler/`: `context.mmd`, `request-sequence.mmd`, `failure-flow.mmd`, `scaling-evolution.mmd`. The diagrams are embedded in their respective sections: architecture in section 11, request flow in section 12, failure scenarios in section 19, and scaling stages in section 24.

## 29. Further reading
GPU scheduling: docs/10-extreme-scale/08-gpu-batch-scheduling; model serving: docs/ai-systems/11-model-serving. Sources: `S-VECTORDB` `S-RAG`.

## 30. Practical exercises

1. Gang schedule 4-GPU training. 2. Preempt with checkpoint. 3. Backfill batch into spare. 4. Utilization > 80 percent. 5. Multi-cluster federation.

---
Previous: Real-time voice agent · Next: Multi-model routing platform

