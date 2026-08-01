# Backlog

The complete list of remaining chapters and case studies. Status:

- ✅ done · 🚧 in progress · 🔲 planned

This backlog drives issue creation (see `.github/ISSUE_TEMPLATE/new-chapter.md` and
`new-case-study.md`). Milestone ownership is noted per item (see [ROADMAP.md](ROADMAP.md)).

## Curriculum chapters

### Level 0 — Prerequisites (M2)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/00-prerequisites/00-computing-fundamentals.md` | Computing fundamentals |
| ✅ | `docs/00-prerequisites/01-networking-http.md` | Networking & HTTP |
| ✅ | `docs/00-prerequisites/02-os-linux.md` | OS & Linux fundamentals |
| ✅ | `docs/00-prerequisites/03-complexity-data-structures.md` | Time/space complexity; basic data structures |
| ✅ | `docs/00-prerequisites/05-db-basics.md` | Basic database concepts |

### Level 1 — Foundations (M2)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/01-foundations/00-requirements-and-quality-attributes.md` | Requirements & quality attributes |
| ✅ | `docs/01-foundations/01-capacity-planning.md` | Capacity planning |
| ✅ | `docs/01-foundations/02-scalability.md` | Scalability; stateless vs stateful |
| ✅ | `docs/01-foundations/03-redundancy-fault-tolerance.md` | Redundancy, fault tolerance, graceful degradation |

### Level 2 — Core Infrastructure Components (M2)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/02-core-components/00-dns-proxies.md` | DNS, forward & reverse proxies |
| ✅ | `docs/02-core-components/01-load-balancers.md` | Load balancers, L4 vs L7 |
| ✅ | `docs/02-core-components/02-api-gateway-service-discovery.md` | API gateway, service discovery |
| ✅ | `docs/02-core-components/03-cdn-caching.md` | CDN, caching, distributed caches |
| ✅ | `docs/02-core-components/04-storage-classes.md` | Object/block/file storage |
| ✅ | `docs/02-core-components/05-queues-streams-search.md` | Message queues, event streams, search |
| ✅ | `docs/02-core-components/06-workers-schedulers-notifications.md` | Connection pools, workers, schedulers, cron, notifications |

### Level 3 — Data & Storage (M3)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/03-data-storage/00-rdbms-vs-nosql.md` | RDBMS & NoSQL families; SQL vs NoSQL |
| ✅ | `docs/03-data-storage/01-normalization-indexing.md` | Normalization, denormalization, indexing |
| ✅ | `docs/03-data-storage/02-replication.md` | Replication topologies |
| ✅ | `docs/03-data-storage/03-partitioning-sharding.md` | Partitioning, sharding, consistent hashing, federation |
| ✅ | `docs/03-data-storage/04-cdc-materialized-views.md` | CDC, materialized views, storage tiers, lifecycle |
| ✅ | `docs/03-data-storage/05-id-generation.md` | Multi-tenancy, Snowflake IDs, UUIDs |
| ✅ | `docs/03-data-storage/06-migrations-backups.md` | Migrations, backup, restore, PITR |

### Level 4 — Distributed Systems (M3)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/04-distributed-systems/00-cap-pacelc.md` | CAP, PACELC, partitions, partial failure |
| ✅ | `docs/04-distributed-systems/01-consistency-spectrum.md` | Consistency models & quorums |
| ✅ | `docs/04-distributed-systems/02-consensus.md` | Locks, leases, leader election, Raft, Paxos, BFT |
| ✅ | `docs/04-distributed-systems/03-clocks-gossip.md` | Logical/vector clocks, gossip, anti-entropy, Merkle trees |
| ✅ | `docs/04-distributed-systems/04-distributed-transactions.md` | 2PC, 3PC, Saga, orchestration vs choreography |
| ✅ | `docs/04-distributed-systems/05-delivery-semantics.md` | Idempotency, retries, DLQs, delivery guarantees |
| ✅ | `docs/04-distributed-systems/06-crdts-snapshots.md` | CRDTs, distributed snapshots |

