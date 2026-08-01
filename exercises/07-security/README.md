# Level 7 — Security — Exercises

Practice problems keyed to the [07-security](../../docs/07-security/README.md) level.

## Estimation & reasoning drills

- 1. A long-lived JWT can't be revoked. Redesign with short access + rotating refresh + denylist.
- 2. Threat-model an upload flow with STRIDE; list a mitigation per category.
- 3. A client supplies tenant_id in the request and reads another tenant's data. Fix it end to end.

## Design prompts

- 4. Explain envelope encryption and why key LOSS is as dangerous as key theft.
- 5. Compare RBAC and ABAC for a system needing row-level access; when do you add PBAC?

## What would break? / when NOT to use

- 6. Design supply-chain controls: pinning, SBOM, signing/provenance, hermetic builds.

> Answers are intentionally open-ended; discuss trade-offs and constraints. See the matching chapters and the [interview framework](../../interview-framework/README.md).
