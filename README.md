# System Design Mastery

> A graded, original curriculum for learning system design — from absolute beginner to
> staff/principal extreme-scale architecture. Every explanation, example, capacity
> estimate, and diagram is written from scratch for this repository.

[![Markdown lint](https://img.shields.io/badge/markdown-lint-blue)](.github/workflows/markdown-lint.yml)
[![Link check](https://img.shields.io/badge/links-checked-green)](.github/workflows/link-check.yml)
[![Mermaid](https://img.shields.io/badge/mermaid-validated-teal)](.github/workflows/mermaid-validate.yml)

## Why this repository exists

Most system-design resources fall into two camps: a broad link index with little prose, or
a strong set of interview answers whose wording and diagrams come from elsewhere. This
repository fills the gap with a **single graded curriculum** (Level 0 → Level 10), a
**failure-first** teaching style, **original Mermaid diagrams**, vendor-neutral explanations
separated from vendor-specific implementations, and a consistent **30-section case-study
format** applied to 40+ systems.

## Who it is for

- Complete beginners who need prerequisites before "system design" means anything.
- Backend / infrastructure / cloud / DevOps / SRE engineers building real systems.
- Interview candidates who want understanding, not memorized answers.
- Senior, staff, and principal engineers and architects working at extreme scale.

## Learning progression

| Level | Directory | Focus |
|------:|-----------|-------|
| 0 | `docs/00-prerequisites/` | Computing, OS, complexity, networking, HTTP/TLS, RPC, serialization, Linux, DB basics |
| 1 | `docs/01-foundations/` | Requirements, quality attributes, capacity planning, scaling, redundancy |
| 2 | `docs/02-core-components/` | DNS, proxies, load balancers, API gateways, CDN, caching, queues, search |
| 3 | `docs/03-data-storage/` | RDBMS/NoSQL families, indexing, replication, partitioning, ID generation |
| 4 | `docs/04-distributed-systems/` | CAP/PACELC, consistency, quorums, consensus, clocks, transactions, CRDTs |
| 5 | `docs/05-architecture-patterns/` | Monolith→microservices, DDD, CQRS/ES, strangler, resilience, MapReduce/Lambda/Kappa |
| 6 | `docs/06-reliability/` | SLI/SLO/SLA, error budgets, DR, overload, cascading failure, chaos engineering |
| 7 | `docs/07-security/` | AuthN/Z, OAuth2/OIDC/JWT, zero-trust, encryption, KMS, WAF, threat modeling |
| 8 | `docs/08-observability/` | Logs/metrics/traces, OpenTelemetry, golden signals, incident response |
| 9 | `docs/09-cloud-platform/` | Containers, K8s, service mesh, serverless, IaC, GitOps, autoscaling, IDP |
| 10 | `docs/10-extreme-scale/` | Multi-region writes, billion-user systems, ML/LLM serving, lakehouse, data mesh |

Each level has its own `README.md` index. Every chapter is independently navigable and ends
with **previous/next** links, examples, trade-offs, common mistakes, and review questions.

## Case studies

40+ original designs across four tiers: `case-studies/beginner`, `.../intermediate`,
`.../advanced`, `.../extreme`. Each follows the [case-study template](templates/CASE-STUDY-TEMPLATE.md).
See [BACKLOG.md](BACKLOG.md) for the full list and implementation status.

## Practical components

- Capacity estimation, availability, storage-growth, latency-budget, and sharding calculators
  in `calculations/`.
- Python simulations (consistent hashing, rate limiting, queues/retries, failure injection) in
  `examples/`.
- Templates: case study, ADR, interview framework, design/security/reliability review
  checklists in `templates/`.

## Diagrams

All diagrams are authored in **Mermaid** as source code under `diagrams/` and embedded in
chapters. They are original to this repository — see the [diagram originality policy](../work/RESEARCH-REPORT.md#11-diagram-originality-policy).

## How to use this repo

1. Start at your level using the table above. If prerequisites feel shaky, start at Level 0.
2. Read each chapter end-to-end; the trade-offs and "common mistakes" sections matter most.
3. Try the review questions before moving on.
4. Reinforce with a case study at or just above your level.
5. Use the interview framework when preparing for interviews.

## Repository navigation

```text
system-design-mastery/
├── docs/            # 11 levels of curriculum
├── case-studies/    # beginner · intermediate · advanced · extreme
├── diagrams/        # original Mermaid sources
├── exercises/       # practice problems
├── interview-framework/
├── calculations/    # capacity/availability/sharding worksheets
├── templates/       # case study, ADR, checklists
├── examples/        # Python simulations
├── references/      # curated primary references
└── .github/         # issue templates + validation workflows
```

See [CONTENT-MAP.md](CONTENT-MAP.md) for the full file map and [ROADMAP.md](ROADMAP.md) for the milestone plan.

## Originality and attribution

This repository is original work. It was informed by studying several public system-design
repositories (see [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)) but does **not** copy their
wording, structure, examples, interview answers, or diagrams. Factual claims are cited in
[SOURCES.md](SOURCES.md). The research behind these decisions is in
[`work/RESEARCH-REPORT.md`](../work/RESEARCH-REPORT.md).

## License

Content is licensed under [CC BY 4.0](LICENSE) and code under MIT, both compatible with
attribution. See [CONTRIBUTING.md](CONTRIBUTING.md) for the originality requirements that
apply to every contribution.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md) before opening a pull request. All PRs must pass the
markdown-lint, link-check, and Mermaid-validation workflows.
