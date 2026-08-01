# Level 10 — Advanced & Extreme-Scale — Exercises

Practice problems keyed to the [10-extreme-scale](../../docs/10-extreme-scale/README.md) level.

## Estimation & reasoning drills

- 1. Choose single-writer vs multi-leader vs global-consensus for a multi-region banking ledger.
- 2. A region fails; what RPO does async cross-region replication imply, and how do you reduce it?
- 3. Design a Kappa stream pipeline with effectively-once via checkpoints + idempotent sinks.

## Design prompts

- 4. At billion-user scale, a viral post on one shard melts it. Give the blast-radius-reduction stack.
- 5. GPU cluster: why does gang scheduling matter, and how do you mix latency serving with batch?

## What would break? / when NOT to use

- 6. RAG: tune retrieval depth vs latency/cost, and design a refuse-on-no-context fallback.

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
