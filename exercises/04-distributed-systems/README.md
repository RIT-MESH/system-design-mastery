# Level 4 — Distributed Systems — Exercises

Practice problems keyed to the [04-distributed-systems](../../docs/04-distributed-systems/README.md) level.

## Estimation & reasoning drills

- 1. Restate 'pick two' CAP correctly using PACELC, and give a PA/EL and a PC/EC example.
- 2. A read-your-writes path is broken by load-balancing reads to lagging replicas. Fix it three ways.
- 3. Compute the quorum condition R+W>N and explain why it gives a read the latest write.

## Design prompts

- 4. Design a lease + fencing token to prevent a paused old leader from writing after a new leader takes over.
- 5. Compare 2PC and a saga for a cross-service order flow; when is each right?

## What would break? / when NOT to use

- 6. A consumer isn't idempotent and redelivery doubles a charge. Show the idempotency-key + outbox fix.

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
