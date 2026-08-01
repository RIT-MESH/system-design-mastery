"""Alert deduplication / correlation simulator (educational, std-lib only).

Shows dedup (same key within a window) and correlation (same root-cause group).
Demonstrates alert suppression vs correlation. Original for system-design-mastery.

Run:  python alert_dedup.py
"""
import collections, hashlib

EVENTS = [
    ("fw1", "VPN tunnel down", 1),
    ("fw1", "VPN tunnel down", 2),       # duplicate
    ("fw1", "VPN tunnel down", 3),       # duplicate
    ("core-r1", "BGP neighbor 10.2.0.1 DOWN", 4),
    ("core-r2", "BGP neighbor 10.2.0.1 DOWN", 5),  # correlated (same root: peer)
    ("sw3", "Interface eth0 link flapping", 6),
    ("fw1", "VPN tunnel down", 30),      # outside window -> new incident
]

def key(d, msg): return hashlib.sha256(f"{d}|{msg}".encode()).hexdigest()[:8]

def main():
    WINDOW = 10
    open_incidents = collections.OrderedDict()
    out = []
    for dev, msg, t in EVENTS:
        k = key(dev, msg)
        if k in open_incidents and t - open_incidents[k]["first"] <= WINDOW:
            open_incidents[k]["count"] += 1
            out.append(f"t={t:3} SUPPRESS dup on {dev} ({open_incidents[k]['count']}x)")
        else:
            open_incidents[k] = {"first": t, "count": 1}
            out.append(f"t={t:3} NEW incident {k} {dev}: {msg}")
    # simple correlation by shared token (peer IP / service)
    peer = collections.defaultdict(list)
    for dev, msg, t in EVENTS:
        for tok in msg.split():
            if tok not in ("DOWN","up","down"):
                peer[tok].append(dev)
    print("\n".join(out))
    print("\nCorrelation groups (shared token):")
    for tok, devs in peer.items():
        if len(set(devs)) > 1:
            print(f"  '{tok}' -> {sorted(set(devs))}  (likely shared root cause)")
    print("\nSuppression cuts noise; correlation groups same-root events.")

if __name__ == "__main__":
    main()