### Level 5 — Architecture & Integration Patterns (M4)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/05-architecture-patterns/00-monolith-modular-microservices.md` | Layered, modular monolith, microservices, SOA, EDA |
| ✅ | `docs/05-architecture-patterns/01-hexagonal-clean-onion-ddd.md` | Hexagonal, clean, onion, DDD |
| ✅ | `docs/05-architecture-patterns/02-cqrs-es-outbox.md` | CQRS, event sourcing, outbox, inbox |
| ✅ | `docs/05-architecture-patterns/03-strangler-sidecar-bff.md` | Strangler, sidecar, ambassador, BFF, API composition/federation |
| ✅ | `docs/05-architecture-patterns/04-resilience-patterns.md` | Bulkhead, circuit breaker, retry, timeout, load shedding |
| ✅ | `docs/05-architecture-patterns/05-cache-strategies.md` | Cache strategies; shared-nothing, actor, pipeline |
| ✅ | `docs/05-architecture-patterns/06-mapreduce-lambda-kappa.md` | MapReduce, Lambda, Kappa |

### Level 6 — Reliability & Resilience (M4)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/06-reliability/00-sli-slo-sla-error-budgets.md` | SLI/SLO/SLA, error budgets |
| ✅ | `docs/06-reliability/01-dr-rto-rpo.md` | DR, RTO, RPO, active-active/passive, failover |
| ✅ | `docs/06-reliability/02-health-overload.md` | Health/readiness/liveness, backpressure, overload |
| ✅ | `docs/06-reliability/03-cascading-failure.md` | Cascading failure, retry storms, thundering herd, split-brain |
| ✅ | `docs/06-reliability/04-chaos-graceful-shutdown.md` | Chaos engineering, fault injection, graceful shutdown, brownouts |

### Level 7 — Security (M4)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/07-security/00-authn-authz.md` | AuthN/AuthZ, sessions, cookies, tokens, API keys |
| ✅ | `docs/07-security/01-oauth-oidc-saml-jwt.md` | OAuth 2.0, OIDC, SAML, JWT |
| ✅ | `docs/07-security/02-rbac-abac-pbac-zero-trust.md` | RBAC/ABAC/PBAC, zero-trust, mTLS |
| ✅ | `docs/07-security/03-encryption-kms-secrets.md` | Encryption, KMS, secrets, certs |
| ✅ | `docs/07-security/04-waf-ddos-secure-api.md` | WAF, DDoS, secure API, tenant isolation |
| ✅ | `docs/07-security/05-audit-privacy-threat-modeling.md` | Audit, privacy, STRIDE threat modeling |
| ✅ | `docs/07-security/06-supply-chain-security.md` | Supply-chain security |

### Level 8 — Observability & Operations (M4)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/08-observability/00-logs-metrics-traces.md` | Logs, metrics, traces, correlation IDs |
| ✅ | `docs/08-observability/01-opentelemetry.md` | OpenTelemetry |
| ✅ | `docs/08-observability/02-golden-signals-red-use.md` | Golden signals, RED, USE, alerting, dashboards |
| ✅ | `docs/08-observability/03-rca-incident-response.md` | RCA, incident response |
| ✅ | `docs/08-observability/04-on-call-runbooks-postmortems.md` | On-call, runbooks, postmortems, capacity monitoring |
| ✅ | `docs/08-observability/05-cost-synthetic-rum-profiling.md` | Cost, synthetic/RUM, profiling, continuous verification |

### Level 9 — Cloud-Native & Platform (M5)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/09-cloud-platform/00-containers-orchestration.md` | VMs, containers, orchestration |
| ✅ | `docs/09-cloud-platform/01-k8s-architecture.md` | Kubernetes architecture |
| ✅ | `docs/09-cloud-platform/02-service-mesh-ingress.md` | Service mesh, ingress |
| ✅ | `docs/09-cloud-platform/03-serverless-faas.md` | Serverless, FaaS |
| ✅ | `docs/09-cloud-platform/04-iac-immutable-gitops.md` | IaC, immutable infra, GitOps |
| ✅ | `docs/09-cloud-platform/05-ci-cd-deployment-feature-flags.md` | CI/CD, deployment strategies, feature flags |
| ✅ | `docs/09-cloud-platform/06-autoscaling.md` | HPA, VPA, cluster autoscaling |
| ✅ | `docs/09-cloud-platform/07-cloud-networking.md` | Cloud networking, VPC, hybrid/multi-cloud, edge |
| ✅ | `docs/09-cloud-platform/08-platform-engineering-idp.md` | Platform engineering, IDP |

