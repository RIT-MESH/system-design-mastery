# Level 2 — Core Infrastructure Components — Exercises

Practice problems keyed to the [02-core-components](../../docs/02-core-components/README.md) level.

## Estimation & reasoning drills

- 1. Choose L4 vs L7 for (a) a TCP database proxy and (b) routing /api/* vs /web/*. Justify.
- 2. Design a CDN caching policy for a news site that tolerates 60s staleness but must cut origin egress.
- 3. A viral paste melts the origin. Add three layers of protection (edge, coalescing, stale-while-revalidate).

## Design prompts

- 4. Compare a message queue and an event stream for an audit-log consumer that must replay history.
- 5. Why must worker consumers be idempotent and bounded? Sketch the failure if they aren't.

## What would break? / when NOT to use

- 6. A connection pool is sized per instance; sum across 50 instances exceeds the DB max. What do you do?

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
