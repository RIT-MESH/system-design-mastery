# System Design Interview Framework

> A repeatable, original method for approaching system-design interviews and real design
> sessions. Use it to stay structured under time pressure. It deliberately separates
> *understanding* from *designing* from *validating*.

## Why a framework

In a system-design interview, the goal is not a perfect diagram. It is a structured
conversation that demonstrates you can: clarify ambiguity, scope, estimate, design at the
right level of abstraction, justify trade-offs, and anticipate failure. A framework keeps
you from diving into boxes before you understand the problem.

## The six phases (aim for ~45 min total)

### Phase 1 — Clarify & scope (5–7 min)
- Restate the problem in your own words; confirm the interviewer agrees.
- Ask about users, scale, geography, devices, and the single most important metric.
- Separate must-have from nice-to-have (v1 scope).
- Identify read/write ratio and the dominant access pattern.
- *Deliverable:* a one-line problem statement and a scoped feature list.

### Phase 2 — Estimate (3–5 min)
- Compute RPS, storage, bandwidth. State assumptions out loud.
- Round generously; the goal is the *shape* of the system, not precision.
- Identify the binding resource (compute, storage, bandwidth, IOPS) — it steers the design.
- *Deliverable:* a 3-line capacity estimate and the binding constraint.

### Phase 3 — High-level design (10–12 min)
- Draw the data flow end-to-end (client → edge → services → data).
- Name each component and its single responsibility.
- Choose the storage(s) with a one-line reason each.
- *Deliverable:* a context/component diagram and component responsibilities.

### Phase 4 — Deep dive (12–15 min)
- Pick the hardest part (usually the stateful hot path) and design it deeply.
- Cover the data model, partitioning, replication, consistency, caching, and idempotency.
- Discuss failure modes and graceful degradation explicitly.
- *Deliverable:* a request-sequence diagram and a failure-flow discussion.

### Phase 5 — Validate & trade-offs (5–7 min)
- Walk through your SLI/SLO and error budget assumptions.
- State 2–3 trade-offs and what you sacrificed.
- Offer at least one alternative design and why you rejected it.
- *Deliverable:* a trade-off table and an alternative.

### Phase 6 — Wrap-up (2–3 min)
- Summarize the design in 30 seconds.
- Acknowledge what you would harden next with more time.
- Invite the interviewer's strongest critique.

## Anti-patterns to avoid

- Drawing boxes before clarifying scope.
- Naming a specific vendor product as if it were an architecture.
- Skipping failure modes (interviewers probe here on purpose).
- Optimizing a path the requirements never said was hot.
- Claiming ""eventual consistency is fine"" without naming what ""eventual"" means to users.

## A pocket checklist

- [ ] Problem restated and confirmed
- [ ] Scope agreed (in/out)
- [ ] Read:write ratio stated
- [ ] Binding resource identified
- [ ] Data flow drawn end-to-end
- [ ] Storage(s) chosen with reasons
- [ ] Hardest part designed deeply
- [ ] Failure modes addressed
- [ ] Trade-offs stated with rejections
- [ ] Alternative offered
- [ ] Summary + next hardening

See [templates/design-review-checklist.md](design-review-checklist.md),
[templates/security-review-checklist.md](security-review-checklist.md), and
[templates/reliability-review-checklist.md](reliability-review-checklist.md) for the
detailed review gates.
