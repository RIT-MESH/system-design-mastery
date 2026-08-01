"""Model-routing simulator (educational, std-lib only)."""
MODELS = {"small": {"cost": 0.50, "max": 4096, "caps": ["classify","summarize","extract"]},
          "medium": {"cost": 3.00, "max": 16384, "caps": ["classify","summarize","extract","analyze","code"]},
          "large": {"cost": 15.0, "max": 131072, "caps": ["classify","summarize","extract","analyze","code","reason","vision"]},
          "local": {"cost": 0.10, "max": 8192, "caps": ["classify","summarize","extract","confidential"]}}
def route(task, tokens, conf=False):
    if conf: return "local"
    for n in ["small","medium","large"]:
        if task in MODELS[n]["caps"] and tokens <= MODELS[n]["max"]: return n
    return "large"
def main():
    for task, tok, conf in [("classify",200,False),("analyze",50000,False),("reason",80000,False),("extract",500,True)]:
        m = route(task, tok, conf)
        c = MODELS[m]["cost"] * tok / 1e6
        print(f"{task:10} -> {m:7} ${c:.4f}")
if __name__ == "__main__": main()
