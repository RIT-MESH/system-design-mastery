# Roadmap

This roadmap tracks the milestone-based build-out of `system-design-mastery`. Each milestone
defines a coherent, reviewable chunk. Milestones are sequential; later milestones depend on
the concepts and templates delivered in earlier ones.

## Status legend

- ✅ Done — merged and validated by CI.
- 🚧 In progress — actively being written.
- ⏳ Planned — scoped, not yet started.
- 🔲 Stub — placeholder file exists, content pending.

## Milestones

### Milestone 1 — Repository foundation ✅
- Repository scaffold and full directory structure.
- Root docs: README, ROADMAP, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, ACKNOWLEDGEMENTS,
  SOURCES, GLOSSARY, CHANGELOG, CONTENT-MAP, BACKLOG.
- Research report and source/diagram/originality policies.
- Curriculum content map and per-level README indexes.
- Initial foundational chapters (Level 0 and Level 1 starters) with original Mermaid diagrams.
- Templates: case study, ADR, interview framework, design/security/reliability review
  checklists.
- GitHub issue templates, PR template, and validation workflows (markdown lint, link check,
  Mermaid validation).
- Backlog of all remaining chapters and case studies.

### Milestone 2 — Prerequisites, foundations, capacity, core components ⏳
- Complete Level 0 (prerequisites) chapters.
- Complete Level 1 (foundations) chapters including capacity planning.
- Capacity-estimation worksheets and availability calculator in `calculations/`.
- Level 2 (core infrastructure components) chapters.
- Original Mermaid diagrams for the above.

### Milestone 3 — Data, caching, messaging, distributed fundamentals ⏳
- Level 3 (data & storage architecture).
- Caching and messaging deep dives (cross-level chapters).
- Level 4 (distributed systems) fundamentals.
- Sharding calculator, consistent-hashing simulation.

### Milestone 4 — Architecture, reliability, security, observability ⏳
- Level 5 (architecture & integration patterns).
- Level 6 (reliability & resilience).
- Level 7 (security architecture).
- Level 8 (observability & operations).

### Milestone 5 — Cloud-native, multi-region, extreme-scale ⏳
- Level 9 (cloud-native & platform design).
- Level 10 (advanced & extreme-scale systems) concepts.
- Multi-region and global-routing chapters.

### Milestone 6 — Beginner & intermediate case studies ⏳
- All beginner-tier case studies.
- All intermediate-tier case studies.

### Milestone 7 — Advanced & extreme case studies ⏳
- All advanced-tier case studies.
- All extreme-tier case studies.

### Milestone 8 — Exercises, simulations, interview prep, hardening ⏳
- Exercise sets per level.
- Python simulations (rate limiter, queue/retry, failure injection).
- Interview-framework deep dive and mock-interview scripts.
- Hardened CI: spell check, cross-link integrity, Mermaid render checks.

## How to track progress

- Per-chapter status lives in [BACKLOG.md](BACKLOG.md).
- Per-milestone completion is recorded here and in [CHANGELOG.md](CHANGELOG.md).
- Issues are generated from BACKLOG items using the `new-chapter` and `new-case-study`
  issue templates.

## Principles that govern every milestone

1. **Originality first** — no copied wording, structure, examples, or diagrams.
2. **Failure-first** — every pattern includes when NOT to use it and its failure modes.
3. **Vendor-neutral core** — universal concepts separated from vendor implementations.
4. **Navigable** — every chapter has prev/next links and a standalone reading order.
5. **Validated** — markdown lint, link check, and Mermaid validation pass in CI.