### Level 10 — Advanced & Extreme-Scale (M5)
| Status | File | Topic |
|:------:|------|-------|
| ✅ | `docs/10-extreme-scale/00-global-routing-multi-region.md` | Global routing, multi-region writes, cross-region replication |
| ✅ | `docs/10-extreme-scale/01-geo-partitioning-sovereignty.md` | Geo-partitioning, data sovereignty |
| ✅ | `docs/10-extreme-scale/02-edge-compute.md` | Edge caching/compute, millions of connections |
| ✅ | `docs/10-extreme-scale/03-billion-user-pb-eb.md` | Billion-user, PB/EB platforms |
| ✅ | `docs/10-extreme-scale/04-stream-realtime-analytics.md` | Stream/real-time analytics |
| ✅ | `docs/10-extreme-scale/05-large-scale-graph-search.md` | Large-scale graph & search |
| ✅ | `docs/10-extreme-scale/06-ml-feature-stores-serving.md` | Distributed ML, feature stores, model serving |
| ✅ | `docs/10-extreme-scale/07-vector-search-rag.md` | Vector search, RAG |
| ✅ | `docs/10-extreme-scale/08-gpu-batch-scheduling.md` | GPU clusters, batch scheduling |
| ✅ | `docs/10-extreme-scale/09-lakehouse-data-mesh.md` | Data lakes, lakehouses, meshes, recsys/ad systems |
| ✅ | `docs/10-extreme-scale/10-payment-ledger-systems.md` | Payments, ledgers, fraud |
| ✅ | `docs/10-extreme-scale/11-identity-iot-p2p-blockchain.md` | Identity, IoT, digital twins, P2P, blockchain |

## Case studies (M6 & M7)

Each follows [templates/CASE-STUDY-TEMPLATE.md](templates/CASE-STUDY-TEMPLATE.md) with all 30
sections and original Mermaid diagrams.

### Beginner (M6)
| Status | System |
|:------:|--------|
| ✅ | URL shortener |
| ✅ | Paste service |
| ✅ | Rate limiter |
| ✅ | Web crawler |
| ✅ | Notification platform |

### Intermediate (M6)
| Status | System |
|:------:|--------|
| ✅ | Chat application |
| ✅ | Social-media feed |
| ✅ | Photo-sharing platform |
| ✅ | Search autocomplete |
| ✅ | Distributed cache |
| ✅ | Logging platform |

### Advanced (M7)
| Status | System |
|:------:|--------|
| ✅ | Video-streaming platform |
| ✅ | Video-conferencing system |
| ✅ | Search engine |
| ✅ | Cloud file-storage platform |
| ✅ | Message broker |
| ✅ | Metrics platform |
| ✅ | Distributed scheduler |
| ✅ | Ride-hailing platform |
| ✅ | Food-delivery platform |
| ✅ | E-commerce platform |
| ✅ | Inventory-management platform |
| ✅ | Payment gateway |
| ✅ | Digital wallet |
| ✅ | Hotel-booking platform |
| ✅ | Airline-reservation platform |
| ✅ | Online multiplayer game |
| ✅ | Collaborative document editor |
| ✅ | Code-hosting platform |
| ✅ | Continuous integration platform |
| ✅ | API gateway |
| ✅ | Identity & access-management platform |
| ✅ | Real-time analytics platform |
| ✅ | Recommendation engine |

### Extreme (M7)
| Status | System |
|:------:|--------|
| ✅ | Banking ledger |
| ✅ | Stock-trading platform |
| ✅ | Fraud-detection system |
| ✅ | Advertisement platform |
| ✅ | Data lake |
| ✅ | Vector database |
| ✅ | Retrieval-augmented generation platform |
| ✅ | Large-language-model inference platform |
| ✅ | Internet of Things platform |
| ✅ | Feature store / model-serving system |



## Network & AI Operations extension

