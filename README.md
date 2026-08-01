# System Design Mastery

**A graded, original curriculum for learning system design — from absolute prerequisites to extreme-scale architecture.**

System Design Mastery is a self-contained, vendor-neutral reference and learning path that teaches how to design distributed systems in depth. It is organized as eleven progressive levels (Level 0 through Level 10), from the computing and networking fundamentals a beginner needs before "system design" means anything concrete, through distributed-systems theory, reliability, security, and observability, up to the patterns and constraints that only appear at billion-user, petabyte, and globally-distributed scale. The repository was independently drafted and is reviewed using exact-match, similarity, attribution, and diagram-duplication checks. Confirmed overlap is rewritten or attributed. Standard algorithms, protocol names, architecture patterns, and common technical terminology are not claimed as proprietary. See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) for license status and [PROVENANCE.md](PROVENANCE.md) for the review process.

The repository is deliberately a curriculum rather than a list of interview answers. Each chapter is independently navigable and follows a consistent structure — learning objectives, examples, trade-offs, a "common mistakes" section, failure modes, review questions, and further reading with citations — so a reader can open any chapter and learn the topic in context. The conceptual material is reinforced by practical components: capacity-estimation and availability worksheets, small Python simulations of real mechanisms (consistent hashing, token-bucket rate limiting, retry with jitter, and a circuit-breaker/failure-injection model), reusable templates (case study, architecture decision record, and design/security/reliability review checklists), and an interview framework with a timed mock-interview script. Sixty-six case studies apply the method end to end, each written to a fixed thirty-section template.

