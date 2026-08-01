# Sharding Calculator

> Decide shard count and per-shard load for a write- or read-heavy workload. Original.

## Inputs
| Variable | Symbol | Your value |
|----------|:------:|------------|
| Peak throughput (ops/s) | `T` | |
| Max safe ops/s per shard | `S` | |
| Growth factor (12 months) | `g` | |
| Headroom target | `h` (e.g., 0.3 = 30% spare) | |
| Replication factor (read replicas) | `RF` | |
| Read fraction | `r` | |

## Minimum shards (capacity, writes)
`N_write = ceil(T × (1 − r) / (S × (1 − h)))`

## Minimum shards (reads, with replicas)
`N_read = ceil(T × r / (S × RF × (1 − h)))`

## Choose
`N = max(N_write, N_read)`, rounded up to a comfortable number (e.g., a power of two or a
multiple of nodes) to ease future rebalancing.

## 12-month sizing
`N_next_year = ceil(N × g)`. Pre-provision or plan the reshard path *before* hitting it.

## Hot-key sanity
If a single key drives > `S / N` of traffic, no shard count saves you; mitigate the hot key
(caching, splitting the key, rate limiting) before adding shards.

## Worked mini-example
- T = 20,000 ops/s, r = 0.9 (read-heavy), S = 5,000/shard, RF = 3 read replicas, h = 0.3.
- N_write = ceil(2000 / 3500) = 1; N_read = ceil(18000 / (5000×3×0.7)) = ceil(18000/10500)=2.
- N = 2 shards × 3 read replicas; verify no single key exceeds 5,000/2 = 2,500 ops/s.

## Notes
- Resharding is expensive; over-provision shard count modestly early rather than resharding
  under fire.
- Consistent hashing with vnodes eases rebalancing (see consistent_hashing.py example).
