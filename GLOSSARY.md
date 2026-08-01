# Glossary

Definitions used consistently across the repository. Terms are introduced with a link to
their glossary entry on first use in each chapter. Where a term has a precise RFC or paper
definition, the SOURCES.md ID is noted.

## A–C

- **ACID** — Atomicity, Consistency, Isolation, Durability; transaction guarantees in RDBMS.
- **API gateway** — A single entry point that routes, authenticates, transforms, and rate-limits API traffic.
- **At-least-once delivery** — A message may be delivered more than once; receivers must deduplicate.
- **At-most-once delivery** — A message is delivered zero or one times; lost messages are not retried.
- **Availability** — The fraction of time a system successfully serves requests; often expressed in "nines" (e.g., 99.9% = three nines).
- **Backpressure** — Upstream signaling that a downstream cannot keep up; producers must slow down.
- **Bulkhead** — Isolating resources (threads, connections) per tenant/dependency so one failure cannot exhaust shared capacity.
- **Caching (cache-aside)** — App reads from cache; on miss, reads store and populates cache.
- **CAP theorem** — In a partition, choose consistency or availability; cannot have both (S-CAP).
- **CDN** — Content Delivery Network; geographically distributed edge caches for static/dynamic content.
- **Change Data Capture (CDC)** — Streaming row changes from a database's log to other systems.
- **Choreography** — Services react to events independently; no central orchestrator.
- **Circuit breaker** — Stops calling a failing dependency for a cooldown period to prevent cascading failure.
- **Consistent hashing** — A hashing scheme where adding/removing nodes moves only a fraction of keys (S-CHASH).
- **CRDT** — Conflict-free Replicated Data Type; replicas converge without coordination.
- **CQRS** — Command Query Responsibility Segregation; separate write and read models.

## D–F

- **Deduplication** — Removing duplicate messages/events using IDs or content hashes.
- **DNS** — Domain Name System; resolves names to IP addresses (S-DNS).
- **Edge computing** — Running compute close to users/data sources instead of central regions.
- **Error budget** — Allowed unavailability derived from an SLO (1 − SLO); balances reliability and velocity.
- **Eventual consistency** — Replicas may diverge temporarily but converge given no new updates.
- **Exactly-once** — Effective single-delivery, typically achieved via idempotency + transactional output (S-EXACTLYONCE).
- **Failover** — Promoting a standby to handle traffic after a primary failure.
- **Feature flag** — Runtime switch to enable/disable behavior without redeploying.

## G–L

- **GitOps** — Operating infrastructure from declarative state in Git, reconciled by an agent (S-ARMENTR).
- **gRPC** — RPC framework using HTTP/2 and Protocol Buffers (S-PROTOBUF, S-RFC9113).
- **Idempotency** — Repeating an operation has the same effect as doing it once.
- **Idempotency key** — Client-supplied key allowing the server to deduplicate retried requests.
- **IaC** — Infrastructure as Code; provisioning via declarative code.
- **Index (covering)** — An index containing all columns a query needs, avoiding table lookup.
- **Latency** — Time for one operation to complete; p50/p95/p99 are percentiles.
- **Leader election** — Choosing one node to coordinate; others follow (S-RAFT, S-PAXOS).

## M–R

- **Materialized view** — A precomputed, stored query result updated from base data.
- **Merkle tree** — A hash tree enabling efficient anti-entropy comparisons between replicas.
- **Multi-tenancy** — One system serving multiple isolated tenants.
- **Orchestration** — A central coordinator drives a multi-step workflow.
- **PACELC** — Extends CAP with latency/consistency trade-off when no partition (S-PACELC).
- **Partition (shard)** — A horizontal slice of data assigned to one node/range.
- **Quorum** — Minimum number of nodes that must agree/acknowledge (e.g., majority).
- **Rate limiting** — Constraining request rate per client/tenant to protect capacity.
- **Read-through / Write-through / Write-behind** — Cache read and write strategies with different consistency/cost trade-offs.
- **Replication** — Copying data across nodes for durability/availability.
- **Reverse proxy** — A server-side proxy receiving client traffic and forwarding to backends.
- **RPC** — Remote Procedure Call; invoking a function on a remote machine.

## S–Z

- **Saga** — A sequence of local transactions with compensating actions on failure.
- **Service mesh** — A sidecar layer handling inter-service traffic, mTLS, and observability (S-ISTIO).
- **Sharding** — Partitioning data across nodes, typically by a shard key.
- **SLI / SLO / SLA** — Service Level Indicator / Objective / Agreement (S-SLO).
- **Snowflake ID** — Time-based ID encoding epoch + worker + sequence (S-SNOWFLAKE).
- **Stateless service** — A service holding no per-request state in process; horizontally scalable.
- **Strangler pattern** — Incrementally replacing a legacy system by routing selected routes to new code.
- **Throughput** — Operations completed per unit time.
- **Thundering herd** — Many clients retrying simultaneously after an outage, overwhelming recovery.
- **Vector clock** — Per-node logical clock detecting concurrent updates (S-VECTORCLOCK).
- **Vector database** — Store optimized for similarity search over embeddings (S-VECTORDB).
- **Zero trust** — Never trust by network location; authenticate and authorize every request.
