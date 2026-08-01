# Post-Upgrade Validation (Network-AI)

> Run after every upgrade; failure triggers the rollback plan.

## Checks
- [ ] Device reachable (management plane)
- [ ] Control plane healthy (routing/neighbors)
- [ ] Data plane healthy (key paths)
- [ ] Services recovered (VPN, DNS, DHCP, etc.)
- [ ] HA/cluster state healthy
- [ ] No new critical syslog events
- [ ] Performance within baseline (CPU, memory, throughput)
- [ ] Config drift vs intended: none

## Result
- **Pass / fail:** 
- **On fail:** execute rollback-plan; link report.
- **Sign-off:** 
