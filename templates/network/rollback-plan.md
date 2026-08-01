# Rollback Plan (Network-AI)

> Always prepared before an upgrade. Executed automatically on post-upgrade validation failure.

## Trigger
- Validation failure | service not recovered | health-check failure | manual abort

## Rollback steps
1. Stop further rollout (HA/cluster aware).
2. Restore previous config from backup (verify checksum).
3. Revert firmware to previous version (if required and supported).
4. Re-run health checks + validation.
5. Confirm service restored.
6. Record rollback in the upgrade report and audit log.

## Safety
- Never rollback without a verified backup.
- High-risk rollback actions require approval.
- Full audit of who/when/what.
