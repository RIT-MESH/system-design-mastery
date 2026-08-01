# AI Systems Track

> First-class coverage of modern AI system architecture: LLM applications, RAG, agentic
> workflows, model serving, evaluation, security, and cost control. Vendor-neutral; vendor
> products appear only as implementation examples.

This track extends the curriculum so AI infrastructure is treated with the same rigor as
traditional distributed systems. It is staged across the AI milestones below; the chapters
currently present are linked, and the remaining milestones are tracked in [BACKLOG.md](../../BACKLOG.md).

## Chapters present

### AI Milestone 1 — Foundations
- [AI and ML Fundamentals](00-ai-ml-fundamentals.md) — AI/ML/DL/generative, foundation models, LLMs, tokens, embeddings, context windows, inference vs training, sampling, structured output, tool calling, latency metrics
- [AI Hardware](01-ai-hardware.md) — CPU/GPU/TPU, tensor cores, VRAM, PCIe/NVLink, memory- vs compute-bound, quantization (FP16/BF16/INT8/INT4)
- [AI Capacity Planning](02-ai-capacity-planning.md) — token-based vs request-based planning, GPU capacity, KV cache, TTFT/TPOT, cost

### AI Milestone 2 — Retrieval Systems
- [Vector Databases](03-vector-databases.md) — dense/sparse, ANN (HNSW/IVF/PQ), similarity, sharding, re-indexing, multi-tenancy, hybrid
- [Chunking and Ingestion](04-chunking-ingestion.md) — chunking strategies, embeddings, ingestion pipeline, metadata
- [Hybrid Search and Reranking](05-hybrid-search-reranking.md) — hybrid (keyword+vector), reranking, metadata filtering
- [Basic RAG](06-basic-rag.md) — retrieve-then-generate, grounding, citations, evaluation

## AI milestones (roadmap)
- M1 Foundations · M2 Retrieval · M3 Advanced RAG (query transform, GraphRAG, permission-aware, grounding) · M4 Agentic (tools, memory, ReAct, planner-executor, approvals) · M5 Security & Evaluation · M6 Model Serving (batching, KV cache, quantization, multi-GPU, autoscaling) · M7 Extreme Scale (multi-region, billion-chunk, multi-LoRA, GPU scheduling, governance) · M8 Case Studies & Tools.

See [BACKLOG.md](../../BACKLOG.md) for per-chapter status of M3–M8.

## AI chapter standard
Each AI chapter includes learning objectives, overview, mechanics, architecture diagram, capacity/latency/cost, security and privacy risks, evaluation, scaling, trade-offs, a "when NOT to use" note, common mistakes, failure modes, a practical exercise, interview questions, and further reading. AI assists; humans approve high-risk actions (see the [Network-AI security review](../../templates/network/network-ai-security-review.md) and the AI safety-gateway principle).
