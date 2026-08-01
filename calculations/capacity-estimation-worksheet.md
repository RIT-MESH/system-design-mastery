# Capacity Estimation Worksheet

> A reusable template for back-of-envelope capacity estimation. Fill in the shaded
> placeholders. This is a worksheet, not a guarantee — round generously and state every
> assumption.

## 1. Usage profile
| Variable | Symbol | Value (your system) |
|----------|:------:|---------------------|
| Active users | `U` | |
| Daily-active fraction | `DAU_frac` | |
| Actions per DAU per day | `A` | |
| Read fraction of actions | `r` | e.g., 0.95 |
| Peak : average multiplier | `P` | e.g., 10 |

## 2. Requests per second
- Daily actions = `U × DAU_frac × A` = ____ /day
- Daily reads = `Daily actions × r` = ____ /day
- Daily writes = `Daily actions × (1 − r)` = ____ /day
- Avg reads/s = `Daily reads / 86400` ≈ ____
- Avg writes/s = `Daily writes / 86400` ≈ ____
- Peak reads/s = `Avg × P` ≈ ____
- Peak writes/s = `Avg × P` ≈ ____
- Read:write ratio ≈ `r : (1 − r)` = ____

## 3. Storage
| Variable | Value |
|----------|-------|
| Average object size | |
| Metadata per object | |
| New objects/day | (= daily writes) |
| New data/day | `objects/day × (size + metadata)` |
| Retention (days) | |
| Total stored | `new data/day × retention` |
| Index overhead (% of data) | |
| Storage with indexes | |

## 4. Bandwidth
- Write bandwidth = `avg writes/s × object size` ≈ ____
- Read bandwidth = `avg reads/s × object size` ≈ ____
- Peak read bandwidth = `peak reads/s × object size` ≈ ____
- Egress dominates: note cloud egress cost implications.

## 5. Binding resource & compute (rough)
- Binding resource: compute / storage / bandwidth / IOPS? → ____
- If a node handles ~N ops/s of the binding kind, machines needed ≈ `peak / N × (1/(1−buffer))`
- Buffer target: ____

## 6. Headroom & growth
- 12-month growth factor: ____
- Projected peak next year: ____
- Machines/storage next year with buffer: ____

## 7. Notes
Record the dominant cost driver and the single assumption most likely to be wrong.
