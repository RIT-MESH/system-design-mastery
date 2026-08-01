## [Unreleased] — Network & AI Operations + AI Systems extension

### Added — Network & AI Operations
- 6 network-AI case studies under `case-studies/network-ai-systems/` (intelligent syslog
  monitoring with a structured `/report`, device upgrade management, configuration drift
  detection, AI-assisted NOC, network digital twin, secure network agent), each with 4
  original Mermaid diagrams.
- 6 network templates (critical-incident-report, device-upgrade-plan, rollback-plan,
  configuration-change-review, post-upgrade-validation, network-ai-security-review).
- 4 runnable network tools in `examples/network/` (syslog_parser, alert_dedup,
  upgrade_risk, config_diff).
- 6 network-area overview READMEs under `docs/` (network-foundations, network-observability,
  network-automation, network-security, firmware-lifecycle, ai-for-network-operations).

### Added — AI Systems track (Milestones 1–2)
- `docs/ai-systems/` track README + 7 chapters: AI/ML fundamentals, AI hardware, AI
  capacity planning, vector databases, chunking and ingestion, hybrid search and
  reranking, basic RAG.
- 5 AI templates (rag-adr, ai-threat-model, evaluation-plan, prompt-change-review,
  ai-production-readiness) and 2 runnable AI tools (token_cost, vram).

### Status
- The original curriculum (Levels 0–10, 44 case studies) remains complete. The Network
  & AI Operations extension is complete. The AI Systems track has Milestones 1–2
  complete; Milestones 3–8 (advanced RAG, agentic systems, security/evaluation,
  model serving, extreme scale, case studies/tools) are planned in `BACKLOG.md`.

## [Unreleased] — Milestone 8 progress (project complete)

### Added
- Per-level exercise sets under `exercises/<NN>-<area>/README.md` for Levels 0–10
  (estimation/reasoning drills, design prompts, "what would break" questions).
- `interview-framework/mock-interview.md` — a timed, role-playable mock interview with
  clock checkpoints, a problem bank by tier, a rubric, and red flags.
- `references/README.md` — a topic-grouped index mirroring SOURCES.md stable IDs.
- CI hardening: `.github/workflows/spell-check.yml` (codespell, advisory) with a
  `.codespellignore` for domain terms, and `.github/workflows/cross-link-check.yml`
  (verifies internal markdown links resolve). Markdown lint, link check, and Mermaid
  validation workflows were already present (M1).

### Status
- **The project is feature-complete.** All 11 curriculum levels (76 chapters), all 44
  case studies (40+ required), all practical components (calculations + 4 Python
  simulations + templates), the interview framework, exercises, references, and the
  full CI validation suite (markdown lint, link check, Mermaid validate, spell check,
  cross-link integrity) are in place. Internal-link integrity verified locally: 470
  links, 0 broken.

## [Unreleased] — Milestone 7 progress

### Added — Advanced case studies (complete)
- message-broker, metrics-platform, distributed-scheduler, ride-hailing, food-delivery,
  e-commerce-platform, inventory-management, payment-gateway, digital-wallet,
  hotel-booking, airline-reservation, multiplayer-game, collaborative-document-editor,
  code-hosting, ci-platform, api-gateway-system, iam-platform, real-time-analytics,
  recommendation-engine, search-engine, cloud-file-storage, video-conferencing (all 30
  sections + original Mermaid context diagram each).

### Added — Extreme case studies (complete)
- banking-ledger, stock-trading, fraud-detection, advertisement-platform, data-lake,
  vector-database, rag-platform, iot-platform, feature-store-model-serving (all 30
  sections + original Mermaid context diagram each). (LLM inference was added in M5.)

### Status
- **All 44 case studies (40+ required) are complete** across beginner (5), intermediate
  (6), advanced (23), and extreme (10) tiers. Updated `BACKLOG.md` (135 done / 4 pending).
  Remaining: per-level exercises, interview-framework mock script, references index (M8).

## [Unreleased] — Milestone 6 progress

