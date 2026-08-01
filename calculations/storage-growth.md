# Storage-Growth Calculation

> Estimate how storage grows over time and when tiers must change. Original formulas.

## Inputs
| Variable | Symbol | Your value |
|----------|:------:|------------|
| New data per day (incl. metadata) | `D` | |
| Retention (days) | `R` | |
| Compression ratio | `c` (e.g., 0.5 = halves size) | |
| Replication factor | `RF` | |
| Index/overhead fraction | `i` (e.g., 0.2 = +20%) | |

## Steady-state storage (after retention window fills)
`Steady = D × R × c × RF × (1 + i)`

## Time to reach a budget / tier boundary
Given a capacity cap `C` for a tier:
`Days to fill = (C − Current) / (D × c × RF × (1 + i))`

Alert before this point so you can shard, archive, or buy capacity.

## Tiering savings
If a fraction `f` of data moves from hot (cost `P_hot`/GB-month) to cold (cost `P_cold`/GB-month)
after `t` days, monthly savings =
`(D × f × (R − t)) × (P_hot − P_cold)`

## Worked mini-example (paste service)
- D = 5 GB/day, R = 1826 days (5 y), c = 1.0, RF = 3, i = 0.2
- Steady = 5 × 1826 × 1 × 3 × 1.2 ≈ 32.9 TB (with 3 replicas + 20% overhead)
- Single-replica raw = ~9.1 TB; the 3× + overhead dominates the bill — archive cold pastes.

## Notes
- Include logs/metrics, which often exceed business data.
- Re-estimate on growth changes; treat this as a quarterly cadence.