**Current status:** Complete. It contains 97 curriculum chapters (76 across Levels 0–10, 15 in the AI Systems track, and 6 in the Network Operations area), 66 case studies (each with the full 30-section content and four original Mermaid diagrams), 19 runnable Python tools, 16 templates, and a full CI validation suite. The [Network & AI Operations](#network-and-ai-operations) track and the [AI Systems](#ai-systems-track) track (15 chapters covering all 8 AI milestones) are complete. Original Mermaid diagrams are used throughout (284 standalone `.mmd` sources plus 327 inline diagram blocks).

**Purpose:** to give a beginner, a working engineer, and a senior architect a single coherent path that builds genuine design judgment — the ability to gather requirements, estimate, choose components, reason about consistency and failure, and justify trade-offs — rather than memorized answers to a fixed set of interview questions.

The author is [RIT-MESH](https://github.com/RIT-MESH). The repository is public on GitHub at <https://github.com/RIT-MESH/system-design-mastery>.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Goals and Learning Outcomes](#goals-and-learning-outcomes)
3. [Intended Audience](#intended-audience)
4. [Prerequisites](#prerequisites)
5. [Repository Structure](#repository-structure)
6. [Curriculum: Levels 0–10](#curriculum-levels-0-10)
7. [Case Studies](#case-studies)
8. [Practical Components](#practical-components)
9. [Diagrams and Documentation Format](#diagrams-and-documentation-format)
10. [The Design Method Used in This Repository](#the-design-method-used-in-this-repository)
11. [Recurring Design Principles](#recurring-design-principles)
12. [How to Use This Repository](#how-to-use-this-repository)
13. [Progress and Project Status](#progress-and-project-status)
14. [Planned Work](#planned-work)
15. [Contribution Guidelines](#contribution-guidelines)
16. [Documentation Standards](#documentation-standards)
17. [References and Sources](#references-and-sources)
18. [Author](#author)
19. [License](#license)

## Project Overview

System Design Mastery exists because most public system-design material falls into one of two camps: a broad index of links with little prose, or a strong set of interview answers whose wording and diagrams come from elsewhere. This repository fills the gap between them with a single graded curriculum that is failure-first, original, and vendor-neutral.

What makes it different from a collection of notes or interview answers:

- **A graded progression.** Eleven levels move the reader from "how a computer runs a program" and the HTTP/TLS fundamentals, through capacity planning, storage, distributed-systems theory, architecture patterns, reliability, security, and observability, to extreme-scale concerns such as multi-region writes, GPU scheduling, lakehouses, and retrieval-augmented generation. Each level assumes the previous one.
- **Failure-first teaching.** Every pattern chapter includes a "when NOT to use this" section, common mistakes, and failure modes, because the cost of a pattern is as important as its benefit.
- **Original content.** Explanations, examples, capacity estimates, and diagrams are independently written. The four public repositories that were studied while planning this one are acknowledged in [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md) as reference-only; none of their wording, structure, examples, or diagrams were copied.
- **A consistent case-study format.** Forty-four case studies each follow the same thirty-section template (problem, scope, requirements, assumptions, traffic/storage/bandwidth estimates, API design, data model, architecture, request flow, component responsibilities, database selection, caching, partitioning, replication, consistency, failures, reliability, security, observability, cost, scaling stages, trade-offs, alternatives, interview points, diagrams, further reading, and exercises) so the method is applied uniformly across very different systems.
- **Citations, not assertions.** Factual and technical claims cite primary sources through stable identifiers (for example `S-RFC8446` for TLS 1.3) defined in [`SOURCES.md`](SOURCES.md), preferring RFCs, academic papers, and official documentation.

The repository combines conceptual learning, practical design, interview preparation, and real-world architecture. The chapters build the concepts; the practical components and exercises build the skills; the case studies apply the method to real system shapes; and the interview framework turns the whole thing into a repeatable process under time pressure.

## Goals and Learning Outcomes

After working through the curriculum and a representative set of case studies, a learner should be able to:

- **Gather requirements and constraints.** Separate functional from non-functional requirements, translate vague quality words ("fast", "reliable") into measurable SLIs and SLOs, and state assumptions explicitly rather than hiding them.
- **Estimate.** Compute back-of-envelope requests-per-second, storage, and bandwidth from a usage scenario, identify the binding resource (compute, storage, bandwidth, or IOPS), and size headroom for peak and failure.
- **Design APIs and data models.** Choose REST, RPC, or gRPC with reasons; pick serialization (JSON, Protocol Buffers, Avro) for the workload; and model entities, indexes, and access paths.
- **Select components.** Choose among the storage families (relational, key-value, document, column-family, graph, time-series, search, vector) and the infrastructure components (load balancers, caches, queues, streams, CDNs) based on access pattern, not fashion.
- **Find bottlenecks and single points of failure.** Walk the data path and ask "what happens if this dies?" for every component, then eliminate single points of failure with redundancy and tested failover.
- **Reason about scalability and availability.** Decide when to scale vertically versus horizontally, push state out of services to unlock horizontal scaling, and quantify availability in "nines" with error budgets.
- **Evaluate consistency and latency trade-offs.** Use CAP and PACELC to reason about consistency, availability, and latency; choose the weakest consistency model users can tolerate; and set read/write quorums deliberately.
- **Design caching, messaging, replication, and partitioning.** Pick a cache strategy and invalidation model, prevent cache stampedes, choose leader-follower versus leaderless replication, and shard by a key that balances load without hot keys.
- **Plan observability, security, disaster recovery, and failure handling.** Instrument logs, metrics, and traces; model threats with STRIDE; define RTO and RPO; and design graceful degradation and chaos tests.
- **Explain decisions.** Justify each architectural choice, state what was sacrificed, and offer at least one alternative design and why it was rejected — the skill that interviews and real design reviews both measure.

## Intended Audience

- **Complete beginners** who need the Level 0 prerequisites before distributed systems mean anything.
- **Backend developers** who want to understand the systems their code runs on and move toward architecture.
- **Infrastructure, cloud, and network engineers** who design the platforms other teams build on.
- **DevOps and SRE engineers** who operate distributed systems and need to reason about reliability, overload, and recovery.
- **Platform engineers** building internal developer platforms and golden paths.
- **Software architects, staff, and principal engineers** working at scale where the patterns of Levels 9 and 10 dominate.
- **System-design interview candidates** who want understanding rather than memorized answers, and who can use the interview framework and mock-interview script to practice.

A beginner can start at Level 0; an experienced engineer can jump to the level matching their gaps. No single reader is expected to read all 76 chapters linearly.

## Prerequisites

Level 0 is itself the prerequisite track, so the repository assumes very little: basic programming comfort and a willingness to read technical prose. Helpful (but not required) prior exposure includes: how an operating system runs a program, the request/response nature of HTTP, what a database table is, and big-O notation. Readers who already know these can skim [Level 0](docs/00-prerequisites/) and begin at [Level 1 — Foundations](docs/01-foundations/). The curriculum is self-contained: every later concept is defined when introduced and cross-references the glossary in [`GLOSSARY.md`](GLOSSARY.md).

## Repository Structure

```text
system-design-mastery/
├── README.md, ROADMAP.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE
├── ACKNOWLEDGEMENTS.md, SOURCES.md, GLOSSARY.md, CONTENT-MAP.md
├── BACKLOG.md, CHANGELOG.md, .markdownlint.json, .codespellignore, .gitignore
├── docs/                 # 11 levels (00-10), 76 chapters
│   ├── 00-prerequisites/ … 10-extreme-scale/
├── case-studies/         # beginner · intermediate · advanced · extreme (44 studies)
├── diagrams/             # original Mermaid sources (foundations/, patterns/, case-studies/)
├── exercises/            # one exercise set per level (11 sets)
├── interview-framework/  # the method + a timed mock-interview script
├── calculations/         # capacity/availability/storage/latency/sharding worksheets
├── templates/            # case-study, ADR, and design/security/reliability checklists
├── examples/             # 4 Python simulations (standard library only)
├── references/           # topic-grouped index mirroring SOURCES.md
└── .github/              # issue templates, PR template, and CI workflows
```

Top-level documents at a glance:

- [`ROADMAP.md`](ROADMAP.md) — milestone-based plan and status.
- [`CONTENT-MAP.md`](CONTENT-MAP.md) — canonical file inventory and navigation contract.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — originality requirements, citation policy, and chapter/case-study checklists.
- [`SOURCES.md`](SOURCES.md) — stable-ID citations for every factual claim.
- [`GLOSSARY.md`](GLOSSARY.md) — shared terminology used consistently across chapters.
- [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md) — the studied reference repositories, marked reference-only.
- [`BACKLOG.md`](BACKLOG.md) and [`CHANGELOG.md`](CHANGELOG.md) — what is done and what changed.

## Curriculum (Levels 0-10)

The curriculum is eleven directories under [`docs/`](docs/), one per level. Every chapter is independently readable and ends with previous/next navigation. All 76 chapters share the same structure: learning objectives, examples, trade-offs, common mistakes, failure modes, review questions, and further reading with SOURCES.md citations. All 76 chapters contain trade-offs, common-mistakes, failure-mode, and review-question sections; 327 inline Mermaid diagrams and 284 standalone `.mmd` sources support them.

### Level 0 — Prerequisites (`docs/00-prerequisites/`)

The fundamentals required before "system design" means anything concrete.

- [Computing Fundamentals](docs/00-prerequisites/00-computing-fundamentals.md) — processes/threads, CPU/memory/disk/network latency tiers
- [Networking & HTTP](docs/00-prerequisites/01-networking-http.md) — DNS, TCP/UDP, TLS, REST, RPC/gRPC, JSON/Protobuf/Avro
- [Operating-System & Linux Fundamentals](docs/00-prerequisites/02-os-linux.md) — virtual memory, file descriptors, signals, I/O models
- [Complexity & Basic Data Structures](docs/00-prerequisites/03-complexity-data-structures.md) — big-O, hash maps, trees, heaps, Bloom filters
- [Basic Database Concepts](docs/00-prerequisites/05-db-basics.md) — tables, keys, indexes, ACID, SQL vs NoSQL first pass

### Level 1 — System Design Foundations (`docs/01-foundations/`)

The vocabulary and estimating skills that make later levels intelligible.

- [Requirements & Quality Attributes](docs/01-foundations/00-requirements-and-quality-attributes.md) — functional vs non-functional, availability/durability/scale
- [Capacity Planning](docs/01-foundations/01-capacity-planning.md) — RPS, storage, bandwidth, read-heavy vs write-heavy, headroom
- [Scalability: Stateless vs Stateful](docs/01-foundations/02-scalability.md) — vertical vs horizontal, externalizing state
- [Redundancy, Fault Tolerance & Graceful Degradation](docs/01-foundations/03-redundancy-fault-tolerance.md) — SPOFs, replication factors, degradation

### Level 2 — Core Infrastructure Components (`docs/02-core-components/`)

The building-block services most production architectures compose.

- [DNS, Forward & Reverse Proxies](docs/02-core-components/00-dns-proxies.md)
- [Load Balancers: Layer 4 vs Layer 7](docs/02-core-components/01-load-balancers.md)
- [API Gateway & Service Discovery](docs/02-core-components/02-api-gateway-service-discovery.md)
- [CDN & Caching](docs/02-core-components/03-cdn-caching.md)
- [Storage Classes: Object, Block, File](docs/02-core-components/04-storage-classes.md)
- [Message Queues, Event Streams & Search Engines](docs/02-core-components/05-queues-streams-search.md)
- [Workers, Schedulers, Cron & Notifications](docs/02-core-components/06-workers-schedulers-notifications.md)

### Level 3 — Data and Storage Architecture (`docs/03-data-storage/`)

Choosing, structuring, distributing, and operating data stores.

- [RDBMS and the NoSQL Families](docs/03-data-storage/00-rdbms-vs-nosql.md)
- [Normalization, Denormalization & Indexing](docs/03-data-storage/01-normalization-indexing.md)
- [Replication Topologies](docs/03-data-storage/02-replication.md)
- [Partitioning, Sharding & Consistent Hashing](docs/03-data-storage/03-partitioning-sharding.md)
- [CDC, Materialized Views & Data Lifecycle](docs/03-data-storage/04-cdc-materialized-views.md)
- [ID Generation & Multi-tenancy](docs/03-data-storage/05-id-generation.md)
- [Database Migrations, Backup & Point-in-Time Recovery](docs/03-data-storage/06-migrations-backups.md)

### Level 4 — Distributed Systems (`docs/04-distributed-systems/`)

What changes when a system spans machines that fail independently over an unreliable network.

- [CAP, PACELC, Partitions & Partial Failure](docs/04-distributed-systems/00-cap-pacelc.md)
- [The Consistency Spectrum & Quorums](docs/04-distributed-systems/01-consistency-spectrum.md)
- [Consensus: Locks, Leases, Leader Election, Raft, Paxos, BFT](docs/04-distributed-systems/02-consensus.md)
- [Clocks, Gossip & Anti-entropy](docs/04-distributed-systems/03-clocks-gossip.md)
- [Distributed Transactions: 2PC, 3PC, Saga](docs/04-distributed-systems/04-distributed-transactions.md)
- [Delivery Semantics: Idempotency, Retries, DLQs](docs/04-distributed-systems/05-delivery-semantics.md)
- [CRDTs & Distributed Snapshots](docs/04-distributed-systems/06-crdts-snapshots.md)

### Level 5 — Architecture and Integration Patterns (`docs/05-architecture-patterns/`)

How services are organized, communicate, and protect themselves — each with a "when not to use it" note.

- [Monolith, Modular Monolith, Microservices, SOA, Event-Driven](docs/05-architecture-patterns/00-monolith-modular-microservices.md)
- [Hexagonal, Clean, Onion Architecture & DDD](docs/05-architecture-patterns/01-hexagonal-clean-onion-ddd.md)
- [CQRS, Event Sourcing, Outbox, Inbox](docs/05-architecture-patterns/02-cqrs-es-outbox.md)
- [Strangler, Sidecar, Ambassador, BFF, API Composition & Federation](docs/05-architecture-patterns/03-strangler-sidecar-bff.md)
- [Resilience Patterns: Bulkhead, Circuit Breaker, Retry, Timeout, Load Shedding](docs/05-architecture-patterns/04-resilience-patterns.md)
- [Cache Strategies, Shared-Nothing, Actor, Pipeline](docs/05-architecture-patterns/05-cache-strategies.md)
- [MapReduce, Lambda & Kappa](docs/05-architecture-patterns/06-mapreduce-lambda-kappa.md)

### Level 6 — Reliability and Resilience (`docs/06-reliability/`)

Keeping systems dependable under failure and overload, with measurable objectives.

- [SLI, SLO, SLA & Error Budgets](docs/06-reliability/00-sli-slo-sla-error-budgets.md)
- [Disaster Recovery, RTO/RPO, Active-Active/Passive, Failover](docs/06-reliability/01-dr-rto-rpo.md)
- [Health, Readiness, Liveness, Backpressure, Overload Protection](docs/06-reliability/02-health-overload.md)
- [Cascading Failure, Retry Storms, Thundering Herd, Split-brain](docs/06-reliability/03-cascading-failure.md)
- [Chaos Engineering, Fault Injection, Graceful Shutdown, Brownouts](docs/06-reliability/04-chaos-graceful-shutdown.md)

### Level 7 — Security Architecture (`docs/07-security/`)

Protecting identity, data, and supply chain across the architecture.

- [Authentication, Authorization, Sessions, Cookies, Tokens, API Keys](docs/07-security/00-authn-authz.md)
- [OAuth 2.0, OpenID Connect, SAML, JWT](docs/07-security/01-oauth-oidc-saml-jwt.md)
- [RBAC, ABAC, PBAC, Zero-Trust, mTLS](docs/07-security/02-rbac-abac-pbac-zero-trust.md)
- [Encryption in Transit & at Rest, KMS, Secrets, Certificates](docs/07-security/03-encryption-kms-secrets.md)
- [WAF, DDoS Protection, Secure API Design, Tenant Isolation](docs/07-security/04-waf-ddos-secure-api.md)
- [Audit Logs, Data Masking, Privacy-by-Design, Threat Modeling (STRIDE)](docs/07-security/05-audit-privacy-threat-modeling.md)
- [Supply-Chain Security](docs/07-security/06-supply-chain-security.md)

### Level 8 — Observability and Operations (`docs/08-observability/`)

Knowing what the system is doing, why it broke, and how to run it on-call.

- [Logs, Metrics, Traces, Correlation IDs](docs/08-observability/00-logs-metrics-traces.md)
- [OpenTelemetry](docs/08-observability/01-opentelemetry.md)
- [Golden Signals, RED, USE, Alerting & Dashboards](docs/08-observability/02-golden-signals-red-use.md)
- [Root-Cause Analysis & Incident Response](docs/08-observability/03-rca-incident-response.md)
- [On-Call, Runbooks, Postmortems, Capacity Monitoring](docs/08-observability/04-on-call-runbooks-postmortems.md)
- [Cost Observability, Synthetic/RUM, Profiling, Continuous Verification](docs/08-observability/05-cost-synthetic-rum-profiling.md)

### Level 9 — Cloud-Native and Platform Design (`docs/09-cloud-platform/`)

How modern systems are packaged, scheduled, deployed, and operated on cloud platforms.

- [VMs, Containers & Container Orchestration](docs/09-cloud-platform/00-containers-orchestration.md)
- [Kubernetes Architecture](docs/09-cloud-platform/01-k8s-architecture.md)
- [Service Mesh & Ingress](docs/09-cloud-platform/02-service-mesh-ingress.md)
- [Serverless & Functions as a Service](docs/09-cloud-platform/03-serverless-faas.md)
- [IaC, Immutable Infrastructure & GitOps](docs/09-cloud-platform/04-iac-immutable-gitops.md)
- [CI/CD, Deployment Strategies & Feature Flags](docs/09-cloud-platform/05-ci-cd-deployment-feature-flags.md)
- [Autoscaling: HPA, VPA, Cluster Autoscaling](docs/09-cloud-platform/06-autoscaling.md)
- [Cloud Networking, VPC, Hybrid/Multi-Cloud & Edge](docs/09-cloud-platform/07-cloud-networking.md)
- [Platform Engineering & Internal Developer Platforms](docs/09-cloud-platform/08-platform-engineering-idp.md)

### Level 10 — Advanced and Extreme-Scale Systems (`docs/10-extreme-scale/`)

Patterns and constraints that only matter past millions of users, petabytes, or globally distributed writes.

- [Global Routing, Multi-Region Writes & Cross-Region Replication](docs/10-extreme-scale/00-global-routing-multi-region.md)
- [Geo-Partitioning & Data Sovereignty](docs/10-extreme-scale/01-geo-partitioning-sovereignty.md)
- [Edge Compute & Millions of Concurrent Connections](docs/10-extreme-scale/02-edge-compute.md)
- [Billion-User Systems & Petabyte/Exabyte Platforms](docs/10-extreme-scale/03-billion-user-pb-eb.md)
- [High-Frequency Event Processing, Stream & Real-Time Analytics](docs/10-extreme-scale/04-stream-realtime-analytics.md)
- [Large-Scale Graph Processing & Search](docs/10-extreme-scale/05-large-scale-graph-search.md)
- [Distributed ML, Feature Stores & Model Serving](docs/10-extreme-scale/06-ml-feature-stores-serving.md)
- [Vector Search & Retrieval-Augmented Generation (RAG)](docs/10-extreme-scale/07-vector-search-rag.md)
- [GPU Clusters & Batch Scheduling](docs/10-extreme-scale/08-gpu-batch-scheduling.md)
- [Data Lakes, Lakehouses & Data Mesh](docs/10-extreme-scale/09-lakehouse-data-mesh.md)
- [Payment Systems, Financial Ledgers & Fraud Detection](docs/10-extreme-scale/10-payment-ledger-systems.md)
- [Internet-Scale Identity, IoT/Digital Twins, P2P & Blockchain](docs/10-extreme-scale/11-identity-iot-p2p-blockchain.md)
## Case Studies

Sixty-six case studies apply the design method end to end. Each follows the [case study template](templates/CASE-STUDY-TEMPLATE.md) and contains original traffic/storage/bandwidth estimates, an API design, a data model, and four original Mermaid diagrams — a high-level architecture (context/component) diagram, a request-sequence diagram, a failure-flow diagram, and a scaling-evolution diagram — plus a request-flow description, failure-scenarios description, scaling stages, trade-offs, alternatives, interview discussion points, and exercises. Standalone diagram sources live under [`diagrams/case-studies/`](diagrams/case-studies/).

### Beginner ([`case-studies/beginner/`](case-studies/beginner/))

| Case study | Problem in brief | Status |
|------------|------------------|:------:|
| [URL Shortener](case-studies/beginner/url-shortener.md) | Shorten long URLs; resolve short codes at scale (read-heavy, edge-cached) | Complete |
| [Paste Service](case-studies/beginner/paste-service.md) | Store and serve text pastes via short URLs (read-heavy, long-tail) | Complete |
| [Rate Limiter](case-studies/beginner/rate-limiter.md) | Per-client token-bucket limiting at the edge | Complete |
| [Web Crawler](case-studies/beginner/web-crawler.md) | Distributed crawl with per-host politeness and dedup | Complete |
| [Notification Platform](case-studies/beginner/notification-platform.md) | Multi-channel fan-out with retry, DLQ, and dedup | Complete |

### Intermediate ([`case-studies/intermediate/`](case-studies/intermediate/))

| Case study | Problem in brief | Status |
|------------|------------------|:------:|
| [Distributed Cache](case-studies/intermediate/distributed-cache.md) | Sharded, replicated in-memory cache with hot-key handling | Complete |
| [Chat Application](case-studies/intermediate/chat-application.md) | Real-time messaging, presence, connection-scale gateways | Complete |
| [Social-Media Feed](case-studies/intermediate/social-media-feed.md) | Hybrid fan-out (on-write + celebrity pull-on-read) | Complete |
| [Photo-Sharing Platform](case-studies/intermediate/photo-sharing-platform.md) | Object storage + CDN; egress-dominated | Complete |
| [Search Autocomplete](case-studies/intermediate/search-autocomplete.md) | Per-keystroke latency with an in-memory prefix index | Complete |
| [Logging Platform](case-studies/intermediate/logging-platform.md) | High-rate ingest, hot index + cold tier, date-partitioned | Complete |

### Advanced ([`case-studies/advanced/`](case-studies/advanced/))

Message broker, metrics platform, distributed scheduler, ride-hailing, food-delivery, e-commerce, inventory-management, payment gateway, digital wallet, hotel-booking, airline-reservation, multiplayer game, collaborative document editor, code-hosting, continuous integration, API gateway, identity & access management, real-time analytics, recommendation engine, search engine, cloud file-storage, video-conferencing, and video-streaming — 23 studies, all complete. Each is linked from its file in [`case-studies/advanced/`](case-studies/advanced/).

### Extreme ([`case-studies/extreme/`](case-studies/extreme/))

Banking ledger, stock-trading, fraud detection, advertisement platform, data lake, vector database, retrieval-augmented generation platform, Internet of Things platform, feature store / model-serving, and large-language-model inference — 10 studies, all complete. Each is linked from its file in [`case-studies/extreme/`](case-studies/extreme/).

## Practical Components

**Calculation worksheets** ([`calculations/`](calculations/)) — reusable, original templates:

- [Capacity-estimation worksheet](calculations/capacity-estimation-worksheet.md) — RPS, storage, bandwidth, binding resource
- [Availability calculator](calculations/availability-calculator.md) — nines→downtime, series/parallel formulas
- [Storage-growth calculation](calculations/storage-growth.md) — steady-state growth, tiering savings
- [Latency-budget template](calculations/latency-budget.md) — distributing an end-to-end SLO across the call path
- [Sharding calculator](calculations/sharding-calculator.md) — minimum shards, hot-key sanity

**Python simulations** ([`examples/`](examples/)) — standard-library only, runnable with `python3 <file>.py`:

- [`consistent_hashing.py`](examples/consistent_hashing.py) — demonstrates minimal key movement vs naive modulo hashing
- [`rate_limiter.py`](examples/rate_limiter.py) — a token-bucket limiter with burst and refill
- [`queue_retry.py`](examples/queue_retry.py) — exponential backoff with jitter and a dead-letter policy
- [`failure_injection.py`](examples/failure_injection.py) — a circuit breaker and timeout containing a failing dependency

**Templates** ([`templates/`](templates/)):

- [Case-study template](templates/CASE-STUDY-TEMPLATE.md) — the 30-section format every case study follows
- [Architecture decision record (ADR) template](templates/ADR-TEMPLATE.md)
- [Design-review checklist](templates/design-review-checklist.md)
- [Security-review checklist](templates/security-review-checklist.md)
- [Reliability-review checklist](templates/reliability-review-checklist.md)

**Interview framework** ([`interview-framework/`](interview-framework/)):

- [The six-phase method](interview-framework/README.md) — clarify, estimate, high-level, deep-dive, validate, wrap-up
- [Mock-interview script](interview-framework/mock-interview.md) — timed checkpoints, a problem bank by tier, and a rubric

**Exercises** ([`exercises/`](exercises/)) — one set per level (11 sets), each with estimation/reasoning drills, design prompts, and "what would break / when not to use" questions.

**References** ([`references/`](references/README.md)) — a topic-grouped index mirroring the stable IDs in [`SOURCES.md`](SOURCES.md).

## Diagrams and Documentation Format

The documentation is **Markdown** and diagrams are **Mermaid**. There are no committed PNG or SVG image files; diagrams are authored as Mermaid source so they stay in version control, render natively on GitHub, and are easy to revise. Each diagram carries an `%% created-for: system-design-mastery` comment asserting it was drawn for this repository. Two hundred and thirty-two standalone `.mmd` sources live under [`diagrams/`](diagrams/) (`foundations/`, `patterns/`, `case-studies/`, `ai-systems/`), and 324 additional diagrams are embedded inline in the chapters and case studies. Diagram types include context/component, request-sequence, failure-flow, scaling-evolution, state-machine, and replication diagrams. Every case study includes the first four (context/component, request-sequence, failure-flow, scaling-evolution); state-machine, replication, and entity-relationship diagrams appear in the relevant chapters (for example, in [Consensus](docs/04-distributed-systems/02-consensus.md) and [Replication](docs/03-data-storage/02-replication.md)).

Other formats present: Python code examples (the four simulations), Markdown calculation worksheets, and YAML GitHub Actions configuration.

## The Design Method Used in This Repository

The case studies and the interview framework share one method, summarized as six phases (detailed in the [mock-interview script](interview-framework/mock-interview.md)):

1. **Clarify and scope** — restate the problem, separate must-have from nice-to-have, surface the read/write ratio and the single most important metric.
2. **Estimate** — compute RPS, storage, bandwidth; state assumptions out loud; name the binding resource.
3. **High-level design** — draw the data flow end-to-end; give each component a single responsibility; choose storage with a one-line reason.
4. **Deep dive** — take the hardest part (usually the stateful hot path) and design data model, partitioning, replication, consistency, caching, idempotency, and failure modes.
5. **Validate and trade-offs** — state the SLO and error budget; name what was sacrificed; offer an alternative design and why it was rejected.
6. **Wrap-up** — summarize in 30 seconds and name the next hardening step.

Every case study is written to this shape, which is why the thirty sections appear in the same order across all forty-four of them.

## Recurring Design Principles

The curriculum returns to a small set of principles that recur across levels:

- **Design for failure, not just for the happy path.** Enumerate failure scenarios and graceful degradation before the system is needed under stress (Levels 1, 6).
- **Pick the weakest consistency users can tolerate.** Stronger consistency costs latency and availability; do not pay for it where you do not need it (Level 4).
- **The network costs "years."** The latency gap between memory, disk, and network is enormous; caching, batching, and co-locating compute with data are necessities, not optimizations (Level 0, applied throughout).
- **Push state out of services to scale horizontally.** Stateless tiers autoscale; stateful tiers force affinity and replication (Levels 1, 3).
- **Minimize the stateful core.** Most of a system should be stateless; isolate and carefully operate the part that is not (Levels 1, 3, 5).
- **Autoscaling does not fix a bottleneck.** Adding replicas around a saturated dependency just adds waiters to the same queue (Levels 6, 9).
- **Make blast radius small everywhere.** Bulkheads, canaries, feature flags, and sharding so one failure or one bad change is a slice, not the whole (Levels 5, 6, 9, 10).
- **Treat cost and reliability as first-class.** Operate below capacity for headroom, watch unit cost continuously, and bind staleness explicitly (Levels 6, 8, 10).
- **Cite, do not assert.** Use primary sources and stable IDs; separate universal concepts from vendor products (see [Documentation Standards](#documentation-standards)).

## How to Use This Repository

### For self-study

Start at the level matching your current knowledge using the [Curriculum](#curriculum-levels-0-10) section. Read each chapter end-to-end; the trade-offs and "common mistakes" sections are where the judgment lives. Try the review questions before moving on, then reinforce with the matching [exercise set](exercises/) and a case study at or just above your level. Use [`GLOSSARY.md`](GLOSSARY.md) for terms and [`SOURCES.md`](SOURCES.md) to go deeper on any claim.

### For interview preparation

Read the [six-phase method](interview-framework/README.md), then run yourself through the [timed mock-interview script](interview-framework/mock-interview.md) using a problem from the bank at your tier. Practice communicating trade-offs out loud against the clock, and compare your design to the matching case study afterward. The case-study "interview discussion points" sections call out the ambiguities a strong candidate surfaces.

### For working engineers

Use the repository as a design reference and a set of review checklists. Before a design review, run it against the [design-review checklist](templates/design-review-checklist.md), the [security-review checklist](templates/security-review-checklist.md), and the [reliability-review checklist](templates/reliability-review-checklist.md). Jump to the relevant level when evaluating a specific decision (for example, [replication](docs/03-data-storage/02-replication.md) or [resilience patterns](docs/05-architecture-patterns/04-resilience-patterns.md)).

### For contributors

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first — it defines the originality requirements, the citation policy, and the chapter and case-study checklists, and it is required reading before opening a pull request. See [Contribution Guidelines](#contribution-guidelines) below.

## Network and AI Operations

> **Track:** Network & AI Operations (complete). Extends the curriculum with network-focused AI systems, infrastructure automation, log intelligence, and controlled device-management workflows.

### Case studies ([`case-studies/network-ai-systems/`](case-studies/network-ai-systems/))

Six case studies, each with 30 sections and four original Mermaid diagrams:

| Case study | Problem | Status |
|------------|---------|:------:|
| [Intelligent Syslog Monitoring](case-studies/network-ai-systems/intelligent-syslog-monitoring.md) | Multi-vendor syslog ingest, rule+AI severity classification, structured /report, incident reporting | Complete |
| [Device Upgrade Management](case-studies/network-ai-systems/device-upgrade-management.md) | Firmware/software upgrade planning, backup/rollback, HA-pair/cluster-aware execution | Complete |
| [Configuration Drift Detection](case-studies/network-ai-systems/configuration-drift-detection.md) | Baseline comparison, drift classification, risk scoring, ticketing | Complete |
| [AI-Assisted NOC](case-studies/network-ai-systems/ai-assisted-noc.md) | NOC copilot with multi-model routing, runbook RAG, voice agent, ticket creation | Complete |
| [Network Digital Twin](case-studies/network-ai-systems/network-digital-twin.md) | Live topology model, change simulation, impact prediction, pre-change validation | Complete |
| [Secure Network Agent](case-studies/network-ai-systems/secure-network-agent.md) | Tool-calling agent under policy gateway, approval workflow, full audit, RBAC | Complete |

### Templates ([`templates/network/`](templates/network/))

- [Critical incident report](templates/network/critical-incident-report.md)
- [Device upgrade plan](templates/network/device-upgrade-plan.md)
- [Rollback plan](templates/network/rollback-plan.md)
- [Configuration change review](templates/network/configuration-change-review.md)
- [Post-upgrade validation](templates/network/post-upgrade-validation.md)
- [Network-AI security review](templates/network/network-ai-security-review.md)

### Tools ([`examples/network/`](examples/network/))

Four runnable Python tools (standard library only): `syslog_parser.py` (parse + classify severity), `alert_dedup.py` (dedup + correlation simulator), `upgrade_risk.py` (upgrade-risk calculator), `config_diff.py` (configuration-difference checker).

### Design principle

AI should assist network engineers, not bypass operational controls. Use AI for summarization, classification, retrieval, correlation, explanation, recommendation, and report generation. Use deterministic systems and human approval for firmware upgrades, routing changes, firewall changes, VPN changes, device reboots, configuration deployment, security-policy modification, and destructive or irreversible operations.

## AI Systems Track

> **Track:** AI Systems (complete). Fifteen chapters covering modern AI system architecture from fundamentals to extreme scale: LLM applications, RAG, agentic workflows, model serving, evaluation, security, and cost control. Vendor-neutral; vendor products appear only as implementation examples.

### Chapters ([`docs/ai-systems/`](docs/ai-systems/))

| # | Chapter | Topic | Status |
|:-:|---------|-------|:------:|
| 00 | [AI and ML Fundamentals](docs/ai-systems/00-ai-ml-fundamentals.md) | AI/ML/DL/generative, foundation models, LLMs, tokens, embeddings, context windows, inference vs training, sampling, structured output, tool calling, latency metrics | Complete |
| 01 | [AI Hardware](docs/ai-systems/01-ai-hardware.md) | CPU/GPU/TPU, tensor cores, VRAM, PCIe/NVLink, memory- vs compute-bound, quantization (FP16/BF16/INT8/INT4) | Complete |
| 02 | [AI Capacity Planning](docs/ai-systems/02-ai-capacity-planning.md) | Token-based vs request-based planning, GPU capacity, KV cache, TTFT/TPOT, cost | Complete |
| 03 | [Vector Databases](docs/ai-systems/03-vector-databases.md) | Dense/sparse, ANN (HNSW/IVF/PQ), similarity, sharding, re-indexing, multi-tenancy, hybrid | Complete |
| 04 | [Chunking and Ingestion](docs/ai-systems/04-chunking-ingestion.md) | Chunking strategies, embeddings, ingestion pipeline, metadata | Complete |
| 05 | [Hybrid Search and Reranking](docs/ai-systems/05-hybrid-search-reranking.md) | Hybrid (keyword+vector), reranking, metadata filtering | Complete |
| 06 | [Basic RAG](docs/ai-systems/06-basic-rag.md) | Retrieve-then-generate, grounding, citations, evaluation | Complete |
| 07 | [Advanced RAG](docs/ai-systems/07-advanced-rag.md) | Query transformation, adaptive retrieval, GraphRAG, federated, permission-aware, grounding verification | Complete |
| 08 | [Agentic Systems](docs/ai-systems/08-agentic-systems.md) | Tool calling, ReAct, planner-executor, multi-agent, memory, human approvals, policy gateway | Complete |
| 09 | [AI Security](docs/ai-systems/09-ai-security.md) | Prompt injection, data poisoning, RBAC-aware RAG, PII protection, AI safety gateway | Complete |
| 10 | [AI Evaluation](docs/ai-systems/10-ai-evaluation.md) | Retrieval/generation/agent/cost/safety metrics, release gates, rollback triggers, adversarial sets | Complete |
| 11 | [Model Serving](docs/ai-systems/11-model-serving.md) | Continuous batching, KV caching, quantization, distributed/multi-GPU inference, autoscaling | Complete |
| 12 | [AI at Extreme Scale](docs/ai-systems/12-ai-extreme-scale.md) | Multi-region serving, billion-chunk retrieval, multi-LoRA, GPU scheduling, enterprise AI gateways, AI governance | Complete |
| 13 | [LLM Gateways](docs/ai-systems/13-llm-gateway.md) | Unified model API, complexity/cost/latency/capability routing, token-based quotas, failover, content filtering, audit | Complete |
| 14 | [Semantic Caching](docs/ai-systems/14-semantic-caching.md) | Embedding-based cache lookup, similarity thresholds, safety risks (financial, medical, user-specific, time-sensitive) | Complete |

### AI Case Studies ([`case-studies/ai-systems/`](case-studies/ai-systems/))

| Case study | Problem | Status |
|------------|---------|:------:|
| [Enterprise RAG Platform](case-studies/ai-systems/enterprise-rag-platform.md) | Multi-tenant RAG, permission-aware retrieval, per-tenant token budgets, semantic caching, multi-model routing, AI governance | Complete |
| [Autonomous Support-Agent Team](case-studies/ai-systems/autonomous-support-agent-team.md) | Multi-agent ticket handling (triage, research, resolution, review), supervisor coordination, policy gateway, human approval | Complete |
| [LLM API Gateway](case-studies/ai-systems/llm-api-gateway.md) | Unified model API across providers, complexity/cost/latency routing, token budgets, failover, PII redaction, audit | Complete |

### Templates ([`templates/ai/`](templates/ai/))

- [RAG ADR](templates/ai/rag-adr.md) - RAG architecture decision record
- [AI Threat Model](templates/ai/ai-threat-model.md) - STRIDE-for-AI threat model
- [Evaluation Plan](templates/ai/evaluation-plan.md) - AI evaluation gates and metrics
- [Prompt Change Review](templates/ai/prompt-change-review.md) - prompt/version change review
- [AI Production Readiness](templates/ai/ai-production-readiness.md) - pre-production checklist

### Tools ([`examples/ai/`](examples/ai/))

Four runnable Python tools: `token_cost.py` (token-cost calculator), `vram.py` (VRAM calculator), `chunking_simulator.py` (chunk-size/overlap trade-off simulator), `model_routing_simulator.py` (multi-model routing by task type and cost).

### Design principle

AI should assist, not bypass operational controls. Use AI for summarization, classification, retrieval, correlation, explanation, recommendation, and report generation. Use deterministic systems and human approval for firmware upgrades, routing changes, firewall changes, VPN changes, device reboots, configuration deployment, security-policy modification, and destructive or irreversible operations.

## Progress and Project Status

Every status below is derived from the actual repository contents (files that exist and their section coverage), not from the milestone plan.

| Area | Status | Current content | Next step |
|------|--------|-----------------|----------|
| Level 0 — Prerequisites | Complete | 5 chapters, all with trade-offs/mistakes/failures/review questions | — |
| Level 1 — Foundations | Complete | 4 chapters | — |
| Level 2 — Core Components | Complete | 7 chapters | — |
| Level 3 — Data & Storage | Complete | 7 chapters | — |
| Level 4 — Distributed Systems | Complete | 7 chapters | — |
| Level 5 — Architecture Patterns | Complete | 7 chapters | — |
| Level 6 — Reliability | Complete | 5 chapters | — |
| Level 7 — Security | Complete | 7 chapters | — |
| Level 8 — Observability | Complete | 6 chapters | — |
| Level 9 — Cloud-Native | Complete | 9 chapters | — |
| Level 10 — Extreme-Scale | Complete | 12 chapters | — |
| Case studies | Complete | 66 studies (beginner, intermediate, advanced, extreme, network-AI, AI), all 30 sections, 4 diagrams each | — |
| Diagrams | Complete | 284 `.mmd` sources + 327 inline Mermaid blocks; every case study has context, request-sequence, failure-flow, and scaling-evolution | — |
| Per-level index pages | Complete | 11 `docs/<level>/README.md` indexes with correct chapter tables | — |
| Network & AI Operations | Complete | 6 case studies + 6 templates + 11 tools + 6 chapters + simulation READMEs | — |
| AI Systems | Complete | 15 chapters + 3 case studies + 5 templates + 4 tools (all 8 AI milestones) | — |
| Calculation worksheets | Complete | 5 worksheets | — |
| Python simulations | Complete | 4 simulations (runnable, std-lib only) | — |
| Templates | Complete | Case study, ADR, 3 review checklists | — |
| Interview framework | Complete | Method + timed mock-interview script | — |
| Exercises | Complete | 11 per-level sets (prompts; no answer keys) | Add worked solutions |
| References index | Complete | Topic-grouped mirror of SOURCES.md | — |
| CI validation | Complete | markdown-lint, link-check, mermaid-validate, spell-check, cross-link-check | — |
| License | Complete | Dual: MIT (code) + CC BY 4.0 (content) | — |

The targeted scope is complete. Remaining work is enhancement, listed below as planned.

## Planned Work

The items below are **not** present in the repository today and are listed as future enhancements only:

- **Worked exercise solutions.** The 11 exercise sets contain prompts but no answer keys; model answers are a planned addition.
- **More case studies.** Forty-four are complete; additional systems (for example, a configuration service, a feature-flag service, or a multi-region search index) are a natural extension.
- **Rendered diagram exports.** Diagrams are Mermaid source only; optional committed PNG/SVG renderings are not yet added.
- **Multi-language simulations.** The four simulations are Python only; equivalent examples in other languages are not present.
- **Expanded reference list.** [`SOURCES.md`](SOURCES.md) is the authoritative citation list; a downloadable/offline bibliography export is not present.
- **Test fixtures for simulations.** The Python examples run but have no committed automated test harness.

No part of the above is described as complete elsewhere in this README.

## Contribution Guidelines

Formal contribution rules, the originality statement, the citation policy, and the chapter and case-study checklists are defined in [`CONTRIBUTING.md`](CONTRIBUTING.md). The short version:

1. Read existing material before proposing changes, to avoid duplicate topics.
2. All content must be original — do not copy wording, examples, capacity estimates, or diagrams from other sources.
3. Back every non-trivial factual claim with a stable ID from [`SOURCES.md`](SOURCES.md); add new IDs there as needed.
4. Keep explanations vendor-neutral; separate universal concepts from vendor-specific products.
5. Include examples, trade-offs, a "when not to use" note (for patterns), common mistakes, failure modes, review questions, and previous/next navigation in every chapter.
6. Verify internal links, Mermaid syntax, and (for code) that examples run.
7. Open a pull request using [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md), which includes the originality statement. Two reviewers are recommended where feasible (one technical, one editorial).

The community standard is [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Issue templates exist for [new chapters](.github/ISSUE_TEMPLATE/new-chapter.md), [new case studies](.github/ISSUE_TEMPLATE/new-case-study.md), and [content review](.github/ISSUE_TEMPLATE/content-review.md).

## Documentation Standards

Standards the existing content follows and new content should maintain:

- **State assumptions explicitly** and tag them as constraints versus assumptions.
- **Cite reliable primary sources** (RFCs, papers, official documentation) via SOURCES.md stable IDs; avoid vendor marketing.
- **Include trade-offs and a "when not to use" section** for any pattern or choice.
- **Distinguish universal concepts from vendor products**; do not present one architecture as universally correct.
- **Use consistent terminology** from [`GLOSSARY.md`](GLOSSARY.md).
- **Verify diagrams and internal links**; diagrams must be original Mermaid with the origin comment.
- **Include failure scenarios and operational concerns**, not just the happy path.
- **Avoid unsupported performance claims**; round capacity estimates generously and show the arithmetic.

## References and Sources

The authoritative citation list is [`SOURCES.md`](SOURCES.md), where each source has a stable ID (for example `S-RFC8446` for TLS 1.3, `S-RAFT` for the Raft paper, `S-CHASH` for consistent hashing). Chapters cite these IDs in their "Further reading" sections. A topic-grouped browsing index is in [`references/README.md`](references/README.md). Sources include RFCs and standards (HTTP, TLS, OAuth 2.0, JWT, OIDC, SAML, DNS, QUIC), distributed-systems theory (CAP, PACELC, Raft, Paxos, BFT, Lamport/vector clocks, CRDTs, Dynamo), database and storage references (Spanner, Bigtable, consistent hashing, PostgreSQL, Kafka, Redis, Snowflake IDs), cloud-native references (Kubernetes, OpenTelemetry, Istio, GitOps, Google SRE, chaos principles), architecture and resilience patterns, analytics and ML/LLM references (MapReduce, Lambda, vector databases, RAG), and security references (STRIDE, OWASP API). The four public system-design repositories studied while planning this project are acknowledged in [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md) as reference-only; no content was copied from them.

## Author

GitHub: <https://github.com/RIT-MESH>

This repository was authored as an original system-design curriculum. No biographical claims beyond the GitHub profile are made here.

## License

This repository is dual-licensed, as stated in the [`LICENSE`](LICENSE) file:

- **Code** — the Python simulations, calculation worksheets, Mermaid sources, and GitHub Actions configuration — is licensed under the **MIT License**.
- **Content** — the prose documentation, explanations, examples, and diagrams — is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Reuse therefore requires attribution under CC BY 4.0 for the content and the MIT notice for the code. See the [`LICENSE`](LICENSE) file for the full text.

---

*System Design Mastery — an original, graded curriculum from prerequisites to extreme scale. Authored by [RIT-MESH](https://github.com/RIT-MESH).*

<!-- BEGIN GENERATED REPOSITORY STATS -->
| Metric | Value |
|--------|-------|
| Total files | 510 |
| Markdown files | 209 |
| Python files | 15 |
| Standalone .mmd files | 272 |
| Inline Mermaid blocks | 376 |
| Case-study directories | 6 |
| Case-study Markdown files | 60 |
| Median case-study word count | 843 |
| Min case-study word count | 725 |
| Max case-study word count | 2397 |
| Complete case studies | 60 |
| Draft case studies | 0 |
<!-- END GENERATED REPOSITORY STATS -->