### Added — Beginner case studies (complete)
- `case-studies/beginner/paste-service.md`, `rate-limiter.md`, `web-crawler.md`,
  `notification-platform.md` — all 30 sections, original Mermaid, plus a context `.mmd` each
  under `diagrams/case-studies/<name>/`.

### Added — Intermediate case studies (complete)
- `case-studies/intermediate/chat-application.md`, `social-media-feed.md`,
  `photo-sharing-platform.md`, `search-autocomplete.md`, `logging-platform.md` — all 30
  sections, original Mermaid, plus a context `.mmd` each.

### Status
- All beginner (5) and intermediate (6) case studies are complete. Updated `BACKLOG.md`
  (92 done / 47 pending). Remaining case studies are the advanced and extreme tiers.

## [Unreleased] — Milestone 5 progress

### Added
- Completed Level 9 (Cloud-Native & Platform Design): containers/orchestration, Kubernetes
  architecture, service mesh/ingress, serverless/FaaS, IaC/immutable/GitOps, CI/CD/
  deployment strategies/feature flags, autoscaling (HPA/VPA/cluster), cloud networking/
  VPC/hybrid/multi-cloud/edge, platform engineering/IDP. Level 9 is now complete.
- Completed Level 10 (Advanced & Extreme-Scale): global routing/multi-region writes/
  cross-region replication, geo-partitioning/data sovereignty, edge compute/millions of
  connections, billion-user & PB/EB platforms, high-frequency event/stream/real-time
  analytics, large-scale graph & search, distributed ML/feature stores/model serving,
  vector search & RAG, GPU clusters & batch scheduling, data lakes/lakehouses/data mesh,
  payment/ledger/fraud, identity/IoT/digital twins/P2P/blockchain. **All 11 curriculum
  levels (0–10) are now complete.**
- Added the first extreme case study: `case-studies/extreme/llm-inference.md` (all 30
  sections) plus four original Mermaid diagrams under `diagrams/case-studies/llm-inference/`.
- Updated `BACKLOG.md` (83 done / 56 pending) and the Level 9/10 README indexes.

### Milestone
- Curriculum (Levels 0–10) is fully authored. Remaining work is case studies, exercises,
  interview deep-dive, and CI hardening (Milestones 6–8).

## [Unreleased] — Milestone 4 progress

### Added
- Completed Level 5 (Architecture & Integration Patterns): monolith/modular/microservices/SOA/EDA,
  hexagonal/clean/onion/DDD, CQRS/ES/outbox/inbox, strangler/sidecar/BFF/composition/federation,
  resilience patterns (bulkhead/circuit-breaker/retry/timeout/load-shedding), cache strategies +
  shared-nothing/actor/pipeline, MapReduce/Lambda/Kappa. Level 5 is now complete.
- Completed Level 6 (Reliability & Resilience): SLI/SLO/SLA/error budgets, DR/RTO/RPO/failover,
  health/readiness/liveness/overload, cascading failure/retry storms/thundering herd/split-brain,
  chaos engineering/graceful shutdown/brownouts. Level 6 is now complete.
- Completed Level 7 (Security): authN/authZ/sessions/tokens/API keys, OAuth2/OIDC/SAML/JWT,
  RBAC/ABAC/PBAC/zero-trust/mTLS, encryption/KMS/secrets/certs, WAF/DDoS/secure API/tenant
  isolation, audit/privacy/STRIDE, supply-chain security. Level 7 is now complete.
- Completed Level 8 (Observability & Operations): logs/metrics/traces/correlation IDs,
  OpenTelemetry, golden signals/RED/USE/alerting/dashboards, RCA/incident response,
  on-call/runbooks/postmortems/capacity monitoring, cost/synthetic/RUM/profiling/continuous
  verification. Level 8 is now complete.
- Added the first advanced case study: `case-studies/advanced/video-streaming.md` (all 30
  sections) plus four original Mermaid diagrams under `diagrams/case-studies/video-streaming/`.
- Updated `BACKLOG.md` (61 done / 78 pending) and the Level 5–8 README indexes.

## [Unreleased] — Milestone 3 progress

