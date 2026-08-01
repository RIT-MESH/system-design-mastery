"""VRAM calculator (educational, std-lib only).

Estimates whether a model + KV cache fits in GPU VRAM and how many concurrent
contexts fit, across precision and context length. Original for system-design-mastery.

Run:  python vram.py
"""
PARAM_BYTES = {"fp32":4,"fp16":2,"bf16":2,"int8":1,"int4":0.5}

def model_bytes(params_b, precision):
    return params_b * 1e9 * PARAM_BYTES[precision]

def kv_bytes(tokens, layers, hidden, kv_precision="fp16"):
    # KV cache ~ 2 * tokens * layers * hidden * bytes_per_elem (approximate)
    return 2 * tokens * layers * hidden * PARAM_BYTES[kv_precision]

def main():
    params_b = 70  # 70B
    layers, hidden = 80, 8192
    vram_gb = 80
    for prec in ["fp16","int8","int4"]:
        m = model_bytes(params_b, prec)
        free = vram_gb*1e9 - m
        ctx = 8192
        per_ctx = kv_bytes(ctx, layers, hidden)
        n = max(0, int(free // per_ctx))
        print(f"{prec:5} model={m/1e9:5.1f}GB  free={free/1e9:5.1f}GB  ctx8k_kv={per_ctx/1e6:5.1f}MB  concurrent_contexts<=~{n}")
    print("\nApproximate; real engines differ (attention impl, batching, overhead).")

if __name__ == "__main__":
    main()
