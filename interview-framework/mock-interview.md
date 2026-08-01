# Mock System-Design Interview Script

> A timed, role-playable mock interview for two people (interviewer + candidate) or
> self-practice. It operationalizes the [interview framework](README.md) into concrete
> prompts, clock checkpoints, and a rubric.

## Format
- 45 minutes. Interviewer drives time; candidate talks/thinks aloud.
- Interviewer uses the prompts below to steer and to probe depth; do not solve for the
  candidate.

## Timeline & checkpoints

### 0–5 min — Clarify & scope
- Interviewer reads the problem, then asks: "Restate the problem in your own words."
- Probes: "Who are the users?", "What is the single most important metric?", "Must-have vs
  nice-to-have for v1?", "Read/write ratio?"
- **Checkpoint**: a one-line problem statement + scoped feature list agreed.

### 5–10 min — Estimate
- Prompt: "Estimate RPS, storage, and bandwidth. State your assumptions out loud."
- Probes: "What is the binding resource?", "Peak multiplier?", "Metadata/index size?"
- **Checkpoint**: 3-line capacity estimate + named binding constraint.

### 10–22 min — High-level design
- Prompt: "Draw the data flow end-to-end and name each component's single responsibility."
- Probes: "Why this storage? Name a rejected alternative.", "Where is the state?", "What is
  the read path vs write path?"
- **Checkpoint**: context/component diagram + storage choices with reasons.

### 22–37 min — Deep dive
- Prompt: "Pick the hardest part and design it deeply."
- Probes: "Data model + indexes?", "Partition key + hot-key handling?", "Replication +
  failover?", "Consistency model for users?", "Failure modes + graceful degradation?",
  "Idempotency on writes?"
- **Checkpoint**: a request-sequence diagram + a failure-flow discussion.

### 37–43 min — Validate & trade-offs
- Prompt: "State your SLO and 2–3 trade-offs with what you sacrificed."
- Probes: "Give an alternative design and why you rejected it.", "What breaks first at 10x?"
- **Checkpoint**: a trade-off table + an alternative.

### 43–45 min — Wrap-up
- Candidate summarizes in 30 s and names the next hardening step. Interviewer gives one
  piece of strong critique.

## A starter bank of problems (by tier)
- Beginner: URL shortener, paste service, rate limiter.
- Intermediate: distributed cache, chat application, social-media feed, search autocomplete.
- Advanced: message broker, ride-hailing, e-commerce checkout, payment gateway, hotel booking.
- Extreme: banking ledger, stock-trading matching, fraud detection, LLM inference, RAG platform.

Pick the problem matching the candidate's level; the same script applies.

## Rubric (score 1–5 each)
| Dimension | What good looks like |
|-----------|----------------------|
| Clarifying | restates, scopes, surfaces ambiguity, asks high-value questions |
| Estimation | right-order numbers, names binding resource, states assumptions |
| Architecture | clean components with single responsibilities, justified storage |
| Depth | designs the hard part: partitioning, replication, consistency, failures |
| Trade-offs | names what was sacrificed; offers an alternative; honest about limits |
| Communication | structured, talks aloud, uses the board, manages time |

## Red flags to catch
- Drawing boxes before clarifying scope.
- Naming a vendor product as the architecture.
- Skipping failure modes.
- Claiming "eventual consistency is fine" without naming the bound.
- Optimizing a path the requirements never said was hot.

## Anti-patterns for the interviewer
- Don't solve for the candidate; steer with questions.
- Don't let them spend 25 min on the high-level diagram at the expense of depth.
- Don't grade on the final diagram; grade on the structured thinking.

## Self-practice mode
Time yourself against the checkpoints. For each checkpoint, write the deliverable; if you
can't produce it in the window, that is the skill to drill. Re-read the matching case study
afterward and compare your trade-offs.
