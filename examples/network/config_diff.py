"""Configuration-difference checker (educational, std-lib only).

Diffs two configs line by line and classifies drift lines. Demonstrates the
core of configuration-drift detection. Original for system-design-mastery.

Run:  python config_diff.py
"""
import difflib

BASELINE = [
    "interface eth0",
    "ip address 10.0.0.1/24",
    "no shutdown",
    "router bgp 65001",
    "neighbor 10.2.0.1 remote-as 65002",
]
CURRENT = [
    "interface eth0",
    "ip address 10.0.0.1/24",
    "no shutdown",
    "router bgp 65001",
    "neighbor 10.2.0.1 remote-as 65099",   # changed
    "ntp server 8.8.8.8",                  # added
]

def classify(line):
    if line.startswith("- "): return "removed", "review"
    if line.startswith("+ "):
        t = line[2:]
        return "added", "policy" if "ntp" in t or "password" in t else "minor"
    return None, None

def main():
    diff = list(difflib.ndiff(BASELINE, CURRENT))
    drift = [l for l in diff if l[:2] in ("+ ","- ")]
    for l in drift:
        kind, sev = classify(l)
        print(f"[{kind:7} {sev:8}] {l}")
    print(f"\n{len(drift)} drifted line(s); classify intent (authorized/unauthorized/error) before action.")

if __name__ == "__main__":
    main()
