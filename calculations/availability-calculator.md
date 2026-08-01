# Availability Calculator

> Convert an availability target into allowed downtime and cost intuition, and combine
> component availabilities for series and parallel (redundant) paths. Original formulas.

## Nines → allowed downtime per year
| SLO | Uptime | Allowed downtime /year | /month (≈) |
|-----|--------|------------------------|------------|
| 99% (two nines) | 0.99 | 3.65 days | 7.3 h |
| 99.9% (three nines) | 0.999 | 8.76 h | 43.8 min |
| 99.95% | 0.9995 | 4.38 h | 21.9 min |
| 99.99% (four nines) | 0.9999 | 52.6 min | 4.4 min |
| 99.999% (five nines) | 0.99999 | 5.26 min | 26 s |

Allowed downtime per period = `(1 − SLO) × period`.

## Combining components

### Series (any failure fails the path)
If a request traverses components with availabilities `A1, A2, …, An` in series, the path
availability is their product:

`A_path = A1 × A2 × … × An`

A path with three 99.9% components in series: `0.999^3 ≈ 0.997` → ~99.7%, worse than any
single component. **Series degrades availability.**

### Parallel (redundant replicas, independent failure)
For `n` independent replicas each with availability `A`, the system is available unless *all*
are down:

`A_parallel = 1 − (1 − A)^n`

Three replicas at 99% each: `1 − 0.01^3 = 1 − 0.000001 = 0.999999` → ~six nines, *if failures
are truly independent*. **Redundancy improves availability, but only to the extent failures
are uncorrelated.**

### Independence is the catch
Most real outages are correlated (a config push takes down all replicas, a shared dependency
fails). Treat the parallel formula as an *upper bound* and audit for shared failure modes
(shared AZ, shared control plane, shared dependency, shared deploy).

## Error budget
For an SLO `S`, the error budget is `1 − S` of allowed bad events over the window. For a
30-day month at 99.9%: `0.001 × 43200 min = 43.2 min` of allowed downtime. Burn rate alerts
compare actual bad-event rate to budget consumption (see Level 6).