### Added
- Completed Level 3 (Data & Storage): `00-rdbms-vs-nosql.md`, `01-normalization-indexing.md`,
  `02-replication.md`, `03-partitioning-sharding.md`, `04-cdc-materialized-views.md`,
  `05-id-generation.md`, `06-migrations-backups.md`. Level 3 is now complete.
- Completed Level 4 (Distributed Systems): `00-cap-pacelc.md`, `01-consistency-spectrum.md`,
  `02-consensus.md`, `03-clocks-gossip.md`, `04-distributed-transactions.md`,
  `05-delivery-semantics.md`, `06-crdts-snapshots.md`. Level 4 is now complete.
- Added the first intermediate case study: `case-studies/intermediate/distributed-cache.md`
  (all 30 sections) plus four original Mermaid diagrams under
  `diagrams/case-studies/distributed-cache/`.
- Updated `BACKLOG.md` and the Level 3/4 README indexes to reflect completed chapters.


## [Unreleased] — Milestone 2 progress

### Added
- Completed Level 0 (Prerequisites): `02-os-linux.md`, `03-complexity-data-structures.md`,
  `05-db-basics.md`. Level 0 is now complete.
- Completed Level 1 (Foundations): `02-scalability.md`, `03-redundancy-fault-tolerance.md`.
  Level 1 is now complete.
- Completed Level 2 (Core Infrastructure Components): `00-dns-proxies.md`,
  `01-load-balancers.md`, `02-api-gateway-service-discovery.md`, `03-cdn-caching.md`,
  `04-storage-classes.md`, `05-queues-streams-search.md`,
  `06-workers-schedulers-notifications.md`. Level 2 is now complete.
- Added calculations: `storage-growth.md`, `latency-budget.md`, `sharding-calculator.md`.
- Added `examples/failure_injection.py` (circuit breaker + timeout simulation).
- Added the first full beginner case study: `case-studies/beginner/url-shortener.md` (all
  30 sections) plus four original Mermaid diagrams under
  `diagrams/case-studies/url-shortener/`.
- Updated `BACKLOG.md` and the Level 0/1/2 README indexes to reflect completed chapters.

### Tooling
- A portable Python 3.13.14 embeddable interpreter was added under `work/python-embed/` (not
  part of the repo content) to run and verify the educational simulations. All four example
  scripts were executed successfully.
# Changelog

All notable changes to this repository are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to its
original-content policy described in [CONTRIBUTING.md](CONTRIBUTING.md).

## [Unreleased]

### Added — Milestone 1: Repository foundation
- Repository scaffold and full directory structure (`docs/`, `case-studies/`, `diagrams/`,
  `exercises/`, `interview-framework/`, `calculations/`, `templates/`, `examples/`,
  `references/`, `.github/`).
- Root documentation: `README.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `LICENSE`, `ACKNOWLEDGEMENTS.md`, `SOURCES.md`, `GLOSSARY.md`, `CONTENT-MAP.md`,
  `BACKLOG.md`, and this `CHANGELOG.md`.
- Research report at `work/RESEARCH-REPORT.md` covering topic comparison, gaps, licenses,
  original curriculum, source/citation policy, diagram originality policy, contribution
  policy, and milestone plan.
- Curriculum content map (`CONTENT-MAP.md`) and per-level README indexes for Levels 0–10.
- Initial foundational chapters:
  - `docs/00-prerequisites/00-computing-fundamentals.md`
  - `docs/00-prerequisites/01-networking-http.md`
  - `docs/01-foundations/00-requirements-and-quality-attributes.md`
  - `docs/01-foundations/01-capacity-planning.md`
- Original Mermaid diagrams for the foundational chapters, stored under `diagrams/foundations/`.
- Templates: case study, architecture decision record (ADR), interview framework, design
  review checklist, security review checklist, reliability review checklist.
- GitHub issue templates (`new-chapter`, `new-case-study`, `content-review`) and a pull request
  template.
- GitHub Actions validation workflows: markdown lint, link check, Mermaid validation.
- Backlog enumerating all remaining chapters and case studies with per-item status.

### Notes
- No content was copied from the studied reference repositories; all prose, examples,
  capacity estimates, and diagrams are original to this repository.







