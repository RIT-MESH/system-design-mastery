# System Design Mastery

> **Learn system design from zero to extreme scale — one step at a time.**

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

A free, open-source system design course that takes you from **"what is a thread?"** to **"how do you serve a billion users?"**

No fluff. No copied content. No link dumps. Just **97 chapters**, **66 real-world case studies**, and **19 runnable code examples** — all written from scratch.

## What you will learn

- **Estimate** traffic, storage, and cost before writing a single line of code
- **Pick the right database** — SQL vs NoSQL vs vector vs graph vs time-series
- **Scale** from 100 users to a billion without rewriting everything
- **Prevent data loss** when servers crash, disks fail, and networks partition
- **Design APIs** that are fast, safe, and easy to use
- **Survive system design interviews** with a repeatable 6-phase method
- **Build AI systems** — RAG, agents, LLM serving, vector search, and more
- **Operate reliably** — SLOs, chaos engineering, incident response, on-call

## Where to start

| If you are... | Start here | What you will find |
|---------------|-----------|-------------------|
| 🐤 New to all this | [Level 0 — Basics](docs/00-prerequisites/) | CPU, memory, networking, HTTP, Linux, databases |
| 💻 Backend developer | [Level 1 — Foundations](docs/01-foundations/) | Requirements, capacity planning, scaling |
| 🏗️ Infrastructure engineer | [Level 2 — Components](docs/02-core-components/) | DNS, CDN, load balancers, queues, caches |
| 📊 Data engineer | [Level 3 — Storage](docs/03-data-storage/) | SQL/NoSQL, indexing, replication, sharding |
| 🎯 Interview candidate | [Interview Framework](interview-framework/) | 6-phase method + timed mock-interview script |
| 🤖 AI/ML engineer | [AI Systems Track](docs/ai-systems/) | 15 chapters: RAG, agents, serving, evaluation |
| 🌐 Network engineer | [Network & AI Operations](docs/ai-for-network-operations/) | Syslog, upgrades, drift, NOC copilot, agents |
| 📋 Just want examples | [Case Studies](case-studies/) | 66 designs from URL shortener to LLM inference |

## The curriculum — 11 levels

```
Level 0  →  Basics         CPU, memory, networking, HTTP/TLS, Linux, complexity
Level 1  →  Foundations    Requirements, capacity planning, scaling, redundancy
Level 2  →  Components     DNS, load balancers, CDN, caching, queues, storage
Level 3  →  Databases      SQL/NoSQL, indexing, replication, sharding, CDC, IDs
Level 4  →  Distributed    CAP/PACELC, consistency, Raft, clocks, CRDTs, sagas
Level 5  →  Architecture   Microservices, DDD, CQRS, circuit breakers, MapReduce
Level 6  →  Reliability    SLOs, error budgets, DR, chaos, cascading failure
Level 7  →  Security       OAuth, JWT, zero-trust, encryption, STRIDE, supply chain
Level 8  →  Observability  Logs/metrics/traces, OpenTelemetry, incident response
Level 9  →  Cloud-native   Kubernetes, service mesh, GitOps, CI/CD, autoscaling
Level 10 →  Extreme scale  Multi-region, billion users, GPU scheduling, AI governance
```

**Plus 15 AI Systems chapters** covering: AI fundamentals, hardware, capacity planning, vector databases, chunking, hybrid search, basic RAG, advanced RAG (GraphRAG, permission-aware), agentic systems (ReAct, multi-agent), AI security, evaluation, model serving, LLM gateways, and semantic caching.

## Case studies — 66 real-world designs

| Difficulty | Count | What you will design |
|-----------|------:|---------------------|
| 🟢 Beginner | 5 | URL shortener, paste service, rate limiter, web crawler, notification platform |
| 🔵 Intermediate | 6 | Distributed cache, chat app, social feed, photo sharing, search autocomplete, logging |
| 🟡 Advanced | 23 | Message broker, ride-hailing, e-commerce, payment gateway, multiplayer game, CI platform... |
| 🔴 Extreme | 10 | Banking ledger, stock trading, fraud detection, data lake, vector database, LLM inference... |
| 🤖 AI Systems | 16 | Enterprise RAG, support-agent team, LLM gateway, GraphRAG, code assistant, AI safety gateway... |
| 🌐 Network AI | 6 | Syslog monitoring, upgrade management, drift detection, NOC copilot, digital twin, secure agent |

Every case study follows the same **30-section structure**: problem → scope → requirements → estimates → API → data model → architecture → request flow → database → caching → partitioning → replication → consistency → failures → reliability → security → observability → cost → scaling → trade-offs → alternatives → interview points → diagrams → exercises.

## Try it right now

```bash
# Clone and explore
git clone https://github.com/RIT-MESH/system-design-mastery.git
cd system-design-mastery

# Run any tool — no dependencies needed
python examples/consistent_hashing.py    # See why sharding works
python examples/rate_limiter.py          # Build a token bucket limiter
python examples/token_cost.py            # Calculate LLM inference costs
python examples/vram.py                  # Check if a model fits in GPU memory
python examples/failure_injection.py     # Watch a circuit breaker in action
```

## Practical tools — 19 runnable Python scripts

| Category | Scripts |
|----------|---------|
| Core | `consistent_hashing.py`, `rate_limiter.py`, `queue_retry.py`, `failure_injection.py` |
| Network | `syslog_parser.py`, `alert_dedup.py`, `upgrade_risk.py`, `config_diff.py`, `certificate_expiry_monitor.py`, `end_of_support_tracker.py`, `noc_summary_generator.py`, `compliance_checker.py`, `change_risk_worksheet.py`, `device_health_checklist.py`, `firmware_inventory_scanner.py` |
| AI | `token_cost.py`, `vram.py`, `chunking_simulator.py`, `model_routing_simulator.py` |

All scripts use only the Python standard library — no pip install needed.

## Diagrams — 648 original Mermaid diagrams

Every case study includes **4 diagrams**: architecture (context), request sequence, failure flow, and scaling evolution. Plus diagrams throughout the 97 chapters. All original, all Mermaid, all render natively on GitHub.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. It explains the originality rules, citation policy, and review process. All content must be independently written — no copying from other repositories.

## License

| What | License |
|------|---------|
| Code (Python, Mermaid, Actions) | **MIT** — do whatever you want |
| Content (prose, diagrams, examples) | **CC BY 4.0** — use it, just give credit |

See [LICENSE](LICENSE) for full text.

## Author

**RIT-MESH** — [GitHub](https://github.com/RIT-MESH)

---

⭐ **If this helped you, star the repo so others can find it too.**