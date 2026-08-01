# Level 5 — Architecture Patterns — Exercises

Practice problems keyed to the [05-architecture-patterns](../../docs/05-architecture-patterns/README.md) level.

## Estimation & reasoning drills

- 1. Argue for a modular monolith over microservices for a 10-person team, and name when to extract a service.
- 2. Draw a bounded-context split for orders/billing/shipping and the events between them.
- 3. When is CQRS worth it, and what eventually-consistent story must you tell users?

## Design prompts

- 4. Add bulkhead + circuit breaker + timeout + bounded retry to a slow payment dependency. What does each prevent?
- 5. Choose write-through vs write-behind for a counter; analyze durability vs latency.

## What would break? / when NOT to use

- 6. When is Kappa simpler than Lambda, and what must hold to use it?

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
