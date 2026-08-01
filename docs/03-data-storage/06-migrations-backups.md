# Database Migrations, Backup & Point-in-Time Recovery

> **Level:** 3 (Data & Storage) · **Prerequisites:** [ID Generation & Multi-tenancy](05-id-generation.md)
> **Navigation:** [← Previous: ID Generation & Multi-tenancy](05-id-generation.md) · [Next → Level 4: Distributed Systems](../04-distributed-systems/README.md)

## Learning objectives
- Run schema migrations without downtime and without locking the hot path.
- Design backups and point-in-time recovery (PITR) to meet an RPO.
- Reason about restore testing — an untested backup is not a backup.

## Schema migrations
A **migration** changes the database schema. The danger is a migration that locks a hot
table or blocks writes during the deploy. The discipline is **expand/contract**:

1. **Expand**: add the new schema alongside the old (e.g., new nullable column, new table)
   without removing anything. Both old and new code paths work.
2. **Migrate/Backfill**: populate the new structure in the background (online, batched).
3. **Switch**: deploy code that uses the new structure.
4. **Contract**: remove the old structure once nothing uses it.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  E["Expand:<br/>add new - no removal"] --> B["Backfill:<br/>online, batched"]
  B --> S["Switch:<br/>code uses new"]
  S --> C["Contract:<br/>remove old"]
```

Avoid the catastrophic patterns: a migration that rewrites a huge table in one transaction
(hours of lock), or dropping a column while code still reads it. Operations to fear: `ALTER`
that rewrites a table, adding a `NOT NULL` without a default on a huge table, and dropping
columns before code is rolled back-safe.

## Backups and PITR
A **backup** is a restorable copy of data. **Point-in-time recovery (PITR)** combines periodic
full backups with continuous log archiving so you can restore to *any second* up to the
latest archived log. PITR is how you meet a small **RPO** (recovery point objective) — the
maximum data loss you can tolerate.

```mermaid
%% created-for: system-design-mastery
flowchart LR
  Full["Full backup - daily"] --> Logs["Continuous WAL/log archive"]
  Logs --> R["Restore to any t in [full, now]"]
  R --> Validate["Restore test"]
```

- **Full + incremental + logs**: full backups are slow; incrementals capture changes; the
  write-ahead log (WAL) lets you replay to any point.
- **RPO** is bounded by how recent your archived logs are (often seconds to minutes).
- **RTO** (recovery time) is bounded by backup size and restore bandwidth; cross-region
  backups reduce RTO after a region loss.

## Restore testing
**An untested backup is not a backup.** Routinely restore into an isolated environment and
verify you can actually read the data and serve from it. Many "backups" turn out to be
corrupt, incomplete, or unrestorable only when you need them. Automate restore drills (a
chaos practice, Level 6).

## Why this matters
Migrations and backups are how you change and recover a stateful system safely. They are
unglamorous but are the difference between a long-lived data system and one that loses data
on its first deploy or first failure.

## Examples
- Adding a required column: expand (nullable + default), backfill, switch, contract (make
  NOT NULL after backfill).
- A transactional DB: nightly full backup to object storage + continuous WAL archiving →
  RPO of seconds; quarterly restore drills into an isolated cluster.
- A sharded DB: each shard has its own backup/restore; rehearse restoring *one* shard.

## Trade-offs
- **Expand/contract** = safe deploys but more migration steps and temporary dual structure.
- **PITR** = small RPO but storage and log-archiving cost and operational complexity.
- **Restore drills** = confidence but cost compute time; do them regularly but cheaply.

## When NOT to apply
- Don't run a "big bang" migration that locks a hot table; always expand/contract.
- Don't keep backups only in the same region as the source (a region loss takes both).
- Don't rely on replication as your only backup (a destructive `DROP` replicates too).

## Common mistakes
- A migration that locks a large table in production.
- Dropping a column before confirming no code reads it (especially after a rollback).
- Backups that were never restore-tested and turn out corrupt.

## Failure modes and operational concerns
- Long-running migration holding locks → cascading timeouts.
- WAL archiving lag growing → RPO silently worse than expected.
- A destructive query replicated to all replicas (replication is not a backup).

## Review questions
1. Describe the expand/contract steps for adding a required column.
2. How does PITR bound your RPO?
3. Why is replication not a substitute for backups?
4. What makes a backup "untested" and why is that dangerous?
5. Name two migration operations to fear and why.

## Further reading
DR/RTO/RPO in Level 6; chaos/restore drills in Level 6.

---
[← Previous: ID Generation & Multi-tenancy](05-id-generation.md) · [Next → Level 4: Distributed Systems](../04-distributed-systems/README.md)
