# Network-AI Security Review

> Review for any network-AI feature before production.

## Data
- [ ] Secrets/PII redacted from logs, configs, prompts, and RAG corpora
- [ ] Access control (RBAC) on incidents, configs, runbooks, audit
- [ ] Log integrity (tamper-evident, append-only)

## AI safety gateway
- [ ] Never expose device passwords / private keys
- [ ] Never auto-execute high-risk or destructive changes
- [ ] Never disable firewalls / modify routing / VPN without approval
- [ ] Never upgrade outside maintenance windows
- [ ] Never return configs to unauthorized users
- [ ] Never send confidential configs/logs to unapproved external models

## Agentic controls
- [ ] Tool risk tiers defined; high-risk routed to approval
- [ ] Policy gateway fail-closed on failure
- [ ] Full audit (actor/action/time/result)
- [ ] Air-gapped / local-model option for confidential data

## Operations
- [ ] Human approval for firmware/routing/firewall/VPN/reboots/config-deploy/security-policy
- [ ] AI used only for summarize/classify/retrieve/correlate/explain/recommend/report
