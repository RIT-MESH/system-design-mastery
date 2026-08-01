# AI Production Readiness Review

> Checklist before shipping an AI feature to production.

## Correctness
- [ ] Eval gates met (groundedness, hallucination, accuracy)
- [ ] Regression and adversarial sets green
- [ ] Structured output validated; tool-call schemas enforced

## Performance & cost
- [ ] TTFT/TPOT SLO met; tokens/s capacity known
- [ ] Per-tenant token budgets + quotas
- [ ] Cost per request measured and capped
- [ ] Caching (semantic/exact) where safe

## Safety & security
- [ ] Prompt-injection defenses; output validation
- [ ] Permission-aware retrieval; PII/secret redaction
- [ ] Policy gateway: no auto high-risk actions; human approval
- [ ] Full audit (prompts, outputs, tool calls, approvals)
- [ ] AI threat model completed (templates/ai/ai-threat-model.md)

## Ops
- [ ] Observability (tokens/s, TTFT/TPOT, cost, errors, eval drift)
- [ ] Rollback path (model/prompt version)
- [ ] Incident runbook
- [ ] Model/provider failover tested
