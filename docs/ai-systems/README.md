# AI Systems Track

> First-class coverage of modern AI system architecture: LLM applications, RAG, agentic
> workflows, model serving, evaluation, security, and cost control. Vendor-neutral; vendor
> products appear only as implementation examples.

This track extends the curriculum so AI infrastructure is treated with the same rigor as
traditional distributed systems. Fifteen chapters cover AI from fundamentals to extreme scale.

## Chapters

### Foundations
- [AI and ML Fundamentals](00-ai-ml-fundamentals.md) — AI/ML/DL/generative, foundation models, LLMs, tokens, embeddings, context windows, inference vs training, sampling, structured output, tool calling, latency metrics
- [AI Hardware](01-ai-hardware.md) — CPU/GPU/TPU, tensor cores, VRAM, PCIe/NVLink, memory- vs compute-bound, quantization (FP16/BF16/INT8/INT4)
- [AI Capacity Planning](02-ai-capacity-planning.md) — token-based vs request-based planning, GPU capacity, KV cache, TTFT/TPOT, cost

### Retrieval Systems
- [Vector Databases](03-vector-databases.md) — dense/sparse, ANN (HNSW/IVF/PQ), similarity, sharding, re-indexing, multi-tenancy, hybrid
- [Chunking and Ingestion](04-chunking-ingestion.md) — chunking strategies, embeddings, ingestion pipeline, metadata
- [Hybrid Search and Reranking](05-hybrid-search-reranking.md) — hybrid (keyword+vector), reranking, metadata filtering
- [Basic RAG](06-basic-rag.md) — retrieve-then-generate, grounding, citations, evaluation

### Advanced RAG
- [Advanced RAG](07-advanced-rag.md) — query transformation, adaptive retrieval, GraphRAG, federated retrieval, permission-aware retrieval, grounding verification

### Agentic Systems
- [Agentic Systems](08-agentic-systems.md) — tool calling, ReAct, planner-executor, multi-agent, memory, human approvals, policy gateway

### Security and Evaluation
- [AI Security](09-ai-security.md) — prompt injection, data poisoning, RBAC-aware RAG, PII protection, AI safety gateway
- [AI Evaluation](10-ai-evaluation.md) — retrieval/generation/agent/cost/safety metrics, release gates, rollback triggers, adversarial sets

### Model Serving
- [Model Serving](11-model-serving.md) — continuous batching, KV caching, quantization, distributed/multi-GPU inference, autoscaling

### Extreme Scale
- [AI at Extreme Scale](12-ai-extreme-scale.md) — multi-region serving, billion-chunk retrieval, multi-LoRA, GPU scheduling, enterprise AI gateways, AI governance

### Infrastructure
- [LLM Gateways](13-llm-gateway.md) — unified model API, provider abstraction, complexity/cost/latency/capability routing, token-based quotas and budgets, failover, content filtering, audit
- [Semantic Caching](14-semantic-caching.md) — embedding-based cache lookup, similarity thresholds, safety risks (financial, medical, user-specific, time-sensitive, authorization-dependent), namespaces, invalidation

## AI chapter standard
Each AI chapter includes learning objectives, overview, mechanics, architecture diagram, capacity/latency/cost considerations, security and privacy risks, evaluation methodology, scaling, trade-offs, a "when NOT to use" note, common mistakes, failure modes, a practical exercise, interview questions, and further reading.

## Design principle
AI should assist, not bypass operational controls. Use AI for summarization, classification, retrieval, correlation, explanation, recommendation, and report generation. Use deterministic systems and human approval for high-risk, destructive, or irreversible operations. See the [AI safety gateway](09-ai-security.md), the [AI threat model](../../templates/ai/ai-threat-model.md), and the [AI production readiness checklist](../../templates/ai/ai-production-readiness.md).

## Templates and tools
- AI templates: [`templates/ai/`](../../templates/ai/) (rag-adr, ai-threat-model, evaluation-plan, prompt-change-review, ai-production-readiness)
- AI tools: [`examples/ai/`](../../examples/ai/) (token_cost.py, vram.py)
