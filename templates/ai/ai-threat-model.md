# AI Threat Model (STRIDE-for-AI)

> Threat-model an AI feature before production. Extend STRIDE with AI-specific threats.

## Spoofing
- Prompt injection impersonating system instructions
- Stolen API keys / impersonated users

## Tampering
- Data poisoning of training/RAG corpus
- Tampered embeddings / index

## Repudiation
- Missing audit of prompts, outputs, tool calls, approvals

## Information disclosure
- PII/secret leakage via prompts/outputs
- Cross-tenant retrieval leakage
- Model-weight exfiltration

## Denial of service
- Token-rate exhaustion / long-context cost bombs
- Vector-index overload

## Elevation of privilege
- Agent executing high-risk actions without approval
- Broken RBAC in RAG/agents

## AI-specific controls
- Prompt-injection defenses and output validation
- Permission-aware retrieval
- Policy gateway (no auto high-risk actions)
- Per-tenant token budgets; PII redaction; full audit
