# Provenance and Originality Review

This document records the research and originality review process for the `system-design-mastery` repository.

## Scope

The repository was reviewed against three stated reference repositories:

- `donnemartin/system-design-primer`
- `DovAmir/awesome-design-patterns`
- `Sairyss/system-design-patterns`

A fourth repository, `ByteByteGoHq/system-design-101`, was also studied during planning.

## Review methods

1. **Targeted exact-phrase scan:** Searched for distinctive canonical phrases from the reference repositories. No matches were found for phrases including:
   - "Latency is the time to perform some action"
   - "Throughput is the number of such actions"
   - "Everything is a trade-off"
   - "If you have a performance problem"
   - "In a distributed computer system, you can only support two"
   - "An API gateway is a software component"
   - "Vertical scaling means scaling by adding more power"
   - "Horizontal scaling means scaling by adding more servers"

2. **Internal duplicate detection:** Scanned all 232 Mermaid `.mmd` source files and 324 inline Mermaid blocks for exact duplicates. No exact duplicate Mermaid blocks were found within the repository.

3. **License verification:** Checked each reference repository for a license file.
   - `donnemartin/system-design-primer`: Creative Commons Attribution 4.0 International (CC BY 4.0) — confirmed.
   - `DovAmir/awesome-design-patterns`: No license file confirmed — treated as reference-only, all rights reserved by default.
   - `Sairyss/system-design-patterns`: No license file confirmed — treated as reference-only, all rights reserved by default.
   - `ByteByteGoHq/system-design-101`: No license file confirmed — treated as reference-only, all rights reserved by default.

4. **Structural similarity assessment:** The curriculum covers topics in an order common to system-design curricula generally (scalability, availability, DNS, CDN, caching, queues, databases, replication, partitioning, consistency, case studies). This overlap is inherent to the subject matter, not evidence of copying. Mitigations: the repository uses a level-based progression, independent examples and capacity assumptions, primary-source citations in each chapter, and original diagrams drawn from chapter requirements.

## Overall assessment

- **Direct verbatim-copy risk:** Low (no matches in targeted phrase scan).
- **Diagram-copy risk:** Low from exact internal duplication checks. External visual similarity was not exhaustively measurable. Before commercial publication, manually review high-risk diagrams for visual similarity to reference figures.
- **Structural/derivative risk:** Moderate (inherent topic overlap, mitigated by independent structure, examples, and citations).
- **Attribution and license risk:** Corrected in this revision (see [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)).

## Recommendations before commercial publication

1. Run a broader external similarity service (e.g., a commercial plagiarism database).
2. Perform pixel-level or visual comparison against external diagrams for high-risk areas: CDN/cache flows, load-balancer architecture, database replication, sharding/consistent hashing, URL shortener, social feed, chat system, API gateway, RAG and agent workflows.
3. Preserve research notes and drafts showing independent development.
4. Maintain an overlap-review checklist in pull requests (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## Limitations

This is a technical similarity and attribution review, not a legal opinion. It included repository-wide local scans, targeted exact-phrase comparison, internal duplicate detection, and license-file checks. It did not include a commercial plagiarism database, full semantic comparison of every paragraph against the entire public web, or pixel-level comparison against every external diagram.
