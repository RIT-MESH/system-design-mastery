# 🏗️ System Design Mastery

> **From "what is a thread?" to "how do you serve a billion users?" — one graded curriculum.**

<p align="center">
  <a href="https://github.com/RIT-MESH/system-design-mastery/stargazers"><img src="https://img.shields.io/github/stars/RIT-MESH/system-design-mastery?style=social" alt="Stars"></a>
  <a href="https://github.com/RIT-MESH/system-design-mastery/forks"><img src="https://img.shields.io/github/forks/RIT-MESH/system-design-mastery?style=social" alt="Forks"></a>
  <a href="https://github.com/RIT-MESH/system-design-mastery/watchers"><img src="https://img.shields.io/github/watchers/RIT-MESH/system-design-mastery?style=social" alt="Watchers"></a>
  <br>
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-MIT-blue.svg" alt="Code: MIT"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/content-CC%20BY%204.0-green.svg" alt="Content: CC BY 4.0"></a>
  <img src="https://img.shields.io/badge/chapters-97-orange" alt="97 Chapters">
  <img src="https://img.shields.io/badge/case%20studies-66-purple" alt="66 Case Studies">
  <img src="https://img.shields.io/badge/Mermaid%20diagrams-648-teal" alt="648 Diagrams">
  <img src="https://img.shields.io/badge/Python%20tools-19-yellow" alt="19 Tools">
</p>

---

## 🎯 What is this?

A **complete, original, vendor-neutral system design curriculum** that takes you from absolute basics to extreme-scale architecture — **11 levels, 97 chapters, 66 case studies, 19 runnable tools, and 648 Mermaid diagrams.**

No copied content. No recycled interview answers. No link dumps. This is a **graded learning path** where each level builds on the last, every chapter follows a consistent structure, and every case study applies the same 30-section design method.

## 📊 Repository at a Glance

| | |
|:---|:---|
| 📚 **Curriculum chapters** | 97 (Levels 0–10 + AI Systems + Network Operations) |
| 📋 **Case studies** | 66 (beginner → extreme, each with 30 sections + 4 diagrams) |
| 🎨 **Mermaid diagrams** | 272 standalone `.mmd` + 376 inline = **648 total** |
| 🐍 **Python tools** | 19 (all standard-library, all runnable) |
| 📝 **Templates** | 16 (case study, ADR, security/reliability/design checklists) |
| ✅ **CI workflows** | 5 (markdown lint, link check, Mermaid validate, spell check, cross-link) |
| 📖 **Learning levels** | 11 (Level 0 prerequisites → Level 10 extreme scale) |

<!-- BEGIN GENERATED REPOSITORY STATS -->
| Metric | Value |
|--------|-------|
| Total files | 510 |
| Markdown files | 209 |
| Python files | 15 |
| Standalone .mmd files | 272 |
| Inline Mermaid blocks | 376 |
| Case-study directories | 6 |
| Case-study Markdown files | 60 |
| Median case-study word count | 843 |
| Min case-study word count | 725 |
| Max case-study word count | 2397 |
| Complete case studies | 60 |
| Draft case studies | 0 |
<!-- END GENERATED REPOSITORY STATS -->

## 🗺️ The Learning Path

```
Level 0  🟢 Prerequisites        →  Computing, networking, HTTP/TLS, OS, complexity, databases
Level 1  🟢 Foundations          →  Requirements, capacity planning, scaling, redundancy
Level 2  🟢 Core Components       →  DNS, load balancers, CDN, caching, queues, storage
Level 3  🟢 Data & Storage        →  SQL/NoSQL, indexing, replication, sharding, CDC, IDs
Level 4  🟢 Distributed Systems   →  CAP/PACELC, consistency, consensus, clocks, CRDTs
Level 5  🟢 Architecture          →  Microservices, DDD, CQRS, resilience, MapReduce/Lambda
Level 6  🟢 Reliability           →  SLOs, error budgets, DR, chaos, cascading failure
Level 7  🟢 Security              →  AuthN/Z, OAuth/JWT, zero-trust, encryption, STRIDE
Level 8  🟢 Observability         →  Logs/metrics/traces, OpenTelemetry, incident response
Level 9  🟢 Cloud-Native          →  Kubernetes, service mesh, GitOps, CI/CD, autoscaling
Level 10 🟢 Extreme Scale         →  Multi-region, billion-user, GPU scheduling, AI governance
```

### 🤖 AI Systems Track (15 chapters)
```
00-06  →  AI fundamentals, hardware, capacity, vector DBs, chunking, hybrid search, basic RAG
07-08  →  Advanced RAG (GraphRAG, federated, permission-aware), Agentic systems (ReAct, multi-agent)
09-10  →  AI security (injection, RBAC-aware RAG), AI evaluation (gates, rollback, adversarial)
11-12  →  Model serving (batching, KV cache, quantization), Extreme scale (multi-region, multi-LoRA)
13-14  →  LLM gateways (routing, budgets, failover), Semantic caching (safety risks, thresholds)
```

### 🌐 Network & AI Operations (6 case studies + 6 chapters)
```
Intelligent syslog monitoring · Device upgrade management · Configuration drift detection
AI-assisted NOC · Network digital twin · Secure network agent
```

