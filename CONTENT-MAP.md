# Content Map

This is the canonical file inventory for `system-design-mastery`. Status markers:

- ✅ written · 🔲 stub/planned · 🚧 in progress

A detailed per-chapter and per-case-study status list lives in [BACKLOG.md](BACKLOG.md).
This map focuses on structure and ownership.

## Top-level files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, audience, progression, navigation |
| `ROADMAP.md` | Milestone-based plan and status |
| `CONTRIBUTING.md` | Originality, citation, chapter/case-study checklists, workflow |
| `CODE_OF_CONDUCT.md` | Community standards |
| `LICENSE` | Dual: MIT (code) + CC BY 4.0 (content) |
| `ACKNOWLEDGEMENTS.md` | Studied repositories (reference-only, no copying) |
| `SOURCES.md` | Stable-ID citations for all factual claims |
| `GLOSSARY.md` | Shared terminology |
| `CONTENT-MAP.md` | This file |
| `BACKLOG.md` | Remaining chapters and case studies with status |
| `CHANGELOG.md` | Release history |
| `work/RESEARCH-REPORT.md` | Pre-implementation research and policies |

## Curriculum — `docs/`

| Level | Directory | README | Chapter files (planned) |
|------:|-----------|--------|---------------------------|
| 0 | `00-prerequisites/` | ✅ | computing-fundamentals ✅, networking-http ✅, os-linux, complexity, data-structures-basics, rpc-grpc-serialization, db-basics |
| 1 | `01-foundations/` | ✅ | requirements-and-quality-attributes ✅, capacity-planning ✅, scalability, redundancy-fault-tolerance, stateless-stateful, graceful-degradation |
| 2 | `02-core-components/` | ✅ | dns, proxies, load-balancers, api-gateway, service-discovery, cdn, caching, storage-classes, queues-streams, search, workers-schedulers, notifications |
| 3 | `03-data-storage/` | ✅ | rdbms, nosql-families, indexing, replication, partitioning-sharding, consistent-hashing, cdc-materialized-views, id-generation, migrations, backups-pitr |
| 4 | `04-distributed-systems/` | ✅ | cap-pacelc, consistency-spectrum, quorums, consensus, clocks, gossip-anti-entropy, distributed-transactions, delivery-semantics, crdts, snapshots |
| 5 | `05-architecture-patterns/` | ✅ | monolith-modular, microservices-soa, eda, hexagonal-clean-onion, ddd, cqrs-es-outbox, strangler, sidecar-ambassador-bff, resilience-patterns, cache-strategies, mapreduce-lambda-kappa |
| 6 | `06-reliability/` | ✅ | sli-slo-sla-error-budgets, dr-rto-rpo, active-active-passive, health-readiness-liveness, overload-backpressure, cascading-failure, chaos-engineering, graceful-shutdown-brownouts |
| 7 | `07-security/` | ✅ | authn-authz, tokens-oauth-oidc-saml, rbac-abac-pbac-zero-trust, encryption-kms-secrets, mTLS, waf-ddos, secure-api, audit-privacy, threat-modeling-stride, supply-chain-security |
| 8 | `08-observability/` | ✅ | logs-metrics-traces, opentelemetry, golden-signals-red-use, alerting-dashboards, rca-incident-response, on-call-runbooks-postmortems, cost-observability, profiling-continuous-verification |
| 9 | `09-cloud-platform/` | ✅ | containers-orchestration, k8s-architecture, service-mesh-ingress, serverless-faas, iac-immutable-gitops, ci-cd-deployment-strategies, feature-flags, autoscaling, cloud-networking-vpc, hybrid-multi-cloud-edge, platform-engineering-idp |
| 10 | `10-extreme-scale/` | ✅ | global-routing-multi-region-writes, geo-partitioning-sovereignty, edge-compute, billion-user-systems, pb-eb-platforms, stream-realtime-analytics, large-scale-graph-search, ml-serving-feature-stores, vector-search-rag, gpu-batch-scheduling, lakehouse-data-mesh, payment-ledger-systems, iot-digital-twins-p2p-blockchain |

## Case studies — `case-studies/`

See [BACKLOG.md](BACKLOG.md) for the 40+ list with tier and status. Each follows
[templates/CASE-STUDY-TEMPLATE.md](templates/CASE-STUDY-TEMPLATE.md).

## Operational folders

| Folder | Contents |
|--------|----------|
| `diagrams/foundations` `diagrams/patterns` `diagrams/case-studies` | Original `.mmd` Mermaid sources |
| `exercises/` | Practice problems per level (M8) |
| `interview-framework/` | Repeatable system-design interview method |
| `calculations/` | Capacity, availability, storage-growth, latency-budget, sharding worksheets |
| `templates/` | Case study, ADR, interview framework, design/security/reliability checklists |
| `examples/` | Python simulations (rate limiter, consistent hashing, queues/retries, failure injection) |
| `references/` | Curated primary references index (mirrors SOURCES.md by topic) |
| `.github/ISSUE_TEMPLATE` | `new-chapter`, `new-case-study`, `content-review` |
| `.github/workflows` | `markdown-lint.yml`, `link-check.yml`, `mermaid-validate.yml` |

## Navigation contract

Every chapter and case study must include:
- A top-level learning objective.
- A `## Further reading` section citing SOURCES.md IDs.
- A `## Review questions` section.
- **← Previous** / **Next →** links at the bottom.

## Network & AI Operations extension
| Path | Contents |
|------|----------|
| `case-studies/network-ai-systems/` | 6 network-AI case studies (4 diagrams each) |
| `templates/network/` | 6 network templates |
| `examples/network/` | 4 runnable network tools |
| `docs/network-*`, `docs/firmware-lifecycle`, `docs/ai-for-network-operations` | 6 area overviews |

## AI Systems track
| Path | Contents |
|------|----------|
| `docs/ai-systems/` | README + 7 chapters (AI Milestones 1–2) |
| `templates/ai/` | 5 AI templates |
| `examples/ai/` | 2 runnable AI tools |
| `diagrams/ai-systems/` | AI chapter diagrams |
