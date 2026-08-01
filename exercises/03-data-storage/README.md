# Level 3 — Data & Storage — Exercises

Practice problems keyed to the [03-data-storage](../../docs/03-data-storage/README.md) level.

## Estimation & reasoning drills

- 1. Design the expand/contract steps to add a required NOT NULL column to a huge table.
- 2. Choose W/R for an N=3 store that is read-heavy and write-rare, and explain the trade-off.
- 3. A single hot tenant melts one shard. Give three mitigations (none of which is 'add shards').

## Design prompts

- 4. Compare dual-writes vs CDC for keeping a search index in sync. Why is dual-write unsafe?
- 5. Why are random UUIDs a poor clustered key in a high-write B-tree, and what replaces them?

## What would break? / when NOT to use

- 6. Explain PITR and what RPO it bounds.

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