## 📋 Case Studies (66 total)

| Tier | Count | Examples |
|------|------:|---------|
| 🟢 Beginner | 5 | URL shortener, paste service, rate limiter, web crawler, notification platform |
| 🔵 Intermediate | 6 | Distributed cache, chat, social feed, photo sharing, search autocomplete, logging |
| 🟡 Advanced | 23 | Message broker, ride-hailing, e-commerce, payment gateway, multiplayer game, CI platform... |
| 🔴 Extreme | 10 | Banking ledger, stock trading, fraud detection, data lake, vector database, LLM inference... |
| 🤖 AI Systems | 16 | Enterprise RAG, support-agent team, LLM gateway, GraphRAG, code assistant, AI safety gateway... |
| 🌐 Network AI | 6 | Syslog monitoring, upgrade management, drift detection, NOC copilot, digital twin, secure agent |

Each case study has **30 sections**: problem → scope → requirements → estimates → API → data model → architecture → request flow → database → caching → partitioning → replication → consistency → failures → reliability → security → observability → cost → scaling → trade-offs → alternatives → interview points → diagrams → exercises.

## 🛠️ Practical Tools (19 runnable Python scripts)

| Category | Scripts |
|----------|---------|
| **Core simulations** | `consistent_hashing.py`, `rate_limiter.py`, `queue_retry.py`, `failure_injection.py` |
| **Network tools** | `syslog_parser.py`, `alert_dedup.py`, `upgrade_risk.py`, `config_diff.py`, `certificate_expiry_monitor.py`, `end_of_support_tracker.py`, `noc_summary_generator.py`, `compliance_checker.py`, `change_risk_worksheet.py`, `device_health_checklist.py`, `firmware_inventory_scanner.py` |
| **AI tools** | `token_cost.py`, `vram.py`, `chunking_simulator.py`, `model_routing_simulator.py` |

All scripts are standard-library Python — no dependencies, just `python3 <script>.py`.

## 📐 Design Method

Every case study follows the same **6-phase method**:

```
1️⃣ Clarify & Scope    →  restate, separate must-have from nice-to-have, surface read/write ratio
2️⃣ Estimate           →  RPS, storage, bandwidth; state assumptions; name the binding resource
3️⃣ High-level Design  →  draw the data flow; one responsibility per component
4️⃣ Deep Dive          →  data model, partitioning, replication, consistency, failures
5️⃣ Validate           →  SLO, error budget, trade-offs, alternative designs
6️⃣ Wrap-up            →  summarize in 30 seconds; name the next hardening step
```

## 🎓 Who is this for?

| Audience | Start here |
|----------|-----------|
| 🐤 Complete beginner | Level 0 — Prerequisites |
| 💻 Backend developer | Level 1 — Foundations |
| 🏗️ Infrastructure / cloud engineer | Level 2 — Core Components |
| 🔧 DevOps / SRE | Level 6 — Reliability |
| 🔒 Security engineer | Level 7 — Security |
| 📊 Data / ML engineer | AI Systems Track |
| 🌐 Network engineer | Network & AI Operations |
| 🎯 Interview candidate | Interview Framework + Mock Script |
| 🏛️ Architect / Staff engineer | Level 10 — Extreme Scale |

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| 📖 Full curriculum index | [docs/](docs/) |
| 📋 Case studies | [case-studies/](case-studies/) |
| 🧮 Calculation worksheets | [calculations/](calculations/) |
| 📐 Templates | [templates/](templates/) |
| 🐍 Python tools | [examples/](examples/) |
| 🎯 Interview framework | [interview-framework/](interview-framework/) |
| 💪 Exercises | [exercises/](exercises/) |
| 📚 Sources & citations | [SOURCES.md](SOURCES.md) |
| 📖 Glossary | [GLOSSARY.md](GLOSSARY.md) |
| 🗺️ Roadmap | [ROADMAP.md](ROADMAP.md) |
| 📝 Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 🔍 Provenance review | [PROVENANCE.md](PROVENANCE.md) |

## ⚙️ Validation

The repository includes **5 CI workflows** and **7 validation scripts**:

```
✅ markdown-lint     →  Markdown formatting
✅ link-check        →  Internal + external links
✅ mermaid-validate  →  Mermaid diagram syntax
✅ spell-check       →  Spelling (advisory)
✅ cross-link-check  →  Relative link integrity
✅ check_repeated_prose   →  No boilerplate paragraphs
✅ check_case_studies     →  30 sections + minimum content
✅ check_source_ids       →  SOURCES.md IDs valid
```

## 📝 License

| Component | License |
|-----------|---------|
| Code (Python, Mermaid, Actions) | **MIT** |
| Content (prose, diagrams, examples) | **CC BY 4.0** |

See [LICENSE](LICENSE) for full text.

## 👤 Author

**RIT-MESH** — [GitHub](https://github.com/RIT-MESH)

---

<p align="center">
  <b>System Design Mastery</b><br>
  <i>An original, graded curriculum from prerequisites to extreme scale.</i><br>
  ⭐ If this helped you, consider starring the repository!
</p>