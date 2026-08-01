"""Token-cost calculator (educational, std-lib only).

Estimates LLM cost from request volume, token distribution, and per-1M-token
prices. Shows why a long-context tail dominates cost. Original for system-design-mastery.

Run:  python token_cost.py
"""
def cost(reqs, in_tok, out_tok, in_price, out_price):
    # prices are per 1,000,000 tokens
    return reqs * (in_tok * in_price / 1_000_000 + out_tok * out_price / 1_000_000)

def main():
    in_p, out_p = 0.50, 1.50  # per 1M tokens (illustrative)
    short = (900_000, 500, 200)
    long  = (100_000, 100_000, 500)
    total = 0.0
    for label, (r, i, o) in [("short-ctx", short), ("long-ctx", long)]:
        c = cost(r, i, o, in_p, out_p)
        total += c
        print(f"{label:10} reqs={r:>7} in={i:>6} out={o:>4} -> ${c:,.2f}")
    print(f"total/day ${total:,.2f}; 10% of requests (long-context) drive most cost.")
    print("\nPrices are illustrative; replace with your provider rates and your real context-length distribution.")

if __name__ == "__main__":
    main()
