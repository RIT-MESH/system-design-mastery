# Network Simulations

Each subdirectory corresponds to a simulation topic. The runnable Python tools are in [`examples/network/`](../../examples/network/).

| Subdirectory | Tool | Description |
|--------------|------|-------------|
| `syslog-correlation/` | [`alert_dedup.py`](../../examples/network/alert_dedup.py) | Alert deduplication and correlation simulator |
| `alert-deduplication/` | [`alert_dedup.py`](../../examples/network/alert_dedup.py) | Duplicate suppression within time windows |
| `upgrade-risk-scoring/` | [`upgrade_risk.py`](../../examples/network/upgrade_risk.py) | Upgrade-risk calculator (0-100 safety score) |
| `topology-impact-analysis/` | [Network Digital Twin case study](../../case-studies/network-ai-systems/network-digital-twin.md) | Change simulation and impact prediction |
| `configuration-drift/` | [`config_diff.py`](../../examples/network/config_diff.py) | Configuration-difference checker and drift classification |
