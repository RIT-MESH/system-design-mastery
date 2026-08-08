# System Design Mastery

> Learn system design from zero to extreme scale — one step at a time.

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-MIT-blue.svg"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/content-CC%20BY%204.0-green.svg"></a>
  <img src="https://img.shields.io/badge/chapters-97-orange">
  <img src="https://img.shields.io/badge/case%20studies-66-purple">
  <img src="https://img.shields.io/badge/diagrams-648-teal">
  <img src="https://img.shields.io/badge/tools-19-yellow">
</p>

---

## What is this?

A free, open-source system design course. Start from nothing. End up designing systems for a billion users.

**No fluff. No copied content. No link dumps.** Just 97 chapters, 66 real-world case studies, and 19 runnable code examples — all original.

## What you will learn

- **Estimate** traffic, storage, and cost before writing code
- **Pick the right database** (SQL vs NoSQL vs vector vs graph)
- **Scale** from 100 users to a billion
- **Prevent data loss** when servers crash
- **Design APIs** people actually want to use
- **Survive interviews** with a repeatable method

## Where to start

| If you are... | Start here |
|------------|-----------|
| New to all this | [Level 0 — Basics](docs/00-prerequisites/) |
| Know some backend | [Level 1 — Foundations](docs/01-foundations/) |
| Preparing for interviews | [Interview Framework](interview-framework/) |
| Into AI/LLM/RAG | [AI Systems Track](docs/ai-systems/) |
| Network engineer | [Network & AI Operations](docs/ai-for-network-operations/) |
| Just want examples | [Case Studies](case-studies/) |

## What's inside?

**📖 97 chapters** across 11 levels:

```
Level 0  →  Basics (CPU, memory, networking, HTTP, Linux)
Level 1  →  Foundations (requirements, capacity, scaling)
Level 2  →  Components (DNS, CDN, load balancers, queues, caches)
Level 3  →  Databases (SQL, NoSQL, indexing, replication, sharding)
Level 4  →  Distributed systems (CAP, consistency, Raft, clocks)
Level 5  →  Architecture (microservices, CQRS, circuit breakers)
Level 6  →  Reliability (SLOs, chaos, failover, disaster recovery)
Level 7  →  Security (OAuth, JWT, zero-trust, encryption, STRIDE)
Level 8  →  Observability (metrics, traces, logs, incident response)
Level 9  →  Cloud-native (Kubernetes, GitOps, CI/CD, autoscaling)
Level 10 →  Extreme scale (multi-region, billion users, GPU scheduling)
```

**📋 66 case studies** — each one walks through a real system design:

| Difficulty | Examples |
|-----------|---------|
| Easy | URL shortener, rate limiter, web crawler |
| Medium | Chat app, social feed, distributed cache |
| Hard | Payment gateway, banking ledger, stock trading |
| Extreme | LLM inference, RAG platform, GPU scheduler |

**🐍 19 Python tools** you can run right now:

```bash
python examples/consistent_hashing.py    # See why sharding works
python examples/rate_limiter.py          # Build a token bucket
python examples/token_cost.py            # Calculate LLM costs
python examples/vram.py                  # Check if a model fits in GPU memory
```

## How case studies work

Every case study follows the same structure so you learn a **repeatable method**:

1. What are we building? → 2. How big is it? → 3. What's the API? → 4. Draw the architecture → 5. Pick the database → 6. How do we shard? → 7. What happens when things break? → 8. How do we scale up?

**30 sections. 4 diagrams. Every time.**

## Contributing

Yes. Read [CONTRIBUTING.md](CONTRIBUTING.md) first — it explains the originality rules and review process.

## License

- **Code** = MIT (do whatever you want)
- **Content** = CC BY 4.0 (use it, just give credit)

See [LICENSE](LICENSE).

## Author

[RIT-MESH](https://github.com/RIT-MESH)

---

⭐ **If this helped you, star the repo.**