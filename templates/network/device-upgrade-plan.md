# Device Upgrade Plan (Network-AI)

> Template for a network-device firmware/software upgrade. Requires approval before execution.

## Scope
- **Plan ID:** 
- **Devices / groups:** 
- **Maintenance window (UTC):** start / end
- **Approver(s):** 

## Pre-checks
- **Current firmware / config version:** 
- **Approved target version:** 
- **Release notes:** 
- **Security advisories / known issues:** 
- **Compatibility:** 
- **Configuration risk analysis:** 
- **HA / cluster awareness:** one-at-a-time | rolling | parallel
- **Dependencies:** 

## Backups
- **Config backup location:** 
- **Config checksum:** 
- **Rollback path:** (link to rollback-plan)

## Execution steps
1. Pre-upgrade health checks
2. Backup config + checksum
3. Execute upgrade
4. Monitor reboot / service recovery
5. Post-upgrade validation
6. On failure: rollback (see rollback-plan)

## Result
- **Outcome:** success | rolled-back | partial
- **Report link:** 
