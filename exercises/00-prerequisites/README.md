# Level 0 — Prerequisites — Exercises

Practice problems keyed to the [00-prerequisites](../../docs/00-prerequisites/README.md) level.

## Estimation & reasoning drills

- 1. Estimate the latency order of L1 cache, RAM, SSD, LAN, WAN. Then design a system assuming the network is as fast as a function call and find where it breaks.
- 2. A server hits EMFILE under 50k connections. Give an immediate fix and a better long-term fix to the I/O model.
- 3. Explain why blocking I/O with one thread per connection does not scale to tens of thousands of connections.

## Design prompts

- 4. Re-derive the four latency tiers from memory and explain the implication for caching and co-locating compute with data.
- 5. Compare TCP vs UDP for live telemetry and justify your choice.

## What would break? / when NOT to use

- 6. Why does REST suit public APIs and gRPC suit internal high-throughput calls? Give one trade-off of each.

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