| Status | Item |
|:------:|------|
| ✅ | `case-studies/network-ai-systems/`: intelligent-syslog-monitoring, device-upgrade-management, configuration-drift-detection, ai-assisted-noc, network-digital-twin, secure-network-agent (6 case studies, 4 diagrams each) |
| ✅ | `templates/network/`: critical-incident-report, device-upgrade-plan, rollback-plan, configuration-change-review, post-upgrade-validation, network-ai-security-review (6 templates) |
| ✅ | `examples/network/`: syslog_parser.py, alert_dedup.py, upgrade_risk.py, config_diff.py (4 runnable tools) |
| ✅ | `docs/` network areas: network-foundations, network-observability, network-automation, network-security, firmware-lifecycle, ai-for-network-operations (6 overview READMEs) |
| ✅ | Remaining practical network tools (11 total, all runnable) (certificate-expiry monitor, end-of-support tracker, NOC summary generator, compliance checker, change-risk worksheet, etc.) |

## AI Systems track

| Status | Item |
|:------:|------|
| ✅ | `docs/ai-systems/` README + AI Milestone 1 chapters: 00-ai-ml-fundamentals, 01-ai-hardware, 02-ai-capacity-planning |
| ✅ | AI Milestone 2 chapters: 03-vector-databases, 04-chunking-ingestion, 05-hybrid-search-reranking, 06-basic-rag |
| ✅ | `templates/ai/`: rag-adr, ai-threat-model, evaluation-plan, prompt-change-review, ai-production-readiness (5 templates) |
| ✅ | `examples/ai/`: token_cost.py, vram.py (2 runnable tools) |
| ✅ | AI Milestone 3 — Advanced RAG: query transformation, adaptive retrieval, GraphRAG, federated retrieval, permission-aware retrieval, grounding and verification |
| ✅ | AI Milestone 4 — Agentic systems: tool calling, workflow state, agent memory, ReAct, planner-executor, multi-agent, human approvals |
| ✅ | AI Milestone 5 — Security and evaluation: prompt injection, data poisoning, RBAC-aware RAG, PII, LLM tracing, RAG/agent evaluation, cost observability |
| ✅ | AI Milestone 6 — Model serving: inference engines, continuous batching, KV caching, quantization, distributed/multi-GPU inference, autoscaling |
| ✅ | AI Milestone 7 — Extreme scale: multi-region serving, billion-chunk retrieval, multi-LoRA, GPU scheduling, enterprise AI gateways, large-scale evaluation, AI governance |
| ✅ | AI Milestone 8 — Case studies and tools: enterprise RAG platform, autonomous support-agent team, LLM API gateway, chunking simulator, model-routing simulator, security and readiness templates |
| ✅ | `simulations/ai/` and `simulations/network/` interactive simulation sets |

## Practical components (M3–M8)
| Status | File | Component |
|:------:|------|-----------|
| ✅ | `calculations/capacity-estimation-worksheet.md` | Capacity-estimation worksheet |
| ✅ | `calculations/availability-calculator.md` | Availability calculator |
| ✅ | `calculations/storage-growth.md` | Storage-growth calculation |
| ✅ | `calculations/latency-budget.md` | Latency-budget template |
| ✅ | `calculations/sharding-calculator.md` | Sharding calculator |
| ✅ | `examples/consistent_hashing.py` | Consistent-hashing simulation |
| ✅ | `examples/rate_limiter.py` | Rate-limiter example |
| ✅ | `examples/queue_retry.py` | Queue & retry simulation |
| ✅ | `examples/failure_injection.py` | Failure-injection example |
| ✅ | `templates/CASE-STUDY-TEMPLATE.md` | Case-study template |
| ✅ | `templates/ADR-TEMPLATE.md` | ADR template |
| ✅ | `templates/design-review-checklist.md` | Design-review checklist |
| ✅ | `templates/security-review-checklist.md` | Security-review checklist |
| ✅ | `templates/reliability-review-checklist.md` | Reliability-review checklist |
| ✅ | `interview-framework/mock-interview.md` | Mock-interview script (M8) |

## Exercises (M8)
✅ Per-level exercise sets under `exercises/<level>/` are complete.

## References index (rolling)
✅ `references/README.md` mirrors SOURCES.md by topic (complete).
